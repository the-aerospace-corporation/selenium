import numpy
import numpy as np
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

import selenium.solar_spectra as pc
class AnalyzeSeleniumData(object):
    def __init__(self, selenium_data_frame, ozone_mls_hdf_file=None, ozone_omi_hdf_file=None, external_telemetry=None, qe=None, lat=None, lon=None, irradiance_spectrum=None):
        """

        Args:
            selenium_data_frame ():
            ozone_mls_hdf_file ():
            ozone_omi_hdf_file ():
            external_telemetry ():
            qe ():
            lat ():
            lon ():
            irradiance_spectrum ():
        """
        self.dataframe = selenium_data_frame
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

        if (ozone_omi_hdf_file is not None) & (qe is not None):
            ozone = auraOmiO3Profile(ozone_omi_hdf_file)
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
        jsc_temperature_corrected = sa.correct_for_temperature(param, self.dataframe['Temperature (C)'], target_temp,
                                                               temp_co)
        return jsc_temperature_corrected

    # def jsc_full_correction(self, target_temp, temp_co):
    def ozone_correct_data(self, dataframe_column_name):
        if "Corrected" in dataframe_column_name.split(' '):
            new_column_name = dataframe_column_name.replace("Corrected", "O3 Corrected")
        else:
            new_column_name = dataframe_column_name

        if 'O3 Correction Factor' in self.dataframe.columns:
            self.dataframe[new_column_name] = self.dataframe[dataframe_column_name].values * self.dataframe['O3 Correction Factor'].values

    def generate_ozone_related_data(self, dataframe, ozone, QE, lat=None, lon=None, irradiance_spectrum=None):
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
        dataframe['Pressure (hPa)'] = dataframe['Pressure'] / 100
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
            if QE is not None:
                interpolation_method='QE'
                # ozone_correction_factor = sa.get_ozone_correction_factor(ozone_AM0, ref_spectrum=irradiance_spectrum, qe=QE, interpolation_method='Irr')
                if i == 0:
                    ref_jsc = sa.get_jsc_from_quantum_efficiency(QE, pc.AM0_2019 , interpolation_method)
                ozone_ref_jsc = sa.get_jsc_from_quantum_efficiency(QE, ozone_AM0, interpolation_method)
                ozone_correction_factor = (ref_jsc / ozone_ref_jsc)
                ozone_correction_factors.append(ozone_correction_factor)
            i+=1

        dataframe['O3 DU'] = ozone_DUs
        if QE is not None:
            dataframe['O3 Correction Factor'] = ozone_correction_factors
        self.dataframe = dataframe
        return dataframe


    def generate_dataframe_with_ozone_corrections_basic(self, dataframe, ozone, lat, lon, QE):

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