import dateutil.parser
import numpy as np
import tables
# from profilehooks import profile


class auraMLSO3Profile(object):
    def __init__(self, filename: str):
        """
        Takes in an AURA MLS ozone hdf file from GES DISC and processes it into a format that is useful for the selenium analysis.

        Args:
            filename (str): an AURA MLS ozone hdf file from GES DISC
        """
        self.filename = filename
        self.hdf5ref = tables.open_file(filename, mode='r', root_uep="/HDFEOS/SWATHS/O3")
        self.geo = self.hdf5ref.get_node("/", "Geolocation Fields")
        self.data = self.hdf5ref.get_node("/", "Data Fields")
        self.file_attr = tables.open_file(filename, mode='r', root_uep="/HDFEOS/ADDITIONAL")
        self.date = dateutil.parser.parse(self.file_attr.root.FILE_ATTRIBUTES._v_attrs.EndUTC)
        self.latitude = self.geo['Latitude'].read()
        self.longitude = self.geo['Longitude'].read()
        self.pressure = self.geo['Pressure'].read()
        # self.altitude = self.geo.Altitude.read()
        self.O3 = self.data.O3.read()
        self.O3Precision = self.data.O3Precision.read()
        self.O3[self.O3 == self.data.O3.atom.dflt] = np.nan
        # self.O3Apriori = self.data.O3Apriori.read()
        # self.ColumnAmountO3 = self.data.ColumnAmountO3.read()
        self.hdf5ref.close()

    def get_O3_profile(self, latitude: float, longitude: float):
        """
        Returns the ozone profile for a given latitude and longitude

        Args:
            latitude (float): latitude of interest
            longitude (float): longitude of interest

        Returns:
            np.ndarray: ozone profile for a given latitude and longitude where column 0 is ozone and column 1 is pressure (hPa)
        """
        o3profile = self._get_data_pressure_profile(latitude, longitude, self.O3)
        return o3profile

    def get_O3_profile_max(self, latitude: float, longitude:float):
        """
        Returns the max ozone profile for a given latitude and longitude using precision included int the MLS file
        Args:
            latitude (float): latitude of interest
            longitude (float): longitude of interest

        Returns:
            np.ndarray: ozone profile for a given latitude and longitude where column 0 is ozone with the max precision and column 1 is pressure (hPa)
        """
        o3profile = self._get_data_pressure_profile(latitude, longitude, self.O3)
        o3profile[:, 0] = o3profile[:, 0] + self.precision
        return o3profile

    def get_O3_profile_min(self, latitude: float, longitude: float):
        """
        Returns the min ozone profile for a given latitude and longitude using precision included int the MLS file

        Args:
            latitude (float): latitude of interest
            longitude (float): longitude of interest

        Returns:
            np.ndarray: ozone profile for a given latitude and longitude where column 0 is ozone with the min precision and column 1 is pressure (hPa)
        """
        o3profile = self._get_data_pressure_profile(latitude, longitude, self.O3)
        o3profile[:, 0] = o3profile[:, 0] - self.precision
        return o3profile

    def _get_data_pressure_profile(self, latitude: float, longitude: float, data_of_interest, precision_filter: bool=True):
        """
        Returns the data profile for a given latitude and longitude

        Args:
            latitude (float):
            longitude (float):
            data_of_interest: data from hdf file that you want to retur
            precision_filter (book): if true, will filter out data with precision filtered according to the MLS Documentation

        Returns:

        """
        if longitude > 180:
            longitude = longitude - 360.0

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

        filter = (np.abs(self.latitude) < 360) == (np.abs(self.longitude) < 360)  # filtering for unreal lat and lons
        val = np.abs(latitude - self.latitude[filter]) + np.abs(longitude - self.longitude[
            filter])  # subtracting lat and lon of interest then finding where its closest to zero
        ind = np.argmin(val)
        # print ind
        # print(self.latitude[ind])
        # print(self.longitude[ind])
        # print len(data_of_interest[ind])
        data = data_of_interest[ind]
        if precision_filter == True:
            precision_filter = self.O3Precision[ind] >= 0
            self.precision = self.O3Precision[ind][precision_filter]
            data = data[precision_filter]
            pressure = self.pressure[precision_filter]
        else:
            pressure = self.pressure
        # data_vs_pressure = np.vstack(((data_of_interest[ind], self.pressure))).T
        data_vs_pressure = np.vstack(((data, pressure))).T
        # data_vs_pressure = data_vs_pressure[data_vs_pressure[:,0]>0]
        high_pressure_filter = data_vs_pressure[:, 1] <= 261  # from MLS Documentation
        data_vs_pressure = data_vs_pressure[high_pressure_filter]
        self.precision = self.precision[high_pressure_filter]
        low_pressure_filter = data_vs_pressure[:, 1] > 0.001
        data_vs_pressure = data_vs_pressure[low_pressure_filter]
        self.precision = np.flip(self.precision[low_pressure_filter])
        data_vs_pressure = np.flip(data_vs_pressure, axis=0)
        return data_vs_pressure
