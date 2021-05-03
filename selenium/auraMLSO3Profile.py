import tables
import numpy as np
from profilehooks import profile

class auraMLSO3Profile(object):
    def __init__(self, filename):
        self.filename = filename
        self.hdf5ref = tables.open_file(filename, mode='r', root_uep="/HDFEOS/SWATHS/O3")
        self.geo = self.hdf5ref.get_node("/", "Geolocation Fields")
        self.data = self.hdf5ref.get_node("/", "Data Fields")
        self.latitude = self.geo['Latitude'].read()
        self.longitude = self.geo['Longitude'].read()
        self.pressure = self.geo['Pressure'].read()
        # self.altitude = self.geo.Altitude.read()
        self.O3 = self.data.O3.read()
        self.O3[self.O3==self.data.O3.atom.dflt] = np.nan
        # self.O3Apriori = self.data.O3Apriori.read()
        # self.ColumnAmountO3 = self.data.ColumnAmountO3.read()
        self.hdf5ref.close()

    def get_O3_profile(self,latitude, longitude):
        o3profile = self._get_data_pressure_profile(latitude, longitude, self.O3)
        o3profile = np.flip(o3profile, axis=0)
        return o3profile

    def _get_data_pressure_profile(self, latitude, longitude, data_of_interest):
        if longitude > 180:
            longitude = longitude-360.0

        # min_val = 5
        #
        # S = np.shape(self.latitude)
        # ind = 0
        #
        # for i in range(S[0]):
        #     if (np.abs(self.latitude[i])<360) and (np.abs(self.longitude[i])<360):
        #         val = np.abs(latitude-self.latitude[i]) + np.abs(longitude-self.longitude[i])
        #         if val < min_val:
        #             # if np.sum(np.isnan(data_of_interest[x,y])) < S[2] - 1:
        #             min_val = val
        #             ind = i

        filter = (np.abs(self.latitude)<360) == (np.abs(self.longitude)<360) # filtering for unreal lat and lons
        val = np.abs(latitude - self.latitude[filter]) + np.abs(longitude - self.longitude[filter]) # subtracting lat and lon of interest then finding where its closest to zero
        ind = np.argmin(val)
        # print ind
        # print(self.latitude[ind])
        # print(self.longitude[ind])
        # print len(data_of_interest[ind])
        data_vs_pressure = np.vstack(((data_of_interest[ind], self.pressure))).T
        data_vs_pressure = data_vs_pressure[data_vs_pressure[:,0]>0]
        data_vs_pressure = data_vs_pressure[data_vs_pressure[:,1]<=300]
        data_vs_pressure = data_vs_pressure[data_vs_pressure[:,1]>0.01]
        return data_vs_pressure
