import numpy as np
import pkg_resources


ozone_absorption_coefficients = np.loadtxt(pkg_resources.resource_filename('selenium', 'data/O3_cm2_molecule_absorption_coefficients.txt'), skiprows=1)
extended_lamda = np.arange(ozone_absorption_coefficients[-1,0]+1, 2501)
ozone_extension = np.zeros((len(extended_lamda),2))
ozone_extension[:,0] = extended_lamda
ozone_extension[:,1] = np.zeros((len(extended_lamda)))
ozone_absorption_coefficients = np.vstack((ozone_absorption_coefficients, ozone_extension))