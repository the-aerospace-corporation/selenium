import numpy as np
import matplotlib.pyplot as plt
import os
import pytz
import datetime as dt
import re
from datetime import datetime
import dateutil


class getLIVsingleSeleniumFile:
    def __init__(self,liv_txt,  time_zone = 'US/Pacific', start_time=None):
        """
        Opens and parses and single LIV file from Pearl Lab.  All parameters are pulled from the measurement and
        placed in the heard of the file, which are then broken into object attributes

        Args:
            liv_txt:
        """
        self.filename = os.path.basename(liv_txt)
        self.notes = []
        self.manufacturer = []
        self.model = []
        self.cell_id = []
        self.junction = []
        self.data = []
        self.xy = []
        self.Voc = []
        self.Jsc = []
        self.Vmax = []
        self.Isc = []
        self.Jmp = []
        self.Imax = []
        self.Pmax = []
        self.FillFactor = []
        self.Efficiency = []
        self.Cell_Temperature_Celsius = []
        self.Cell_Temperature_Kelvin = []
        self.Cell_Area_cm_2 = []
        self.AM0_constant = []
        self.x_angle = []
        self.y_angle = []
        self.x_angle_pre = []
        self.y_angle_pre = []
        self.x_angle_post = []
        self.y_angle_post = []
        self.altitude = []
        self.date = []
        self.time = []

        #Selenium Specific
        self.address = []
        self.firmware = []
        self.altitude = [] #Pressure Sensor temp, pressure, humidity, coversion of pressure to altitude
        self.timestamp = []
        self.utc = []
        self.gps_date_time = [] #Data, Time
        self.gps_datetime_object = []
        self.gps_datetime_object_timestamp = []
        self.latitude = []
        self.longitude = []
        self.gps_altitude = []
        self.gps_speed = []
        self.gps_number_of_satellites = []
        self.Telem = []
        self.sweep_points = []
        self.internal_voltage_raw = []
        self.internal_voltage_conv = []
        self.adc_temperature_C = []
        self.pressure = []
        self.pre_angle = []
        self.post_angle = []

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
                elif ('Serial Number' in m):
                    self.cell_id = m[0+1].rstrip()

                elif ('Voc (V)' in m) or ('Voc(V)' in m):
                    self.Voc = (float(m[0+1]))

                elif ('Jsc (A/cm^2)' in m) or ('Jsc(A/cm^2)' in m):
                    self.Jsc = (float(m[0+1]))

                elif ('Vmax (V)' in m) or ('Vmax(V)' in m):
                    self.Vmax = (float(m[0+1]))

                elif ('Isc (A)' in m) or ('Isc(A)' in m):
                    self.Isc = (float(m[0+1]))

                elif ('Imax (A)' in m) or ('Imax(A)' in m):
                    self.Imax = (float(m[0+1]))

                elif ('Pmax (W)' in m) or ('Pmax(W)' in m):
                    self.Pmax = (float(m[0+1]))

                elif ('FF' in m):
                    self.FillFactor = (float(m[0+1]))

                elif ('Eff (%)' in m) or ('Eff(%)' in m) or ('Eff ()' in m):
                    self.Efficiency = (float(m[0+1]))

                elif ('Cell Temp (C)' in m) or ('cell temp(C)' in m):
                    self.Cell_Temperature_Celsius = (float(m[0+1]))
                    self.Cell_Temperature_Kelvin = self.Cell_Temperature_Celsius+273.15

                elif ('Cell Temp (K)' in m) or ('cell temp(K)' in m):
                    self.Cell_Temperature_Kelvin = (float(m[0+1]))
                    self.Cell_Temperature_Celsius = self.Cell_Temperature_Kelvin-273.15

                elif ('Cell Area (cm^2)' in m) or ('cell area(cm^2)' in m):
                    self.Cell_Area_cm_2 = (float(m[0+1]))

                elif ('AM0 constant (W/cm^2)' in m):
                    self.AM0_constant = (float(m[0+1]))
                
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
                        except ValueError:
                            pass
                        try:
                            self.gps_datetime_object = datetime.strptime(self.gps_date_time, '%m/%d/%y %H:%M:%S')
                        except ValueError:
                            pass
                        try:
                            self.gps_datetime_object = datetime.strptime(self.gps_date_time, '%m/%d/%Y %H:%M:%S')
                        except:
                            print('Check GPS Timestamp in file')

                    else:
                        try:
                            self.gps_datetime_object = datetime.strptime(self.gps_date_time, '%m/%d/%Y %H:%M:%S.%f')
                        except ValueError:
                            pass
                        try:
                            self.gps_datetime_object = datetime.strptime(self.gps_date_time, '%m/%d/%y %H:%M:%S')
                        except ValueError:
                            pass
                        try:
                            self.gps_datetime_object = datetime.strptime(self.gps_date_time, '%m/%d/%Y %H:%M:%S')
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

                elif('ADC Temperature' in m) or ('ADC' in m):
                    self.adc_temperature_C = float(m[1])

                elif ('Voltage (V)' in m) or ('voltage(V)' in m):
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

        if self.Cell_Area_cm_2 == 0:
            self.Cell_Area_cm_2 = 4
            self.Jsc = self.Isc/self.Cell_Area_cm_2 # TODO: probably should make this 1, but most likely a safe bet because we are only using 2x2s
        self.Pmax = self.Pmax/self.Cell_Area_cm_2
        self.Jmp = self.Imax/self.Cell_Area_cm_2
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

