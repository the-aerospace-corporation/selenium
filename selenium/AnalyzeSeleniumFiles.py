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

class AnalyzeSeleniumFiles(getLIVmultipleSeleniumFiles):
    def __init__(self, folderpath,  ozone_mls_hdf_file=None, ozone_omi_hdf_file=None, external_telemetry=None, qe=None, start_time=None, time_zone = 'US/Pacific', basic_ozone=False, lat=None, lon=None):
        getLIVmultipleSeleniumFiles.__init__(self, folderpath, time_zone, start_time)

        self.folderpath = folderpath
        self.dataframe['Jsc Sun Earth Corrected'] = sa.correct_current_for_sun_earth_distance(self.dataframe.Jsc, self.dataframe.index)
        self.dataframe['Jsc Sun Earth Angle Corrected'] = sa.current_angle_correction(self.dataframe['Jsc Sun Earth Corrected'], self.dataframe['x angle post'], self.dataframe['y angle post'])
        self.dataframe['Imax Sun Earth Corrected'] = sa.correct_current_for_sun_earth_distance(self.dataframe.Imax, self.dataframe.index)
        self.dataframe['Imax Sun Earth Angle Corrected'] = sa.current_angle_correction(self.dataframe['Imax Sun Earth Corrected'], self.dataframe['x angle post'], self.dataframe['y angle post'])

        if ozone_mls_hdf_file is not None:
            self.ozone_file = ozone_mls_hdf_file

        if external_telemetry is not None:
            self.dataframe = sa.combine_external_telem_with_selenium(external_telemetry, self.dataframe)

        if (ozone_mls_hdf_file is not None) & (qe is not None):
            ozone = auraMLSO3Profile(ozone_mls_hdf_file)
            if basic_ozone==True:
                self.generate_dataframe_with_ozone_corrections_basic(self.dataframe, ozone, lat, lon, qe)
            else:
                self.generate_dataframe_with_ozone_corrections(self.dataframe, ozone, qe)

        if (ozone_omi_hdf_file is not None) & (qe is not None):
            ozone = auraOmiO3Profile(ozone_omi_hdf_file)
            self.generate_dataframe_with_ozone_corrections(self.dataframe, ozone, qe)


        # self._pre_angle_filtered_indices = self.filtered_indices(self.x_angle_pre, self.y_angle_pre, x_angle_limit=x_angle_filter, y_angle_limit=y_angle_filter)
        # self._post_angle_filtered_indices = self.filtered_indices(self.x_angle_post, self.y_angle_post, x_angle_limit=x_angle_filter, y_angle_limit=y_angle_filter)


    def temperature_correct_jsc(self, param, target_temp, temp_co):
        jsc_temperature_corrected = sa.correct_for_temperature(param, self.dataframe['Temperature (C)'], target_temp, temp_co)
        return jsc_temperature_corrected

    # def jsc_full_correction(self, target_temp, temp_co):

    def generate_dataframe_with_ozone_corrections_basic(self, dataframe, ozone, lat, lon, QE):

        ozone_DUs = []
        ozone_correction_factors = []
        zenith_angles = []
        for i, row in dataframe.iterrows():
            ozone_profile = ozone.get_O3_profile(lat, lon)
            pressure_hPa = row['Pressure']/100
            ozone_DU = sa.total_ozone_above_pressure(ozone_profile, pressure_hPa)
            ozone_DUs.append(ozone_DU)
            zenith = pvlib.solarposition.get_solarposition(i, lat, lon, altitude=row['Altitude_Pressure'], pressure=row['Pressure']).zenith.values[0]
            zenith_angles.append(zenith)
            ozone_AM0 = sa.ozone_attenuated_irradiance(ozone_DU, zenith)
            ozone_correction_factor = sa.get_ozone_correction_factor(ozone_AM0, qe=QE)
            ozone_correction_factors.append(ozone_correction_factor)

        ozone_corrected_current = dataframe['Jsc Sun Earth Angle Corrected'].values*(np.array(ozone_correction_factors))
        ozone_corrected_current_imax = dataframe['Imax Sun Earth Angle Corrected'].values * (np.array(ozone_correction_factors))
        # print(ozone_corrected_current)
        # print(dataframe['Jsc Sun Earth Angle Corrected'].values)
        dataframe['Zenith'] = zenith_angles
        dataframe['O3 DU'] = ozone_DUs
        dataframe['O3 Correction Factor'] = ozone_correction_factors
        dataframe['Jsc_O3_corrected'] = ozone_corrected_current
        dataframe['Imax_O3_corrected'] = ozone_corrected_current_imax
        self.dataframe = dataframe
        return dataframe

    def generate_dataframe_with_ozone_corrections(self, dataframe, ozone, QE):
        # ozone = auraMLSO3Profile(ozone_file)

        ozone_DUs = []
        ozone_correction_factors = []
        zenith_angles = []
        for i, row in dataframe.iterrows():
            ozone_profile = ozone.get_O3_profile(row['Latitude'], row['Longitude'])
            pressure_hPa = press2alt.altitude_to_pressure(row['Altitude (m)']/1000)/100
            ozone_DU = sa.total_ozone_above_pressure(ozone_profile, pressure_hPa)
            ozone_DUs.append(ozone_DU)
            zenith = pvlib.solarposition.get_solarposition(i, row['Latitude'], row['Longitude'], row['Altitude (m)']).zenith.values
            zenith_angles.append(zenith)
            ozone_AM0 = sa.ozone_attenuated_irradiance(ozone_DU, zenith)
            ozone_correction_factor = sa.get_ozone_correction_factor(ozone_AM0, qe=QE)
            ozone_correction_factors.append(ozone_correction_factor)

        ozone_corrected_current = dataframe['Jsc Sun Earth Angle Corrected'].values*np.array(ozone_correction_factors)
        ozone_corrected_current_imax = dataframe['Imax Sun Earth Angle Corrected'].values * (np.array(ozone_correction_factors))

        # print(ozone_corrected_current)
        # print(dataframe['Jsc Sun Earth Angle Corrected'].values)
        dataframe['Zenith'] = zenith_angles
        dataframe['O3 DU'] = ozone_DUs
        dataframe['O3 Correction Factor'] = ozone_correction_factors
        dataframe['Jsc_O3_corrected'] = ozone_corrected_current
        dataframe['Imax_O3_corrected'] = ozone_corrected_current_imax
        self.dataframe = dataframe
        return dataframe

    def generate_dataframe_with_sts_data(self, dataframe, sts_files, ozone_file, qe):
        sts = analyze_sts_selenium_files(sts_files)
        correction_factors = sts.get_correction_factors(dataframe, ozone_file, qe)
        ozone_corrected_current = dataframe['Jsc Sun Earth Angle Corrected'].values*np.array(correction_factors)
        dataframe['STS Correction Factor'] = correction_factors
        dataframe['Jsc_O3_corrected_sts'] = ozone_corrected_current
        self.dataframe = dataframe
        return dataframe

    def plot_param(self, param, style='o'):
        ax = self.dataframe.plot(y=param, style=style)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax.minorticks_on()


    def filtered_indices(self, x_angles, y_angles,x_angle_limit, y_angle_limit):
        indices = []
        for i in range(len(x_angles)):
            if (np.abs(x_angles[i]) < x_angle_limit) & (np.abs(y_angles[i]) < y_angle_limit):
                indices.append(i)
        return np.array(indices)
    
    def temp_vs_current_filtered(self):
        temp = [self.Cell_Temperature_Celsius[i] for i in self._post_angle_filtered_indices]
        jsc = [self.Jsc[i] for i in self._post_angle_filtered_indices]
        temp_vs_jsc = np.vstack((temp,jsc)).T
        return temp_vs_jsc

    def filter_dataframe_for_angles(self, x_angle_limit=2.5, y_angle_limit=2.5):
        self.dataframe = self.dataframe[np.abs(self.dataframe['x angle post'].values)<x_angle_limit]
        self.dataframe = self.dataframe[np.abs(self.dataframe['y angle post'].values)<y_angle_limit]