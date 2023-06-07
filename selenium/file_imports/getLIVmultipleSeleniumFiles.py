import datetime
import glob
import os
import numpy as np
import pandas as pd
from selenium.file_imports.getLIVsingleSeleniumFile import getLIVsingleSeleniumFile
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import selenium.selenium_analysis as sa
from .LivSeDataContainer import LivSeDataContainer
import pytz


class getLIVmultipleSeleniumFiles(LivSeDataContainer): #opens a folder and parses each PEARL LIV file in the folder
    def __init__(self, folderpath, time_zone = 'utc', start_time=None):
        LivSeDataContainer.__init__(self)
        os.chdir(folderpath)
        self.file_name = glob.glob('*.txt')
        if not self.file_name:
            self.file_name = glob.glob('*.c*')
        self.data_objects = []
        attributes = list(self.__dict__.keys())
        for file in self.file_name:
            self.data_objects.append(getLIVsingleSeleniumFile(file, time_zone, start_time))

        attributes.remove('file_name')
        for attr in attributes:
            attr_data = []
            for i, data_object in enumerate(self.data_objects):
                if hasattr(data_object, attr):

                    if attr in ['xy', 'voltage', 'current', 'voltage_std_dev.size', 'current_std_dev.size']:
                        if isinstance(getattr(data_object, attr), np.ndarray):
                            if getattr(data_object, attr).size != 0:
                                attr_data.append(getattr(data_object, attr))
                        elif isinstance(getattr(data_object, attr), list):
                            if getattr(data_object, attr):
                                attr_data.append(getattr(data_object, attr))

                    elif attr in ['fluence', 'gridline_obscuration']:
                        attr_from_object = getattr(data_object, attr)
                        if isinstance(attr_from_object, str):
                            if attr_from_object in ['control', 'low V']:
                                attr_data.append(0)

                        elif isinstance(getattr(data_object, attr), list):
                            if getattr(data_object, attr):
                                attr_data.append(getattr(data_object, attr))

                        elif getattr(data_object, attr) > -1:
                            attr_data.append(getattr(data_object, attr))

                    elif attr in ['gridline_obscuration']:
                        if getattr(data_object, attr) > -1:
                            attr_data.append(getattr(data_object, attr))

                    elif attr in ['gps_datetime_object']:
                        jpl_flight_date = datetime.datetime(2019, 10, 7, tzinfo=pytz.UTC)
                        if jpl_flight_date.date() == getattr(data_object, attr).date():
                            if i == 0:
                                previous_datetime = getattr(data_object, attr)
                                attr_data.append(getattr(data_object, attr))
                            else:
                                current_datetime = getattr(data_object, attr)
                                if current_datetime < previous_datetime:
                                    new_datetime = current_datetime.replace(day=current_datetime.day + 1)
                                    attr_data.append(new_datetime)
                                    previous_datetime = new_datetime
                                else:
                                    attr_data.append(getattr(data_object, attr))
                        else:
                            attr_data.append(getattr(data_object, attr))


                    else:
                        attr_data.append(getattr(data_object, attr))
            setattr(self, attr, attr_data)

        self.dataframe = self.make_dataframe()
        # self.make_dataframe()
        # self.__dict__.keys()

    # def make_dataframe(self): #TODO: Move this to LIV data container and use it for the telem data...maybe make a dictionary mapping the column human readable names to attributes.
    #     dataframe = pd.DataFrame(index=pd.to_datetime(self.gps_datetime_object, utc=True))
    #     # dataframe = dataframe.tz_localize(time_zone)
    #     # print(len(dataframe))
    #     columns = ['Jsc (A/cm2)', 'Isc (A)', 'Voc (V)', 'Imax (A)', 'Vmax (V)', 'Pmax (W)', 'FillFactor', 'Efficiency (%)']
    #     dataframe['Jsc (A/cm2)'] = self.jsc
    #     dataframe['Isc (A)'] = self.isc
    #     dataframe['Voc (V)'] = self.voc
    #     dataframe['Imax (A)'] = self.imax
    #     dataframe['Vmax (V)'] = self.vmax
    #     dataframe['Pmax (W)'] = self.pmax
    #     dataframe['FillFactor'] = self.fill_factor
    #     dataframe['Efficiency (%)'] = self.efficiency
    #     dataframe['x angle pre'] = self.x_angle_pre
    #     dataframe['y angle pre'] = self.y_angle_pre
    #     dataframe['x angle post'] = self.x_angle_post
    #     dataframe['y angle post'] = self.y_angle_post
    #     dataframe['Altitude (m)'] = self.gps_altitude # temp fix
    #     dataframe['Altitude (m)'] = dataframe['Altitude (m)'].replace(1e6, np.nan)
    #     if self.pressure:
    #         dataframe['Pressure'] = self.pressure
    #         dataframe['Altitude_from_Pressure (m)'] = self.altitude_from_pressure
    #     dataframe['Latitude'] = self.latitude
    #     dataframe['Longitude'] = self.longitude
    #     dataframe['Temperature (K)'] = self.cell_temperature_kelvin
    #     dataframe['Temperature (C)'] = self.cell_temperature_celsius
    #     dataframe['ADC Temperature (C)'] = self.adc_temperature_celsius
    #     self.dataframe = dataframe


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


    