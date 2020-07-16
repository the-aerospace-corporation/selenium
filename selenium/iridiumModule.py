import numpy as np
import pearl.aeroData as ae

class iridiumModule(object):
    def __init__(self, iridium_data_file_txt):
        self.data_unsorted = np.loadtxt(iridium_data_file_txt, delimiter=',')
        self.time, self.data = ae.sortTwoArrays(self.data_unsorted[:,0], self.data_unsorted)
        self.latitude = self.data[:,1]
        self.longitude = self.data[:,2]
        self.altitude = self.data[:,3]
