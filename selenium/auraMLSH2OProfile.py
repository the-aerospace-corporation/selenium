import tables
import numpy as np
import dateutil.parser
from profilehooks import profile

class auraMLSH2OProfile(object):
    def __init__(self, filename):
        self.filename = filename
        self.hdf5ref = tables.open_file(filename, mode='r', root_uep="/HDFEOS/SWATHS/H2O")
        self.geo = self.hdf5ref.get_node("/", "Geolocation Fields")
        self.data = self.hdf5ref.get_node("/", "Data Fields")
        self.file_attr = tables.open_file(filename, mode='r', root_uep="/HDFEOS/ADDITIONAL")
        self.date = dateutil.parser.parse(self.file_attr.root.FILE_ATTRIBUTES._v_attrs.EndUTC)
        self.latitude = self.geo['Latitude'].read()
        self.longitude = self.geo['Longitude'].read()
        self.pressure = self.geo['Pressure'].read()
        # self.altitude = self.geo.Altitude.read()
        self.H20 = self.data.H2O.read()
        self.H2OPrecision = self.data.H2OPrecision.read()
        self.H20[self.H20 == self.data.H2O.atom.dflt] = np.nan
        # self.O3Apriori = self.data.O3Apriori.read()
        # self.ColumnAmountO3 = self.data.ColumnAmountO3.read()
        self.hdf5ref.close()

    def get_H2O_profile(self, latitude, longitude):
        h2o_profile = self._get_data_pressure_profile(latitude, longitude, self.H20)
        h2o_profile = np.flip(h2o_profile, axis=0)
        return h2o_profile

    def _get_data_pressure_profile(self, latitude, longitude, data_of_interest, precision_filter=True):
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
        data = data_of_interest[ind]
        if precision_filter == True:
            precision_filter = self.H2OPrecision[ind] >= 0
            self.precision = self.H2OPrecision[ind][precision_filter]
            data = data[precision_filter]
            pressure = self.pressure[precision_filter]
        else:
            pressure = self.pressure
        # data_vs_pressure = np.vstack(((data_of_interest[ind], self.pressure))).T
        data_vs_pressure = np.vstack(((data, pressure))).T
        # data_vs_pressure = data_vs_pressure[data_vs_pressure[:,0]>0]
        high_pressure_filter = data_vs_pressure[:, 1] <= 261 #from MLS Documentation
        data_vs_pressure = data_vs_pressure[high_pressure_filter]
        self.precision = self.precision[high_pressure_filter]
        low_pressure_filter = data_vs_pressure[:, 1] > 0.001
        data_vs_pressure = data_vs_pressure[low_pressure_filter]
        self.precision = self.precision[low_pressure_filter]
        return data_vs_pressure
