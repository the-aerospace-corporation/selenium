import numpy as np
import scipy as sp
from scipy import constants

M = 0.0289644  # kg/mol #Molar Mass of Earth's air
h1_std = np.array([0., 11., 20., 32., 47., 51., 71.]) * 1000.  # height at bottom of layer b (meters; e.g., h1 = 11 000 m)
p1_std = np.array([101325, 22632.10, 5474.89, 868.02, 110.91, 66.94, 3.96])  # static pressure (Pa)
T_std = np.array([288.15, 216.65, 216.65, 228.65, 270.65, 270.65, 214.65])  # standard temperature (K)
dTdh_std = np.array([-6.5, 0.0, 1.0, 2.8, 0.0, -2.8, -2.0]) / 1000.  # standard temperature lapse rate (K/m) in ISA


def altitude_to_pressure(altitude_km):

    if np.isscalar(altitude_km):
        altitude_km = np.array([altitude_km])

    pressure = []

    for alt in altitude_km:

        layer = find_bottom_layer_altitude(alt)

        P_b = p1_std[layer] # static pressure (Pa)
        T_b = T_std[layer] # standard temperature (K)
        L_b = dTdh_std[layer] # standard temperature lapse rate (K/m) in ISA
        l_b = h1_std[layer] # height at bottom of layer b (meters; e.g., h1 = 11 000 m)

        if L_b == 0:
            pressure.append(altitude_to_pressure_zero_lapse_rate(alt, P_b, T_b, l_b))

        else:
            pressure.append(altitude_to_pressure_non_zero_lapse_rate(alt, P_b, T_b, L_b, l_b))
    if np.shape(pressure)[0] <=1:
        pressure = pressure[0]

    else:
        pressure = np.array(pressure)

    return pressure

def altitude_to_pressure_non_zero_lapse_rate(altitude_km, pressure_b, temp_b, lapse_rate_b, alt_b):

    altitude_m = altitude_km*1000.
    exponent = (sp.constants.g * M)/(sp.constants.R * lapse_rate_b)
    pressure = pressure_b * (temp_b/(temp_b+lapse_rate_b*(altitude_m-alt_b))) ** exponent
    return pressure

def altitude_to_pressure_zero_lapse_rate(altitude_km, pressure_b, temp_b, alt_b):
    altitude_m = altitude_km*1000.
    exponent = np.exp((-sp.constants.g * M *(altitude_m-alt_b))/(sp.constants.R * temp_b))
    pressure = pressure_b * exponent
    return pressure


def pressure_to_altitude(pressure_Pa):

    if np.isscalar(pressure_Pa):
        pressure_Pa = np.array([pressure_Pa])

    altitude = []

    for pressure in pressure_Pa:

        layer = find_bottom_layer_pressure(pressure)

        P_b = p1_std[layer] # static pressure (Pa)
        T_b = T_std[layer] # standard temperature (K)
        L_b = dTdh_std[layer] # standard temperature lapse rate (K/m) in ISA
        l_b = h1_std[layer] # height at bottom of layer b (meters; e.g., h1 = 11 000 m)

        if L_b == 0:
            altitude.append(pressure_to_altitude_zero_lapse_rate(pressure, P_b, T_b, l_b))

        else:
            altitude.append(pressure_to_altitude_non_zero_lapse_rate(pressure, P_b, T_b, L_b, l_b))

    if np.shape(altitude)[0] <=1:
        altitude = altitude[0]

    else:
        altitude = np.array(altitude)

    return altitude


def pressure_to_altitude_non_zero_lapse_rate(pressure_Pa, pressure_b, temp_b, lapse_rate_b, alt_b):
    exponent = (sp.constants.R * lapse_rate_b)/(sp.constants.g * M)
    altitude = ((temp_b* (((pressure_b/pressure_Pa)**exponent)-1))/lapse_rate_b)+alt_b
    return altitude

def pressure_to_altitude_zero_lapse_rate(pressure_Pa, pressure_b, temp_b, alt_b):
    altitude = ((sp.constants.R * temp_b *(np.log(pressure_b) - np.log(pressure_Pa)))/(sp.constants.g *M)) + alt_b
    return altitude

def find_bottom_layer_altitude(altitude_km):
    altitude_m = altitude_km*1000

    for i, h1 in enumerate(h1_std):
        if altitude_m == 0:
            layer = 0

        elif altitude_m > (84.852 * 1000.):
            print('too high')
            layer = np.nan

        elif altitude_m < h1:
            layer = i-1
            break

    return layer


def find_bottom_layer_pressure(pressure_Pa):
    for i, p1 in enumerate(p1_std):
        if pressure_Pa > p1_std[1]:
            layer = 0

        elif pressure_Pa < (3.96):
            layer = i

        elif pressure_Pa > p1:
            layer = i - 1
            break

    return layer
