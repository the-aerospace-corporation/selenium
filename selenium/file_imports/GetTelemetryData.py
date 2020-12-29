import os
import pandas as pd
import glob

class GetTelemetryData(object):
    def __init__(self, folder_path):
        os.chdir(folder_path)
        file_extension_check = os.listdir(folder_path)[0]
        if file_extension_check.endswith('.ISC'):
            self.files = glob.glob('*.ISC')
        elif file_extension_check.endswith('.VOC'):
            self.files = glob.glob('*.VOC*')
        elif file_extension_check.endswith('.TXT'):
            self.files = glob.glob('*.TXT*')

        self.dataframe = pd.DataFrame()

        list_of_telem = []
        for file in self.files:
            list_of_telem.append(pd.read_csv(file, sep='\t'))

        self.dataframe = pd.concat(list_of_telem)
        self.dataframe.columns = [a.lower() for a in self.dataframe.columns]
        self.dataframe['gps datetime'] = self.dataframe['gps date']+' '+self.dataframe['gps time']
        self.dataframe['datetime'] = pd.to_datetime(self.dataframe['gps datetime'], infer_datetime_format=True, errors='coerce')

        # removing bad gps time stamps data
        self.dataframe = self.dataframe[self.dataframe.datetime.notnull()]
        self.dataframe = self.dataframe.set_index('datetime')
        # print(self.dateframe.index)


