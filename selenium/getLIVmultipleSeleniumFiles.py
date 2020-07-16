import glob
import os
import numpy as np
import pandas as pd
from pearl.selenium.getLIVsingleSeleniumFile import getLIVsingleSeleniumFile
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pearl.selenium.press2alt as p2a


class getLIVmultipleSeleniumFiles: #opens a folder and parses each PEARL LIV file in the folder
    def __init__(self, folderpath, time_zone = 'US/Pacific'):
        os.chdir(folderpath)
        self.files = glob.glob('*.txt')
        if not self.files:
            self.files = glob.glob('*.c*')
        self.xy = []
        self.Voc = []
        self.Jsc = []
        self.Vmax = []
        self.Isc = []
        self.Imax = []
        self.Pmax = []
        self.FillFactor = []
        self.Efficiency = []
        self.fluence = []
        self.energy = []
        self.particle = []
        self.notes = []
        self.Cell_Temperature_Celsius = []
        self.Cell_Temperature_Kelvin = []
        self.Cell_Area_cm_2 = []
        self.timestamp = []
        self.time_zone_corrected = []
        self.gps_date_time = []
        self.gps_datetime_object = []
        self.gps_datetime_object_timestamp = []
        self.gps_latitude_longitude =[]
        self.latitude = []
        self.longitude = []
        self.gps_altitude = []
        self.gps_speed = []
        self.gps_number_of_satellites = []
        self.adc_temperature_C = []
        self.x_angle = []
        self.y_angle = []
        self.pre_angle = []
        self.post_angle = []
        self.x_angle_pre = []
        self.y_angle_pre = []
        self.x_angle_post = []
        self.y_angle_post = []
        self.pressure = []
        self.altitude_from_pressure = []
        self.dataframe = []


        for file in self.files:
            l = getLIVsingleSeleniumFile(file, time_zone)
            if l.xy.any():
                self.xy.append(l.xy)
            if isinstance(l.Voc, float):
                self.Voc.append(l.Voc)
            if isinstance(l.Jsc, float):
                self.Jsc.append(l.Jsc)
            if isinstance(l.Vmax, float):
                self.Vmax.append(l.Vmax)
            if isinstance(l.Isc, float):
                self.Isc.append(l.Isc)
            if isinstance(l.Imax,float):
                self.Imax.append(l.Imax)
            if isinstance(l.Pmax,float):
                self.Pmax.append(l.Pmax)
            if isinstance(l.FillFactor,float):
                self.FillFactor.append(l.FillFactor)
            if isinstance(l.Efficiency, float):
                self.Efficiency.append(l.Efficiency)
            if l.Cell_Temperature_Celsius:
                self.Cell_Temperature_Celsius.append(l.Cell_Temperature_Celsius)
            if l.Cell_Temperature_Kelvin:
                self.Cell_Temperature_Kelvin.append(l.Cell_Temperature_Kelvin)
            if l.Cell_Area_cm_2:
                self.Cell_Area_cm_2.append(l.Cell_Area_cm_2)
            if l.notes:
                self.notes.append(l.notes)
            if l.timestamp:
                self.timestamp.append(l.timestamp)
            # if l.time_zone_corrected:
            #     self.time_zone_corrected.append(l.time_zone_corrected)
            if l.gps_date_time:
                self.gps_date_time.append(l.gps_date_time)
            if l.gps_datetime_object:
                self.gps_datetime_object.append(l.gps_datetime_object)
            if l.gps_datetime_object_timestamp:
                self.gps_datetime_object_timestamp.append(l.gps_datetime_object_timestamp)
            if isinstance(l.latitude, float):
                self.latitude.append(l.latitude)
            if isinstance(l.longitude, float):
                self.longitude.append(l.longitude)
            if isinstance(l.gps_altitude, float):
                self.gps_altitude.append(l.gps_altitude)
            if isinstance(l.gps_speed, float):
                self.gps_speed.append(l.gps_speed)
            if isinstance(l.gps_number_of_satellites, float):
                self.gps_number_of_satellites.append(l.gps_number_of_satellites)
            if isinstance(l.adc_temperature_C, float):
                self.adc_temperature_C.append(l.adc_temperature_C)
            if l.x_angle_pre:
                self.x_angle_pre.append(l.x_angle_pre)
            if l.y_angle_pre:
                self.y_angle_pre.append(l.y_angle_pre)
            if l.x_angle_post:
                self.x_angle_post.append(l.x_angle_post)
            if l.y_angle_post:
                self.y_angle_post.append(l.y_angle_post)
            if l.pre_angle:
                self.pre_angle.append(l.pre_angle)
            if l.post_angle:
                self.post_angle.append(l.post_angle)

            if isinstance(l.pressure, float):
                self.pressure.append(l.pressure)
                self.altitude_from_pressure.append(p2a.pressure_to_altitude(l.pressure))
        
        dataframe = pd.DataFrame(index=pd.to_datetime(self.gps_datetime_object, utc=True))
        # dataframe = dataframe.tz_localize(time_zone)
        # print(len(dataframe))
        columns = ['Jsc', 'Isc', 'Voc', 'Imax', 'Vmax', 'Pmax', 'FillFactor', 'Efficiency']
        dataframe['Jsc'] = self.Jsc
        dataframe['Isc'] = self.Isc
        dataframe['Voc'] = self.Voc
        dataframe['Imax'] = self.Imax
        dataframe['Vmax'] = self.Vmax
        dataframe['Pmax'] = self.Pmax
        dataframe['FillFactor'] = self.FillFactor
        dataframe['Efficiency'] = self.Efficiency
        dataframe['x angle pre'] = self.x_angle_pre
        dataframe['y angle pre'] = self.y_angle_pre
        dataframe['x angle post'] = self.x_angle_post
        dataframe['y angle post'] = self.y_angle_post
        dataframe['Altitude'] = self.gps_altitude # temp fix
        dataframe['Altitude'] = dataframe['Altitude'].replace(1e6, np.nan)
        if self.pressure:
            dataframe['Pressure'] = self.pressure
            dataframe['Altitude_Pressure'] = self.altitude_from_pressure
        dataframe['Latitude'] = self.latitude
        dataframe['Longitude'] = self.longitude
        dataframe['Temperature (K)'] = self.Cell_Temperature_Kelvin
        dataframe['Temperature (C)'] = self.Cell_Temperature_Celsius
        dataframe['ADC Temperature'] = self.adc_temperature_C
        self.dataframe = dataframe


    def plotIV(self, fade_color = 'Blues'):
        cmap = plt.get_cmap(name = fade_color)
        numberofELplots = len(self.xy)
        line_colors = cmap(np.linspace(0,1,numberofELplots))

        for i in range(numberofELplots):
            plt.plot(self.xy[i][:,0], self.xy[i][:,1], 'o', lw =1, color = line_colors[i])

    def plot_param(self, param):
        ax = self.dataframe.plot(y=param)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax.minorticks_on()


    