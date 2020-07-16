import numpy as np
import pkg_resources

AM0 = np.loadtxt(pkg_resources.resource_filename('selenium', 'data/AM0_2500.txt'))
AM0_FULL = np.loadtxt(pkg_resources.resource_filename('selenium', 'data/AM0.txt'))
AM15 = np.loadtxt(pkg_resources.resource_filename('selenium', 'data/AM1_5.txt'))
