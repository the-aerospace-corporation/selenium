import numpy as np
import scipy as sp
from scipy import integrate
import selenium.selenium_analysis as sa
from selenium.file_imports.get_multiple_sts_selenium_files import get_multiple_sts_selenium_files
from .auraMLSO3Profile import auraMLSO3Profile
import selenium.solar_spectra as pc
import pandas as pd
import selenium.press2alt as press2alt
import pvlib


class analyze_sts_selenium_files(get_multiple_sts_selenium_files):
    def __init__(self, folder_path, ozone_mls_hdf_file=None, external_telemetry=None, qe=None, time_zone = 'US/Pacific'):
        get_multiple_sts_selenium_files.__init__(self, file_folder_path=folder_path, time_zone=time_zone)
        self.dataframe = pd.DataFrame(index=pd.to_datetime(self.datetime_timestamp, utc=True))
        self.dataframe['detector_temp_C'] = self.detector_temp_C

        if ozone_mls_hdf_file is not None:
            self.ozone_file = ozone_mls_hdf_file

        if external_telemetry is not None:
            self.dataframe = sa.combine_external_telem_with_selenium(external_telemetry, self.dataframe)


    def ozone_correct_sts_spectra(self, dataframe, ozone_file):
        ozone = auraMLSO3Profile(ozone_file)

        ozone_DUs = []
        zenith_angles = []
        ozone_corrected_spectra = []
        index = 0
        for i, row in dataframe.iterrows():
            ozone_profile = ozone.get_O3_profile(row['Latitude'], row['Longitude'])
            pressure_hPa = press2alt.altitude_to_pressure(row['Altitude']/1000)/100
            ozone_DU = sa.total_ozone_above_pressure(ozone_profile, pressure_hPa)
            ozone_DUs.append(ozone_DU)
            zenith = pvlib.solarposition.get_solarposition(i, row['Latitude'], row['Longitude'], row['Altitude']).zenith.values
            zenith_angles.append(zenith)
            ozone_transmission = sa.generate_ozone_transmission_spectrum(ozone_DU, zenith)
            ozone_transmission[:,1] = ozone_transmission[:,1]*100
            sts_spectrum = np.vstack((self.wavelengths[index], self.raw_counts[index])).T
            ozone_corrected_spectrum = sa.filterCorrection(sts_spectrum, ozone_transmission)
            ozone_corrected_spectra.append(ozone_corrected_spectrum[:,1])
            index = index +1

        return ozone_corrected_spectra

    def get_correction_factors(self, dataframe, ozone_file, qe):
        ozone_corrected_spectra = self.ozone_correct_sts_spectra(dataframe, ozone_file)
        integrated_ozone = np.zeros((len(ozone_corrected_spectra)))
        for i in range(len(integrated_ozone)):
            integrated_ozone[i] = sp.integrate.trapz(ozone_corrected_spectra[i])

        # index_max_spectrum = np.argmax(integrated_ozone)
        index_max_spectrum = 180
        ref_spectrum = np.vstack((self.wavelengths[index_max_spectrum], ozone_corrected_spectra[index_max_spectrum])).T
        ref_spectrum_cal_to_AM0 = sa.calibrationCorrection(ref_spectrum, ref_spectrum, pc.AM0, units='irradiance vs nm')
        ref_jsc = sa.get_jsc_from_quantum_efficiency(qe, ref_spectrum_cal_to_AM0)

        correction_factors = []
        print(index_max_spectrum)
        for i, spectrum in enumerate(ozone_corrected_spectra):
            spectrum_2d = np.vstack((self.wavelengths[i], spectrum)).T
            spectrum_2d = sa.calibrationCorrection(spectrum_2d, ref_spectrum, pc.AM0, units='irradiance vs nm')
            jsc = sa.get_jsc_from_quantum_efficiency(qe, spectrum_2d)
            cf = ref_jsc/jsc
            correction_factors.append(cf)
        print(ref_jsc, jsc)
        return correction_factors

        correction_factor = sa.get_ozone_correction_factor()
        return norm_ozone_corrected_spectra



