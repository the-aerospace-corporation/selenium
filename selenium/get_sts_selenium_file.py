import os
import numpy as np
from datetime import datetime
import pytz
import pearl.selenium.press2alt as p2a

class get_sts_selenium_file(object):
    def __init__(self, filepath, time_zone='US/Pacific'):
        self.filename = os.path.basename(filepath)
        self.timestamp = []
        self.datetime_timestamp =[]
        self.wavelengths = []
        self.raw_counts = []
        self.nonlinear_corrected = []
        self.detector_temp_C = []
        self.uController_temp_C = []
        self.pressure = []
        self.altitude_from_pressure = []
        with open(filepath, 'rU') as f:
            xy = []
            for j in f:
                m = j.split('\t')
                if ('Timestamp:' in m):
                    self.timestamp = (float(m[0+1]))
                    local_datetime_object = datetime.fromtimestamp(self.timestamp)
                    local_time = pytz.timezone(time_zone).localize(local_datetime_object)
                    self.datetime_timestamp = local_time

                elif ('Detector Temp (C):' in m):
                    self.detector_temp_C = (float(m[0+1]))

                elif ('uController Temp (C):' in m):
                    self.uController_temp_C = (float(m[0+1]))

                elif ('MS5607' in m):
                    self.pressure = float(m[1])
                    self.altitude_from_pressure = p2a.pressure_to_altitude(self.pressure)

                elif ('Wavelengths' in m) or ('Pixel' in m):
                    break

            for j in f:
                m = j.split('\t')
                # print(m)
                self.wavelengths.append(float(m[0]))
                # print(float(m[1]))
                self.raw_counts.append(float(m[1]))
                # self.raw_counts.append(float(int(filter(str.isdigit, m[1]))))
                # self.nonlinear_corrected.append(float(m[2]))


        self.wavelengths = np.array(self.wavelengths)
        self.raw_counts = np.array(self.raw_counts)
        self.nonlinear_corrected = np.array(self.nonlinear_corrected)
                

