import numpy as np
import pkg_resources


ozone_absorption_coefficients = np.loadtxt(pkg_resources.resource_filename('selenium', 'data/O3_cm2_molecule_absorption_coefficients.txt'), skiprows=1)
h2o_absorption_coefficients = np.loadtxt(pkg_resources.resource_filename('selenium', 'data/H2O_cm2_molecule_absorption_coefficients.txt'), skiprows=1)
# h2o_absorption_coefficients[:,1] = h2o_absorption_coefficients[:,1]/33.3679e21 # https://en.wikipedia.org/wiki/Number_density https://www.chem.purdue.edu/courses/chm424/Handouts/13.1%20Measuring%20Absorption.pdf
h2o_absorption_coefficients[:,1] = h2o_absorption_coefficients[:,1]*2.3e3/6.022e23 # https://www.chem.purdue.edu/courses/chm424/Handouts/13.1%20Measuring%20Absorption.pdf
extended_lamda = np.arange(ozone_absorption_coefficients[-1,0]+1, 2501)
ozone_extension = np.zeros((len(extended_lamda),2))
ozone_extension[:,0] = extended_lamda
ozone_extension[:,1] = np.zeros((len(extended_lamda)))
ozone_absorption_coefficients = np.vstack((ozone_absorption_coefficients, ozone_extension))