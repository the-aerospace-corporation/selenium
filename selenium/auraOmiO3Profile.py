import tables
import numpy as np

class auraOmiO3Profile(object):
    def __init__(self, filename):
        self.filename = filename
        self.hdf5ref = tables.open_file(filename, mode='r', root_uep="/HDFEOS/SWATHS/O3Profile")
        self.geo = self.hdf5ref.get_node("/", "Geolocation Fields")
        self.data = self.hdf5ref.get_node("/", "Data Fields")
        self.latitude = self.geo.Latitude.read()
        self.longitude = self.geo.Longitude.read()
        self.altitude = self.geo.Altitude.read()
        self.pressure = self.geo.Pressure.read()
        self.O3 = self.data.O3.read()
        self.O3[self.O3==self.data.O3.atom.dflt] = np.nan
        self.O3Apriori = self.data.O3Apriori.read()
        self.ColumnAmountO3 = self.data.ColumnAmountO3.read()
        self.hdf5ref.close()

    def get_O3_profile(self,latitude, longitude):
        o3profile = self._get_data_altitude_profile(latitude, longitude, self.O3)
        return o3profile

    def get_O3_profile_vmr(self,latitude, longitude):
        if longitude > 180:
            longitude = longitude - 360.0

        min_val = 5

        S = np.shape(self.pressure)

        x_ind = 1
        y_ind = 1

        for x in range(S[0]):
            for y in range(S[1]):
                if (np.abs(self.latitude[x, y]) < 360) and (np.abs(self.longitude[x, y]) < 360):
                    val = np.abs(latitude - self.latitude[x, y]) + np.abs(longitude - self.longitude[x, y])
                    if val < min_val:
                        if np.sum(np.isnan(self.O3[x, y])) < S[2] - 1:
                            min_val = val
                            x_ind = x
                            y_ind = y

        # print x_ind
        # print y_ind
        # print(self.latitude[x_ind, y_ind])
        # print(self.longitude[x_ind, y_ind])
        vmr = ((1.2672*self.O3[x_ind, y_ind]) / np.diff(self.pressure[x_ind, y_ind]))*1e-6
        data_vs_vmr = np.vstack((vmr, self.pressure[x_ind,y_ind,:-1])).T
        return data_vs_vmr


    def _get_data_altitude_profile(self,latitude, longitude, data_of_interest):
        data_vs_altitude = self._get_data_profile(latitude, longitude, data_of_interest, altitude_pressure=self.altitude)
        return data_vs_altitude

    def _get_data_pressure_profile(self,latitude, longitude, data_of_interest):
        data_vs_altitude = self._get_data_profile(latitude, longitude, data_of_interest, altitude_pressure=self.pressure)
        return data_vs_altitude


    def _get_data_profile(self,latitude, longitude, data_of_interest, altitude_pressure):
        if longitude > 180:
            longitude = longitude-360.0

        min_val = 5

        S = np.shape(altitude_pressure)

        x_ind = 1
        y_ind = 1

        for x in range(S[0]):
            for y in range(S[1]):
                if (np.abs(self.latitude[x,y])<360) and (np.abs(self.longitude[x,y])<360):
                    val = np.abs(latitude-self.latitude[x,y]) + np.abs(longitude-self.longitude[x,y])
                    if val < min_val:
                        if np.sum(np.isnan(data_of_interest[x,y])) < S[2] - 1:
                            min_val = val
                            x_ind = x
                            y_ind = y

        # print x_ind
        # print y_ind
        # print self.latitude[x_ind, y_ind]
        # print self.longitude[x_ind, y_ind]
        data_vs_profile = np.vstack((data_of_interest[x_ind,y_ind], altitude_pressure[x_ind,y_ind,:-1])).T
        return data_vs_profile
