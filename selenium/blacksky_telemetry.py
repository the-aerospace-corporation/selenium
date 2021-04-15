import numpy as np
import datetime
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import pvlib

class blacksky_telemetry(object):
    def __init__(self, blacksky_telem_txt, date, time_zone ='US/Pacific'):
        self.file = blacksky_telem_txt
        self.time = []
        self.latitude = []
        self.longitude = []
        self.altitude = []
        self.data = []
        self.dataframe = []
        self.date = datetime.datetime.strptime(date, '%m/%d/%Y')
        self.datetime_index = []

        with open(blacksky_telem_txt,'rU') as f:
            data = []
            for j in f:
                m = j.split(',')
                dto = self.convert_decimal_hour_to_time(m[0])
                self.time.append(dto)
                self.datetime_index.append(self.add_time_to_datetime_object(self.date, m[0]))
                data.append([float(n) for n in m])

        self.data = np.array(data)
        self.latitude = self.data[:,1]
        self.longitude = self.data[:,2]
        self.altitude = self.data[:,3]

        dataframe = pd.DataFrame(data = self.data[:,1:], columns=['Latitude', 'Longitude', 'Altitude (m)'], index=pd.to_datetime(self.datetime_index, utc=True))
        # dataframe = dataframe.tz_localize(time_zone)

        # solarposition = pvlib.solarposition.get_solarposition(time=dataframe.index, latitude=dataframe['Latitude'].values, longitude=dataframe['Longitude'].values, altitude=dataframe['Altitude'].values)
        # dataframe['Zenith'] = solarposition.zenith.values
        # dataframe['Cos Zenith'] = np.cos(np.deg2rad(solarposition.zenith.values))
        self.dataframe = dataframe.sort_index()

        # print(self.dataframe.resample('1S'))

    def plot_altitude(self):
        ax = self.dataframe.plot(y='Altitude')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax.minorticks_on()
        # ax.tick_params(axis='x', which='minor', labelbottom=True)

    def convert_decimal_hour_to_time(self, time_string):
        m = time_string.split(',')
        h = int(float(m[0]))
        min_1 = (float(m[0]) - h) * 60
        min = int(min_1)
        s_1 = (min_1 - min)*60.
        s = int(s_1)
        ms = int((s_1 - s)*1e6)
        time_object = datetime.time(hour=h, minute=min, second=s)
        return time_object

    def add_time_to_datetime_object(self, datetime_object, time_string):
        time_object = self.convert_decimal_hour_to_time(time_string)
        new_datetime_object = datetime_object.replace(hour = time_object.hour, minute = time_object.minute, second = time_object.second)
        return new_datetime_object

#interpolate for seconds, but fixt time series first need to figure a good way to interpolate and work with time series