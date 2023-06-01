import numpy
import numpy as np

import selenium
from selenium.file_imports.getLIVmultipleSeleniumFiles import getLIVmultipleSeleniumFiles
from .auraMLSO3Profile import auraMLSO3Profile
from .auraOmiO3Profile import auraOmiO3Profile
from .analyze_sts_selenium_files import analyze_sts_selenium_files
import selenium.selenium_analysis as sa
import selenium.press2alt as press2alt
import pvlib
import matplotlib.dates as mdates
import os
from profilehooks import profile
import pandas as pd


import selenium.solar_spectra as pc
class AnalyzeSeleniumData(object):
    def __init__(self, selenium_data_frame, ozone_mls_hdf_file: str=None, ozone_omi_hdf_file: str=None, external_telemetry=None, qe: np.ndarray=None, lat: float=None, lon: float=None, irradiance_spectrum: np.ndarray=None):
        """
        Takes in a dataframe of a specific format to process selenium data

        Args:
            selenium_data_frame (pd.DataFrame): A dataframe of selenium data
            ozone_mls_hdf_file (str): The path to the ozone mls hdf file
            ozone_omi_hdf_file (str): The path to the ozone omi hdf file
            external_telemetry (pd.DataFrame): A dataframe of external telemetry data
            qe (np.ndarray): A numpy array of quantum efficiency data where columbn 0 is wavelength and column 1 is QE
            lat (float): The latitude of the location of the selenium data if GPS data was not recorder
            lon (float): The longitude of the location of the selenium data if GPS data was not recorder
            irradiance_spectrum (np.ndarray): A numpy array of the irradiance spectrum
        """
        self.dataframe = selenium.standardize_selenium_dataframe(selenium_data_frame)
        self.irradiance_spectrum = irradiance_spectrum
        if external_telemetry is not None:
            self.dataframe = sa.combine_external_telem_with_selenium(external_telemetry, self.dataframe)
        self.x_angles = []
        self.y_angles = []

        if (ozone_mls_hdf_file is not None) & (qe is not None):
            ozone = auraMLSO3Profile(ozone_mls_hdf_file)
            if lat and lon:
                self.generate_ozone_related_data(self.dataframe, ozone, qe, lat, lon, irradiance_spectrum)
            else:
                self.generate_ozone_related_data(self.dataframe, ozone, qe, irradiance_spectrum=irradiance_spectrum)


        if (ozone_mls_hdf_file is not None) and (qe is None):
            ozone = auraMLSO3Profile(ozone_mls_hdf_file)
            if lat and lon:
                self.generate_ozone_related_data(self.dataframe, ozone, qe, lat, lon, irradiance_spectrum)
            else:
                self.generate_ozone_related_data(self.dataframe, ozone, qe, irradiance_spectrum=irradiance_spectrum)

        if any(terms in self.dataframe.columns for terms in ['YAW', 'PITCH']):
            self.x_angles = self.dataframe['YAW']
            self.y_angles = self.dataframe['PITCH']
        elif any(terms in self.dataframe.columns for terms in ['x angle post', 'y angle post']):
            self.x_angles = self.dataframe['x angle post']
            self.y_angles = self.dataframe['y angle post']

        self.dataframe['Earth-Sun Distance (AU)'] = pvlib.solarposition.nrel_earthsun_distance(self.dataframe.index)

        if 'Jsc (A/cm2)' in self.dataframe.columns:
            self.dataframe['Jsc (A/cm2) Earth Sun Corrected'] = sa.correct_current_for_sun_earth_distance(self.dataframe['Jsc (A/cm2)'].values, self.dataframe.index)
            self.dataframe['Jsc (A/cm2) Earth Sun Angle Corrected'] = sa.current_angle_correction(self.dataframe['Jsc (A/cm2) Earth Sun Corrected'].values, self.x_angles, self.y_angles)
            self.ozone_correct_data('Jsc (A/cm2) Earth Sun Angle Corrected')

        if 'Isc (A)' in self.dataframe.columns:
            self.dataframe['Isc (A) Earth Sun Corrected'] = sa.correct_current_for_sun_earth_distance(self.dataframe['Isc (A)'].values, self.dataframe.index)
            self.dataframe['Isc (A) Earth Sun Angle Corrected'] = sa.current_angle_correction(self.dataframe['Isc (A) Earth Sun Corrected'].values, self.x_angles, self.y_angles)
            self.ozone_correct_data('Isc (A) Earth Sun Angle Corrected')

        if 'Imax (A)' in self.dataframe.columns:
            self.dataframe['Imax (A) Earth Sun Corrected'] = sa.correct_current_for_sun_earth_distance(self.dataframe['Imax (A)'].values, self.dataframe.index)
            self.dataframe['Imax (A) Earth Sun Angle Corrected'] = sa.current_angle_correction(self.dataframe['Imax (A) Earth Sun Corrected'].values, self.x_angles, self.y_angles)
            self.ozone_correct_data('Imax (A) Earth Sun Angle Corrected')

        if ozone_mls_hdf_file is not None:
            self.ozone_file = ozone_mls_hdf_file



        # self._pre_angle_filtered_indices = self.filtered_indices(self.x_angle_pre, self.y_angle_pre, x_angle_limit=x_angle_filter, y_angle_limit=y_angle_filter)  # self._post_angle_filtered_indices = self.filtered_indices(self.x_angle_post, self.y_angle_post, x_angle_limit=x_angle_filter, y_angle_limit=y_angle_filter)

    def temperature_correct_jsc(self, param, target_temp, temp_co):
        # Depreciated
        jsc_temperature_corrected = sa.correct_for_temperature(param, self.dataframe['Temperature (C)'], target_temp,
                                                               temp_co)
        return jsc_temperature_corrected

    # def jsc_full_correction(self, target_temp, temp_co):
    def ozone_correct_data(self, dataframe_column_name: str):
        """
        Corrects the data in the dataframe for ozone. Can be used for example with Isc (A), or Imax (A) etc.

        Args:
            dataframe_column_name (str): The name of the column in the dataframe to correct for ozone

        Returns:
            pd.DataFrame: The dataframe with the ozone corrected data

        """
        if "Corrected" in dataframe_column_name.split(' '):
            new_column_name = dataframe_column_name.replace("Corrected", "O3 Corrected")
        else:
            new_column_name = dataframe_column_name

        if 'O3 Correction Factor' in self.dataframe.columns:
            self.dataframe[new_column_name] = self.dataframe[dataframe_column_name].values * self.dataframe['O3 Correction Factor'].values

    def generate_ozone_related_data(self, dataframe, ozone: auraMLSO3Profile, qe: np.ndarray, lat: float=None, lon: float=None, irradiance_spectrum: np.ndarray=None):
        """
        Generates the ozone related data such as 'O3 Correction Factor', 'O3 DU', 'Zenith', and 'Pressure (hPa)' and adds it to the dataframe.

        Args:
            dataframe (pd.DataFrame): The dataframe to generate the ozone related data for.  In the init function this is the self.dataframe or the input dataframe
            ozone (auraMLSO3Profile | auraOmiO3Profile): The ozone profile to use for the correction
            qe (np.ndarray): The quantum efficiency of the device where column 0 is wavelength in nm and column 1 is the quantum efficiency
            lat (float): The latitude of the device if no gps coordinates are available
            lon (float): The longitude of the device if no gps coordinates are available
            irradiance_spectrum (np.ndarray): The spectrum of the irradiance where column 0 is wavelength in nm and column 1 is the irradiance

        Returns:
            pd.DataFrame: The dataframe with  ozone related data 'O3 Correction Factor', 'O3 DU', 'Zenith', and 'Pressure (hPa)' added to the dataframe
        """
        ozone_DUs = []
        ozone_correction_factors = []
        if 'Altitude (m)' not in dataframe.columns:
            altitude = dataframe["Altitude_from_Pressure (m)"]
        else:
            altitude = dataframe['Altitude (m)']
        if lat and lon:
            dataframe['Latitude'] = lat
            dataframe['Longitude'] = lon
            altitude = dataframe["Altitude_from_Pressure (m)"]
            dataframe['Zenith'] = pvlib.solarposition.get_solarposition(dataframe.index, lat, lon,
                                                                        altitude).zenith.values

        else:
            dataframe['Zenith'] = pvlib.solarposition.get_solarposition(dataframe.index, dataframe['Latitude'],
                                                                        dataframe['Longitude'],
                                                                        altitude).zenith.values

        
        if ('MS56 Pressure(Pa)' in dataframe.columns):
            pressure_Pa = dataframe['MS56 Pressure(Pa)']
        
        elif('Pressure' in dataframe.columns):
            pressure_Pa = dataframe['Pressure']
            
        dataframe['Pressure (hPa)'] = pressure_Pa / 100
        lat_l = None
        lon_l = None
        i = 0
        for index, row in dataframe.iterrows(): # be careful with this don
            if lat and lon:
                if (lat_l != lat) and (lon_l != lon):
                    lat_l = lat
                    lon_l = lon
                    ozone_profile = ozone.get_O3_profile(lat, lon)

            else:
                if i == 0:
                    lat_row = row['Latitude']
                    lon_row = row['Longitude']
                    ozone_profile = ozone.get_O3_profile(lat_row, lon_row)

                elif (lat_l != lat_row) and (lon_l != lon_row):
                    lat_row = row['Latitude']
                    lon_row = row['Longitude']
                    lat_l = lat_row
                    lon_l = lon_row
                    ozone_profile = ozone.get_O3_profile(lat_row, lon_row)

            # if ~np.array_equal(ozone_l, ozone_profile):
            ozone_DU = sa.total_ozone_above_pressure(ozone_profile, row['Pressure (hPa)'])
            ozone_l = ozone_profile
            ozone_DUs.append(ozone_DU)
            ozone_AM0 = sa.ozone_attenuated_irradiance(ozone_DU, row['Zenith'], irradiance_spectrum)
            if qe is not None:
                interpolation_method='QE'
                # ozone_correction_factor = sa.get_ozone_correction_factor(ozone_AM0, ref_spectrum=irradiance_spectrum, qe=QE, interpolation_method='Irr')
                if i == 0:
                    ref_jsc = sa.get_jsc_from_quantum_efficiency(qe, pc.AM0_2019, interpolation_method)
                ozone_ref_jsc = sa.get_jsc_from_quantum_efficiency(qe, ozone_AM0, interpolation_method)
                ozone_correction_factor = (ref_jsc / ozone_ref_jsc)
                ozone_correction_factors.append(ozone_correction_factor)
            i+=1

        dataframe['O3 DU'] = ozone_DUs
        if qe is not None:
            dataframe['O3 Correction Factor'] = ozone_correction_factors
        self.dataframe = dataframe
        return dataframe


    def generate_dataframe_with_ozone_corrections_basic(self, dataframe, ozone, lat, lon, QE):
        # Depreciated
        ozone_DUs = []
        ozone_correction_factors = []
        dataframe['Zenith'] = pvlib.solarposition.get_solarposition(dataframe.index, lat, lon,
                                                                    dataframe['Altitude (m)']).zenith.values
        # dataframe['Pressure (hPa)'] = press2alt.altitude_to_pressure(dataframe['Altitude (m)']/1000)/100 # take out loop
        dataframe['Pressure (hPa)'] = dataframe['Pressure'] / 100

        for i, row in dataframe.iterrows():
            ozone_profile = ozone.get_O3_profile(lat, lon)
            ozone_DU = sa.total_ozone_above_pressure(ozone_profile, row['Pressure (hPa)'])
            ozone_DUs.append(ozone_DU)
            ozone_AM0 = sa.ozone_attenuated_irradiance(ozone_DU, row['Zenith'])
            ozone_correction_factor = sa.get_ozone_correction_factor(ozone_AM0, qe=QE, interpolation_method='Irr')
            ozone_correction_factors.append(ozone_correction_factor)

        ozone_corrected_current = dataframe['Jsc (A/cm2) Earth Sun Angle Corrected'].values * ( np.array(ozone_correction_factors))
        ozone_corrected_current_imax = dataframe['Imax (A) Earth Sun Angle Corrected'].values * (np.array(ozone_correction_factors))
        ozone_corrected_current_isc = dataframe['Isc (A) Earth Sun Angle Corrected'].values * (np.array(ozone_correction_factors))
        # print(ozone_corrected_current)
        # print(dataframe['Jsc Sun Earth Angle Corrected'].values)
        # dataframe['AM'] = 1/np.cos(np.deg2rad(dataframe['Zenith']))
        dataframe['O3 DU'] = ozone_DUs
        dataframe['O3 Correction Factor'] = ozone_correction_factors
        dataframe['Jsc_O3_corrected'] = ozone_corrected_current
        dataframe['Imax_O3_corrected'] = ozone_corrected_current_imax
        dataframe['Isc_O3_corrected'] = ozone_corrected_current_isc
        self.dataframe = dataframe
        return dataframe


    def generate_dataframe_with_ozone_corrections(self, dataframe, ozone, QE):
        # Depreciated
        # ozone = auraMLSO3Profile(ozone_file)

        ozone_DUs = []
        ozone_correction_factors = []
        # zenith_angles = []
        dataframe['Zenith'] = pvlib.solarposition.get_solarposition(dataframe.index, dataframe['Latitude'],
                                                                    dataframe['Longitude'],
                                                                    dataframe['Altitude (m)']).zenith.values
        # dataframe['Pressure (hPa)'] = press2alt.altitude_to_pressure(dataframe['Altitude (m)']/1000)/100 # take out loop # may need to put this back in with some logic for older data with older pressure sensor
        dataframe['Pressure (hPa)'] = dataframe['Pressure'] / 100
        for i, row in dataframe.iterrows():
            ozone_profile = ozone.get_O3_profile(row['Latitude'], row['Longitude'])
            ozone_DU = sa.total_ozone_above_pressure(ozone_profile, row['Pressure (hPa)'])
            ozone_DUs.append(ozone_DU)
            ozone_AM0 = sa.ozone_attenuated_irradiance(ozone_DU, row['Zenith'])
            ozone_correction_factor = sa.get_ozone_correction_factor(ozone_AM0, qe=QE)
            ozone_correction_factors.append(ozone_correction_factor)

        ozone_corrected_current = dataframe['Jsc (A/cm2) Earth Sun Angle Corrected'].values * np.array(ozone_correction_factors)
        ozone_corrected_current_imax = dataframe['Imax (A) Earth Sun Angle Corrected'].values * np.array(ozone_correction_factors)
        ozone_corrected_current_isc = dataframe['Isc (A) Earth Sun Angle Corrected'].values * np.array(ozone_correction_factors)

        # print(ozone_corrected_current)
        # print(dataframe['Jsc Sun Earth Angle Corrected'].values)
        # dataframe['Zenith'] = zenith_angles
        dataframe['O3 DU'] = ozone_DUs
        dataframe['O3 Correction Factor'] = ozone_correction_factors
        dataframe['Jsc_O3_corrected'] = ozone_corrected_current
        dataframe['Imax_O3_corrected'] = ozone_corrected_current_imax
        dataframe['Isc_O3_corrected'] = ozone_corrected_current_isc
        self.dataframe = dataframe
        return dataframe

    def generate_dataframe_with_sts_data(self, dataframe, sts_files, ozone_file, qe):
        sts = analyze_sts_selenium_files(sts_files)
        correction_factors = sts.get_correction_factors(dataframe, ozone_file, qe)
        ozone_corrected_current = dataframe['Jsc Sun Earth Angle Corrected'].values * np.array(correction_factors)
        dataframe['STS Correction Factor'] = correction_factors
        dataframe['Jsc_O3_corrected_sts'] = ozone_corrected_current
        self.dataframe = dataframe
        return dataframe

    def plot_param(self, param, style='o'):
        ax = self.dataframe.plot(y=param, style=style)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax.minorticks_on()

    def filtered_indices(self, x_angles, y_angles, x_angle_limit, y_angle_limit):
        indices = []
        for i in range(len(x_angles)):
            if (np.abs(x_angles[i]) < x_angle_limit) & (np.abs(y_angles[i]) < y_angle_limit):
                indices.append(i)
        return np.array(indices)

    def filter_dataframe_for_angles(self, x_angle_limit=2.5, y_angle_limit=2.5):
        if 'YAW' in self.dataframe.columns:
            self.dataframe = self.dataframe[np.abs(self.dataframe['YAW']) < x_angle_limit]
            self.dataframe = self.dataframe[np.abs(self.dataframe['PITCH']) < y_angle_limit]
        else:
            self.dataframe = self.dataframe[np.abs(self.dataframe['x angle post']) < x_angle_limit]
            self.dataframe = self.dataframe[np.abs(self.dataframe['y angle post']) < y_angle_limit]

    def filter_dataframe_for_altitude(self, min_altitude_m=24000, max_altitude_m=34000, altitude_column='Altitude_from_Pressure (m)'):
        """
        Filter the dataframe for a specific altitude range. You can use 'Altitude (m)' or 'Altitude_from_Pressure (m)' if you don't have gps altitude

        Args:
            min_altitude_m (float): minimum altitude in meters where 24000 is default because it is well above the tropopauseand from experience you have little atmospheic interference above this altitude
            max_altitude_m (float): maximum altitude of the flight or where ever the balloon popped
            altitude_column (str): 'Altitude (m)' or 'Altitude_from_Pressure (m)' if you don't have gps altitude

        Returns:
            dataframe (pd.DataFrame): dataframe filtered for altitude
        """
        dataframe = self.dataframe[(self.dataframe[altitude_column] > min_altitude_m) & (self.dataframe[altitude_column] < max_altitude_m)]
        return dataframe

    def filter_dataframe_for_presssure(self, max_pressure_hPa=100):
        """
        Filter the dataframe for a specific pressure range.

        Args:
            max_pressure_hPa (float): maximum pressure in hPa

        Returns:
            dataframe (pd.DataFrame): dataframe filtered for altitude
        """
        dataframe = self.dataframe[(self.dataframe['Pressure (hPa)'] < max_pressure_hPa)]
        return dataframe

