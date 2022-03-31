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

class getHighFreqSeData(object):
    def __init__(self, selenium_flight_data_folder_path, time_zone='utc', start_time=None):
        self.isc_df = sa.high_freq_data_df(os.path.join(selenium_flight_data_folder_path, 'ISC'), start_time=start_time)
        self.voc_df = sa.high_freq_data_df(os.path.join(selenium_flight_data_folder_path, 'VOC'), start_time=start_time)
        os.chdir(selenium_flight_data_folder_path)
        log_files = glob.glob('*.LOG')
        self.log_data = getLogInfoSe(log_files[0])
        self.start_time = start_time
        self.time_zone = time_zone

    def get_amu_df(self, amu_address):
        isc_df = self.isc_df[['Latitude','Longitude', 'Altitude (m)', 'YAW', 'PITCH', 'MS56 Pressure(Pa)']].copy()
        voc_df = self.voc_df[['Latitude','Longitude', 'Altitude (m)', 'YAW', 'PITCH', 'MS56 Pressure(Pa)']].copy()
        df = []
        for i, address in enumerate(self.log_data.address):
            if amu_address == address:
                for column, data in self.isc_df.iteritems():
                    data = list(data.values.copy())
                    if str(self.log_data.amu_number[i])+'-A' == column:
                        isc_df['ISC (A)'] = data

                    elif str(self.log_data.amu_number[i])+'-T' == column:
                        isc_df["Temperature (C)"] = data

                for column, data in self.voc_df.iteritems():
                    if str(self.log_data.amu_number[i])+'-V' == column:
                        voc_df["Voc (V)"] = data

                    elif str(self.log_data.amu_number[i])+'-T' == column:
                        voc_df["Temperature (C)"] = data
                df = pd.concat([isc_df,voc_df]).sort_index()

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
                elif column in ['ISC (A)']:
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