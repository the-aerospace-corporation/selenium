import numpy as np
from operator import itemgetter

def sortTwoArrays(sortByThisArray, arrayToBeSorted):
    zippedValues = zip(sortByThisArray, arrayToBeSorted)
    zippedValues = sorted(zippedValues, key=itemgetter(0))
    # zippedValues.sort(key=itemgetter(0)) #python 2.7 way
    sortedArray1, sortedArray2 = zip(*zippedValues)
    return np.array(sortedArray1), np.array(sortedArray2)

class iridiumModule(object):
    def __init__(self, iridium_data_file_txt):
        self.data_unsorted = np.loadtxt(iridium_data_file_txt, delimiter=',')
        self.time, self.data = sortTwoArrays(self.data_unsorted[:,0], self.data_unsorted)
        self.latitude = self.data[:,1]
        self.longitude = self.data[:,2]
        self.altitude = self.data[:,3]
