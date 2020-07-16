import glob
import os
import numpy as np
from .get_sts_selenium_file import get_sts_selenium_file

class get_multiple_sts_selenium_files(object):
    def __init__(self, file_folder_path, time_zone='US/Pacific'):
        os.chdir(file_folder_path)
        self.files = glob.glob('*.txt')
        self.timestamp = []
        self.datetime_timestamp = []
        self.wavelengths = []
        self.raw_counts = []
        self.nonlinear_corrected = []
        self.detector_temp_C = []
        self.uController_temp_C = []
        self.relative_spectra = []
        self.pressure = []
        self.altitude_from_pressure = []

        for file in self.files:
            l = get_sts_selenium_file(file,time_zone)
            if l.timestamp:
                self.timestamp.append(l.timestamp)
            if l.datetime_timestamp:
                self.datetime_timestamp.append(l.datetime_timestamp)
            if l.wavelengths.any():
                self.wavelengths.append(l.wavelengths)
            if l.raw_counts.any():
                self.raw_counts.append(l.raw_counts)
            if l.nonlinear_corrected.any():
                self.nonlinear_corrected.append(l.nonlinear_corrected)
            if l.detector_temp_C:
                self.detector_temp_C.append(l.detector_temp_C)
            if l.uController_temp_C:
                self.uController_temp_C.append(l.uController_temp_C)
            if l.pressure:
                self.pressure.append(l.pressure)
            if l.altitude_from_pressure:
                self.altitude_from_pressure.append(l.altitude_from_pressure)

        self.detector_temp_C = np.array(self.detector_temp_C)
        self.uController_temp_C = np.array(self.uController_temp_C)
        # self._get_max_index() # temp fix
        # self._get_relative_spectra()

    def _get_max_index(self):
        max_counts = []
        for i in range(len(self.files)):
            max_counts.append(np.max(self.raw_counts[i]))

        max_index = np.argmax(max_counts)

        return max_index
    
    def _get_relative_spectra(self):
        relative_spectra = []
        max_spectra = self.raw_counts[self._get_max_index()]
        for i in range(len(self.files)):
            relative_spectra.append(self.raw_counts[i]/max_spectra)
        self.relative_spectra = relative_spectra

