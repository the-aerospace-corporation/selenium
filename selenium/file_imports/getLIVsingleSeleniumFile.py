import numpy as np
import matplotlib.pyplot as plt
import os
import pytz
import datetime as dt
import re
from datetime import datetime
import dateutil
import selenium.press2alt as p2a
from .LivSeDataContainer import LivSeDataContainer


class getLIVsingleSeleniumFile(LivSeDataContainer):
    def __init__(self,liv_txt,  time_zone = 'utc', start_time=None):
        """
        Opens and parses and single LIV file from AMU.  All parameters are pulled from the measurement and
        placed in the heard of the file, which are then broken into object attributes

        Args:
            liv_txt:
        """
        LivSeDataContainer.__init__(self)
        attributes = list(self.__dict__.keys())
        self.file_name = os.path.basename(liv_txt)

        with open(liv_txt,'rU') as f:
            xy = []
            for j in f:
                m = j.split('\t')
                if ('Manufacturer' in m):
                    self.manufacturer = m[0+1].rstrip()

                elif ('Model' in m):
                    self.model = m[0+1].rstrip()

                elif ('Junction' in m):
                    self.junction = float(m[0+1])

                elif ('Notes' in m):
                    self.notes = m[1].rstrip()

                elif ('AMU' in m):
                    self.amu = m[1].rstrip()

                elif ('Firmware' in m):
                    self.firmware_version = m[1].rstrip()

                elif ('Address' in m):
                    self.address = int(m[0+1], 16)

                elif ('Coverglass' in m):
                    self.coverglass = m[1].rstrip()

                elif ('Energy' in m):
                    self.energy = (float(m[0 + 1]))

                elif ('Dose' in m):
                    self.Fluence = (float(m[0 + 1]))

                elif ('Telemetry' in m):
                    m = j.rstrip().split('\t')
                    self.telemetry = [float(n) for n in m[1:]]

                elif ('Serial Number' in m):
                    self.cell_id = m[0+1].rstrip()

                elif ('Voc (V)' in m) or ('Voc(V)' in m):
                    self.voc = (float(m[0 + 1]))

                elif ('Jsc (A/cm^2)' in m) or ('Jsc(A/cm^2)' in m):
                    self.jsc = (float(m[0 + 1]))

                elif ('Vmax (V)' in m) or ('Vmax(V)' in m):
                    self.vmax = (float(m[0 + 1]))

                elif ('Isc (A)' in m) or ('Isc(A)' in m):
                    self.isc = (float(m[0 + 1]))

                elif ('Imax (A)' in m) or ('Imax(A)' in m):
                    self.imax = (float(m[0 + 1]))

                elif ('Pmax (W)' in m) or ('Pmax(W)' in m):
                    self.pmax = (float(m[0 + 1]))

                elif ('FF' in m):
                    self.fill_factor = (float(m[0 + 1]))

                elif ('Eff (%)' in m) or ('Eff(%)' in m) or ('Eff ()' in m):
                    self.efficiency = (float(m[0 + 1]))

                elif ('Cell Temp (C)' in m) or ('cell temp(C)' in m):
                    self.cell_temperature_celsius = (float(m[0 + 1]))
                    self.cell_temperature_kelvin = self.cell_temperature_celsius + 273.15

                elif ('Cell Temp (K)' in m) or ('cell temp(K)' in m):
                    self.cell_temperature_kelvin = (float(m[0 + 1]))
                    self.cell_temperature_celsius = self.cell_temperature_kelvin - 273.15

                elif ('Cell Area (cm^2)' in m) or ('cell area(cm^2)' in m):
                    self.cell_area_cm_2 = (float(m[0 + 1]))

                elif ('AM0 constant (W/cm^2)' in m):
                    self.am0_constant_w_cm = (float(m[0 + 1]))
                
                elif ('Notes' in re.findall(r'(Notes)', j)):
                    # self.notes = re.findall(r'\b(?!Notes)(?! )\b.*(?=\t)', j)[0]
                    self.notes = re.findall(r'\b(?!Notes)\b(?! |	).*(?=)', j)[0]

                    
                elif ('Sun Angles (x,y)' in m):
                    self.x_angle = (float(m[0+1]))
                    self.y_angle = (float(m[0+2]))

                elif ('Timestamp:' in m) or ('Timestamp' in m):
                    self.timestamp = (float(m[0+1]))
                    local_datetime_object = datetime.fromtimestamp(self.timestamp)
                    local_time = pytz.timezone(time_zone).localize(local_datetime_object)
                    self.gps_datetime_object_timestamp = local_time.astimezone(pytz.utc)

                elif ('UTC' in m):
                    self.utc = (float(m[0+1]))

                elif('GPS' in m):
                    self.gps_date_time = m[1] + ' ' + m[2]
                    if (m[1].split('/')[0] == '00') or (m[1].split('/')[2] == '80') or (m[1].split('/')[2] == '0000') or (m[1].split('/')[2] == '****'):
                        if start_time != None:
                            start_time_utc_seconds = datetime.timestamp(dateutil.parser.parse(start_time))
                        else:
                            start_time_utc_seconds = 0
                        if self.utc:
                            local_datetime_object = datetime.fromtimestamp(self.utc+start_time_utc_seconds)
                        else:
                            local_datetime_object = datetime.fromtimestamp(self.timestamp)

                        local_time = pytz.timezone(time_zone).localize(local_datetime_object)
                        self.gps_datetime_object = local_time.astimezone(pytz.utc)
                        if self.gps_datetime_object.date() == dt.datetime(2019, 10, 7, tzinfo=pytz.timezone(time_zone)).date(): # fixing gps error in jpl 2019 flight file #8
                            if m[1].split('/')[2] == '0000':
                                self.gps_datetime_object = self.gps_datetime_object + dt.timedelta(hours=7)
                        # print(self.timestamp)
                        # print(local_datetime_object)
                        # print(local_time)
                    
                    elif re.match(r'(0019)', m[1].split('/')[2]):
                        n = m[1].split('/')
                        add_20_to_year = re.sub(r'(00)', '20', n[2])
                        n[2] = add_20_to_year
                        m[1] = '/'.join(n)
                        self.gps_date_time = m[1] + ' ' + m[2]

                        try:
                            self.gps_datetime_object = datetime.strptime(self.gps_date_time, '%m/%d/%Y %H:%M:%S.%f')
                            self.gps_datetime_object = self.gps_datetime_object.replace(tzinfo=pytz.timezone(time_zone))
                        except ValueError:
                            pass
                        try:
                            self.gps_datetime_object = datetime.strptime(self.gps_date_time, '%m/%d/%y %H:%M:%S')
                            self.gps_datetime_object = self.gps_datetime_object.replace(tzinfo=pytz.timezone(time_zone))
                        except ValueError:
                            pass
                        try:
                            self.gps_datetime_object = datetime.strptime(self.gps_date_time, '%m/%d/%Y %H:%M:%S')
                            self.gps_datetime_object = self.gps_datetime_object.replace(tzinfo=pytz.timezone(time_zone))
                        except:
                            print('Check GPS Timestamp in file')

                    else:
                        try:
                            self.gps_datetime_object = datetime.strptime(self.gps_date_time, '%m/%d/%Y %H:%M:%S.%f')
                            self.gps_datetime_object = self.gps_datetime_object.replace(tzinfo=pytz.timezone(time_zone))
                        except ValueError:
                            pass
                        try:
                            self.gps_datetime_object = datetime.strptime(self.gps_date_time, '%m/%d/%y %H:%M:%S')
                            self.gps_datetime_object = self.gps_datetime_object.replace(tzinfo=pytz.timezone(time_zone))
                        except ValueError:
                            pass
                        try:
                            self.gps_datetime_object = datetime.strptime(self.gps_date_time, '%m/%d/%Y %H:%M:%S')
                            self.gps_datetime_object = self.gps_datetime_object.replace(tzinfo=pytz.timezone(time_zone))
                        except ValueError:
                            pass

                    self.latitude = float(m[3])
                    self.longitude = float(m[4])
                    self.gps_altitude = (float(m[0+6]))
                    self.gps_speed =(float(m[0+6]))
                    self.gps_number_of_satellites = (float(m[0+7]))

                    #use for older Eyas files 190315

                    if self.gps_datetime_object.replace(tzinfo=None) < dt.datetime(2019, 3, 16): #date of 190315 EYAS flight
                        self.latitude = float(m[3])
                        if np.abs(self.latitude) >180:
                            self.latitude =np.nan
                        self.longitude = float(m[4])
                        if np.abs(self.longitude) >180:
                            self.longitude = np.nan
                        self.gps_altitude = (float(m[0+5]))
                        self.gps_speed =(float(m[0+6]))
                        self.gps_number_of_satellites = (float(m[0+7]))

                
                elif('Pre-Angle' in m):
                    self.pre_angle = [float(n) for n in m[1:]]
                    self.x_angle_pre = float(m[0+5])
                    self.y_angle_pre = float(m[0+6])
                    # if np.isnan(self.x_angle_pre):
                    #     self.x_angle_pre = -90
                    #
                    # if np.isnan(self.y_angle_pre):
                    #     self.y_angle_pre = -90

                elif('Post-Angle' in m):
                    self.post_angle = [float(n) for n in m[1:]]
                    self.x_angle_post = float(m[0+5])
                    self.y_angle_post = float(m[0+6])
                    # if np.isnan(self.x_angle_post):
                    #     self.x_angle_post = -90
                    # if np.isnan(self.y_angle_post):
                    #     self.y_angle_post = -90

                elif('Pressure' in m):
                    self.pressure = float(m[0+2])

                elif('MS5607' in m):
                    self.pressure = float(m[1])
                    self.MS5607 = float(m[1])

                elif ('BME280' in m):
                    self.BME280 = float(m[1])

                elif('ADC Temperature' in m) or ('ADC' in m):
                    self.adc_temperature_celsius = float(m[1])

                elif ('Voltage (V)' in m) or ('voltage(V)' in m):  # I think this is when/if the the 2d data has a timestamp or angle as the first column
                    if ('Voltage (V)' == m[0]) or ('voltage(V)'== m[0]):
                        data_file_version = 0
                    elif ('AMU Time(ms)' == m[0]):
                        data_file_version = 1
                    break
            for j in f:
                m = j.split('\t')
                if m:
                    if data_file_version == 0:
                        xy.append([float(m[0]), float(m[1])])
                        self.data.append(m)
                    # xy.append([float(n) for n in m])
                    elif data_file_version ==1:
                        xy.append([float(m[1]), float(m[2])])  # 190718
                        self.data.append(m)

                else:
                    f.close()
                    break
            self.xy = np.array(xy)
            # self.data = np.array(xy)
            # self.xy = self.data[:,[0,1]]

        if self.cell_area_cm_2 == 0:
            self.cell_area_cm_2 = 4
            self.jsc = self.isc / self.cell_area_cm_2 # TODO: probably should make this 1, but most likely a safe bet because we are only using 2x2s
        self.pmax = self.pmax / self.cell_area_cm_2
        self.Jmp = self.imax / self.cell_area_cm_2
        # self.time_zone_corrected = self.timezone_convert()
        if not self.cell_id:
            if self.notes:
                serial_split = self.notes.split()[-1]
                if len(serial_split.split('-'))<2:
                    serial_num = self.notes.split()[-2]+'-'+self.notes.split()[-1]
                elif len(serial_split.split('-'))==2:
                    serial_num = serial_split
                else:
                    serial_num = []

                self.cell_id = serial_num

        if not self.model:
            if self.notes:
                self.model = self.notes.split()[0]

        if self.pressure:
            self.altitude_from_pressure = p2a.pressure_to_altitude(self.pressure)

    def plotIV(self):
        plt.plot(self.xy[:,0],self.xy[:,1], '-o', lw = 1, label = self.filename)

    def timezone_convert(self, time_zone="America/Los_Angeles"):
        # utc_time = dt.datetime.utcfromtimestamp(self.timestamp)
        if self.gps_date_time != '00/00/2000':
            utc_time = dt.datetime.strptime(self.gps_date_time + ' ' + self.gps_datetime_object, '%m/%d/%Y %H:%M:%S.%f')
            pst_timestamp = pytz.timezone(time_zone).localize(utc_time)
        else:
            pst_timestamp = 0
        return pst_timestamp

