import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import pandas as pd
import pytz
import datetime as dt
import re
from datetime import datetime
import dateutil
import selenium.press2alt as p2a
from .getLogInfoSe import getLogInfoSe
from .LivSeDataContainer import LivSeDataContainer
import selenium.selenium_analysis as sa
import datetime
from matplotlib.dates import DayLocator, HourLocator, DateFormatter, drange
import pvlib

class getHighFreqSeData(object):
    def __init__(self, selenium_flight_data_folder_path, time_zone='utc', start_time=None):
        self.isc_df = sa.high_freq_data_df(os.path.join(selenium_flight_data_folder_path, 'ISC'), start_time=start_time)
        if 'VOC' in os.listdir(selenium_flight_data_folder_path):
            self.voc_df = sa.high_freq_data_df(os.path.join(selenium_flight_data_folder_path, 'VOC'), start_time=start_time)
            self.df = pd.concat([self.isc_df, self.voc_df]).sort_index()
        else:
            self.voc_df = pd.DataFrame()
            self.df = self.isc_df

        if 'MS56 Pressure(Pa)' in self.df.columns:
            self.df['Altitude_from_Pressure (m)'] = p2a.pressure_to_altitude(self.df['MS56 Pressure(Pa)'])

        # self.df.index = self.df.index.to_pydatetime()+datetime.timedelta(hours=-6)
        os.chdir(selenium_flight_data_folder_path)
        log_files = glob.glob('*.LOG')
        self.log_data = getLogInfoSe(log_files[0])
        self.start_time = start_time
        self.time_zone = time_zone

    def get_amu_df(self, amu_address):
        # isc_df = self.isc_df[['Latitude','Longitude', 'Altitude (m)', 'YAW', 'PITCH', 'MS56 Pressure(Pa)']].copy()
        # voc_df = self.voc_df[['Latitude','Longitude', 'Altitude (m)', 'YAW', 'PITCH', 'MS56 Pressure(Pa)']].copy()
        isc_df = self.isc_df[[col for col in self.isc_df.columns if '-' not in col]].copy()
        voc_df = self.voc_df[[col for col in self.voc_df.columns if '-' not in col]].copy()
        df = []
        for i, address in enumerate(self.log_data.address):
            if amu_address == address:
                for column, data in self.isc_df.iteritems():
                    data = list(data.values.copy())
                    if str(self.log_data.amu_number[i])+'-A' == column:
                        isc_df['Isc (A)'] = data

                    elif str(self.log_data.amu_number[i])+'-T' == column:
                        isc_df["Temperature (C)"] = data

                for column, data in self.voc_df.iteritems():
                    if str(self.log_data.amu_number[i])+'-V' == column:
                        voc_df["Voc (V)"] = data

                    elif str(self.log_data.amu_number[i])+'-T' == column:
                        voc_df["Temperature (C)"] = data
                df = pd.concat([isc_df,voc_df]).sort_index()

        if 'MS56 Pressure(Pa)' in df.columns:
            df['Altitude_from_Pressure (m)'] = p2a.pressure_to_altitude(self.df['MS56 Pressure(Pa)'])

        return df

    def getTelemMultipleSeObject(self):
        amu_dataobject_list = []
        for i, address in enumerate(self.log_data.address):
            data_obj = LivSeDataContainer()
            attributes = list(data_obj.__dict__.keys())
            amu_data = self.get_amu_df(address)
            data_obj.gps_datetime_object = amu_data.index.to_pydatetime()

            for attr in attributes:
                if hasattr(self.log_data.AMUs[i], attr):
                    setattr(data_obj, attr, getattr(self.log_data.AMUs[i], attr))

            for column, data in amu_data.iteritems():
                data = data.values
                if column in ['Latitude']:
                    data_obj.latitude = data
                elif column in ['Longitude']:
                    data_obj.longitude = data
                elif column in ['Altitude (m)']:
                    data_obj.gps_altitude = data
                    data_obj.altitude = data
                elif column in ['YAW']:
                    data_obj.yaw = data
                elif column in ['PITCH']:
                    data_obj.pitch = data
                elif column in ['MS56 Pressure(Pa)']:
                    data_obj.MS5607 = data
                    data_obj.pressure = data
                    data_obj.altitude_from_pressure = p2a.pressure_to_altitude(data_obj.pressure)
                elif column in ['Isc (A)']:
                    data_obj.isc = data
                elif column in ["Voc (V)"]:
                    data_obj.voc = data
                elif column in ["Temperature (C)"]:
                    data_obj.cell_temperature_celsius = data


            data_obj.make_dataframe()

            amu_dataobject_list.append(data_obj)

        return amu_dataobject_list

    def getTelemSingleObject(self, address):
        data_obj = LivSeDataContainer()
        attributes = list(data_obj.__dict__.keys())
        amu_data = self.get_amu_df(address)
        data_obj.gps_datetime_object = amu_data.index.to_pydatetime()

        for attr in attributes:
            if hasattr(self.log_data.AMUs, attr):
                setattr(data_obj, attr, getattr(self.log_data.AMUs, attr))

        for column, data in amu_data.iteritems():
            data = data.values
            if column in ['Latitude']:
                data_obj.latitude = data
            elif column in ['Longitude']:
                data_obj.longitude = data
            elif column in ['Altitude (m)']:
                data_obj.gps_altitude = data
                data_obj.altitude = data
            elif column in ['YAW']:
                data_obj.yaw = data
            elif column in ['PITCH']:
                data_obj.pitch = data
            elif column in ['MS56 Pressure(Pa)']:
                data_obj.MS5607 = data
                data_obj.pressure = data
                data_obj.altitude_from_pressure = p2a.pressure_to_altitude(data_obj.pressure)
            elif column in ['ISC (A)']:
                data_obj.isc = data
            elif column in ["Voc (V)"]:
                data_obj.voc = data
            elif column in ["Temperature (C)"]:
                data_obj.cell_temperature_celsius = data

        data_obj.make_dataframe()
        return data_obj

    def plot_data(self, x='alt', param='A', x_angle_limit=5, y_angle_limit=5, date_range=None):
        # self.filter_dataframe_for_angles(x_angle_limit, y_angle_limit)
        # self.df =self.df.dropna()
        format_time_axis=False
        if x == 'alt':
            x = self.df['Altitude (m)']

        elif x == 'alt_from_press':
            x = self.df['Altitude_from_Pressure (m)']

        elif x == 'press':
            x = self.df['MS56 Pressure(Pa)']

        elif x == 'time':
            format_time_axis = True
            x = self.df.index

        else:
            x = self.df['Altitude (m)']

        fig, ax = plt.subplots()
        if param in ['A', 'V', 'T']:
            for i, address in enumerate(self.log_data.address):
                data = self.df[str(self.log_data.amu_number[i])+'-' + param]
                # ax.plot(x, data, '-', label = self.log_data.amu_number[i])
                ax.plot(x, data, '.', label=self.log_data.cell_id[i])


        else:
            for i, address in enumerate(self.log_data.address):
                data = self.df[param]
                # ax.plot(x, data, '-', label = self.log_data.amu_number[i])
                ax.plot(x, data, '.', label=self.log_data.cell_id[i])


        if format_time_axis:
            time_format = '%H:%M'
            label_rotation = 45
            # ax.set_xlim(date_range)
            ax.xaxis.set_major_formatter(DateFormatter(time_format))
    def filter_dataframe_for_angles(self, x_angle_limit=5, y_angle_limit=5):
        self.df = self.df[np.abs(self.df['PITCH']) < x_angle_limit]
        self.df = self.df[np.abs(self.df['YAW']) < y_angle_limit]

