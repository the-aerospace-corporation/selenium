import numpy as np
import pkg_resources

# ASTM E490 2014
AM0 = np.loadtxt(pkg_resources.resource_filename('selenium', 'data/AM0_2500.txt'))
AM0_FULL = np.loadtxt(pkg_resources.resource_filename('selenium', 'data/AM0.txt'))
AM15 = np.loadtxt(pkg_resources.resource_filename('selenium', 'data/AM1_5.txt'))

# ASTM E490 2019
AM0_2019 = np.loadtxt(pkg_resources.resource_filename('pearl', 'data/ASTM_e490_2019_2500.txt'))
AM0_FULL_2019 = np.loadtxt(pkg_resources.resource_filename('pearl', 'data/ASTM_e490_2019.txt'))