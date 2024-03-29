import numpy as np
import pvlib as pv
import scipy as sp
from scipy import constants
from scipy import integrate
from scipy import interpolate
from scipy import constants as c
from scipy import stats
import pandas as pd
import selenium.press2alt as pa
import selenium.solar_spectra as pc
import selenium.constants_Se as c_Se
from .irradianceSpectrum import irradianceSpectrum
from operator import itemgetter
import os
from datetime import datetime
import dateutil.parser
import pytz
# from profilehooks import profile
# selenium_data_folder = Path('pearl/selenium/data/')
# O3_absorption_coefficients_filepath = selenium_data_folder / 'O3_cm2_molecule_absorption_coefficients.txt'
# o3_abs_coeff = np.loadtxt(pkg_resources.resource_filename('pearl', 'selenium/data/O3_cm2_molecule_absorption_coefficients.txt'), skiprows=1)
# o3_abs_coeff = np.loadtxt(O3_absorption_coefficients_filepath, skiprows=1)

def filter_for_angle(parameter, pan_angles, tilt_angles, pan_angle_limit, tilt_angle_limit):
    """
    Filter data for angles that fall within a specified range. Parameter, x-angles, and y-angles need to be the same size and shape
    
    Args:
        parameter: float or 1d array of parameter interest
        pan_angles: float or 1d array of angles to filter by
        tilt_angles: float or 1d array of angles to filter by
        pan_angle_limit: x-angle to limit filter
        tilt_angle_limit: y-angle to limit filter

    Returns:
        Filtered data
    """

    filtered = []
    for i in range(len(parameter)):
        if (np.abs(pan_angles[i]) < pan_angle_limit) & (np.abs(tilt_angles[i]) < tilt_angle_limit):
            filtered.append(parameter[i])
    return filtered


def current_angle_correction(current, pan_angle=None, tilt_angle=None):
    """
    Corrects current for off pointing by taking the dot product of the pan and tilt angle deviation

    Args:
        current: Current to be corrected such as short circuit current
        pan_angle: The pan angle from direct incidence angle
        tilt_angle: The tilt angle from direct incidence angle

    Returns:
        Current corrected to what it would be if the intensity was at an angle of incidence of 0 degrees

    """
    angle_corrected_for_current = current * (1 / np.cos(np.deg2rad(pan_angle))) * (1 / np.cos(np.deg2rad(tilt_angle)))
    return angle_corrected_for_current


def correct_for_temperature(parameter, temp_of_measurment, target_temp, temperature_coeffecient):
    """
    Corrects a solar cell parameter such as current or voltage to the what the value should be at a target temperature

    Args:
        parameter: Solar cell parameter to be corrected such as current or voltage
        temp_of_measurement: Temperature at which the measurement was taken
        target_temp: The target temperature at which to correct the measured parameter
        temperature_coeffecient: The linear temperature coefficient of the parameter

    Returns:
        Parameter corrected to what its value would be at the target temperature

    """
    new_parameter = parameter + ((target_temp - temp_of_measurment) * temperature_coeffecient)
    return new_parameter


def correct_current_for_sun_earth_distance(current, utc_time, delta_t=None):
    """
    Current current of solar cell for sun earth distance

    Args:
        current: Current of the cell
        utc_time: Time in UTC as a python datetime object

    Returns:
        Current corrected for earth sun distance
    """
    earth_sun_distance_AU = pv.solarposition.nrel_earthsun_distance(utc_time, delta_t=delta_t).values
    r2_sun = 1 / (earth_sun_distance_AU ** 2)
    earth_sun_correction = 1 / (r2_sun)
    corrected_current = current*earth_sun_correction
    return corrected_current

### Ozone Functions

def ppmV_to_mol_m3(ppmV, molecular_weight=47.997, temp_K = 273.15):
    R = (sp.constants.R/sp.constants.value('standard atmosphere'))*1000. # R in L atm mol-1 K-1
    mg_m3 = ppmV*(molecular_weight/(R*temp_K))
    mol_m3 = (mg_m3/1000)/molecular_weight
    return mol_m3

def mg_m3_to_ppmV(mg_m3, molecular_weight=47.997, temp_K = 273.15):
    R = (sp.constants.R/sp.constants.value('standard atmosphere'))*1000. # R in L atm mol-1 K-1
    ppmV = mg_m3*((R*temp_K)/ molecular_weight)
    # check = ((mg_m3/1000.)/molecular_weight) * sp.constants.R * temp_K *(1/(sp.constants.value('standard atmosphere')/1000.))*1000
    # print(check)
    return ppmV

def total_ozone_dobson_from_ppmV_vs_pressure(vmr_pressure):
    """
    Use conversions.pdf to convert vmr data to Dobson Units

    Args:
        vmr_pressure: data from satellite in units vmr vs pressure

    Returns:
        total gas in Dobson units
    """
    R_air = 287.058 #specific gas constant for dry air
    T_o = 273.15
    C = 10*((R_air*T_o)/(sp.constants.g*sp.constants.value('standard atmosphere')))
    total_ozone_column = C*sp.integrate.trapz(vmr_pressure[:, 0]/1e-6, vmr_pressure[:, 1])
    return total_ozone_column

def total_ozone_from_mol_m3_vs_altitude_km(mol_m3_altitude_km):
    altitude_m = mol_m3_altitude_km[:,1]*1000. #convert to meters
    total_ozone_column = (sp.integrate.trapz(mol_m3_altitude_km[:,0], altitude_m)*sp.constants.N_A)/2.687e20 # 1DU = 2.69e20 molecules/m-2
    return total_ozone_column

def convert_vmr_pressure_to_mol_m3_altitude_km(vmr_pressure, molecular_weight=47.997, temp_K = 273.15):
    ppmV= vmr_pressure[:,0]/1e-6 #convert ppmV
    mol_m3 = ppmV_to_mol_m3(ppmV, molecular_weight, temp_K)
    altitude_km = pa.pressure_to_altitude(vmr_pressure[:,1]*100)/1000
    mol_m3_altitude_km = np.vstack((mol_m3, altitude_km)).T
    mol_m3_altitude_km = np.flip(mol_m3_altitude_km, axis=0)
    return mol_m3_altitude_km


def total_ozone_above_pressure(ozone_profile_ppmV, pressure_limit_hPa):
    # interp_profile = sp.interpolate.interp1d(np.log(ozone_profile_ppmV[:,1]), ozone_profile_ppmV[:,0])
    pressures = np.linspace(np.min(ozone_profile_ppmV[:,1]), np.max(ozone_profile_ppmV[:,1]), 1000)
    # vmr = interp_profile(np.log(pressures))
    vmr = np.interp(np.log(pressures), np.log(ozone_profile_ppmV[:,1]), ozone_profile_ppmV[:,0])
    i_min = np.abs(pressures - pressure_limit_hPa).argmin()
    ozone_profile_to_integrate = np.vstack((vmr[0:i_min],pressures[0:i_min])).T
    total_ozone = total_ozone_dobson_from_ppmV_vs_pressure(ozone_profile_to_integrate)
    return total_ozone

def combine_external_telem_with_selenium(telem_dataframe, selenium_dataframe):
    combine = pd.concat([telem_dataframe, selenium_dataframe], sort=True)
    new_data = combine.sort_index()
    for column in telem_dataframe.columns:
        new_data[column] = new_data[column].interpolate()
    new_data = new_data.dropna(axis=0)
    return new_data

def ozone_attenuated_irradiance(ozone_DU=0, zenith_angle=0, irradiance_spectrum=None):
    ozone_molecules_cm2 = ozone_DU * 2.69e16

    if irradiance_spectrum is None:
        irradiance_spectrum = np.copy(pc.AM0_2019)

    else:
        irradiance_spectrum = irradiance_spectrum

    # min_AM0 = np.min(irradiance_spectrum[:,0])
    # max_AM0 = np.max(irradiance_spectrum[:,0])
    # i_min = np.abs(c_Se.ozone_absorption_coefficients[:,0] - min_AM0).argmin()
    # i_max = np.abs(c_Se.ozone_absorption_coefficients[:,0] - max_AM0).argmin()
    # new_ozone = c_Se.ozone_absorption_coefficients[i_min:i_max+1]
    #
    #
    min_ozone = np.min(c_Se.ozone_absorption_coefficients[:,0])
    # max_ozone = np.max(c_Se.ozone_absorption_coefficients[:,0])
    i_min_ozone = np.abs(irradiance_spectrum[:,0] - min_ozone).argmin()
    # i_max_ozone = np.abs(irradiance_spectrum[:,0] - max_ozone).argmin()
    # new_irradiance_spectrum = np.copy(irradiance_spectrum[i_min_ozone+1:i_max_ozone+1])

    ozone_transmission_spectrum = generate_ozone_transmission_spectrum(ozone_DU, zenith_angle=zenith_angle)

    # f_interp_ozone = sp.interpolate.interp1d(ozone_transmission_spectrum[:,0], ozone_transmission_spectrum[:,1])
    ozone_interp = np.zeros(np.shape(irradiance_spectrum[i_min_ozone+1:]))
    ozone_interp[:,0] = irradiance_spectrum[i_min_ozone+1:,0]
    # ozone_interp[:,1] = f_interp_ozone(irradiance_spectrum[i_min_ozone+1:,0])
    ozone_interp[:, 1] = np.interp(irradiance_spectrum[i_min_ozone+1:,0], ozone_transmission_spectrum[:,0], ozone_transmission_spectrum[:,1])
    ozone_attenuated = np.copy(irradiance_spectrum[i_min_ozone+1:])
    ozone_attenuated[:,1] = irradiance_spectrum[i_min_ozone+1:,1]*ozone_interp[:,1]
    # diff = np.copy(ozone_attenuated)
    # diff[:,1] = ozone_attenuated[:,1] - irradiance_spectrum[i_min_ozone+1:,1]
    return ozone_attenuated

def gas_attenuated_irradiance(DU, absorption_coeff, zenith_angle=0, irradiance_spectrum=None):
    ozone_molecules_cm2 = DU * 2.69e16

    if irradiance_spectrum is None:
        irradiance_spectrum = np.copy(pc.AM0_2019)

    else:
        irradiance_spectrum = irradiance_spectrum

    min_AM0 = np.min(irradiance_spectrum[:,0])
    max_AM0 = np.max(irradiance_spectrum[:,0])
    i_min = np.abs(absorption_coeff[:,0] - min_AM0).argmin()
    i_max = np.abs(absorption_coeff[:,0] - max_AM0).argmin()
    new_ozone = absorption_coeff[i_min:i_max+1]


    min_ozone = np.min(absorption_coeff[:,0])
    max_ozone = np.max(absorption_coeff[:,0])
    i_min_ozone = np.abs(irradiance_spectrum[:,0] - min_ozone).argmin()
    i_max_ozone = np.abs(irradiance_spectrum[:,0] - max_ozone).argmin()
    new_irradiance_spectrum = np.copy(irradiance_spectrum[i_min_ozone+1:i_max_ozone+1])

    ozone_transmission_spectrum = generate_gas_transmission_spectrum(DU, absorption_coeff, zenith_angle=zenith_angle)

    f_interp_ozone = sp.interpolate.interp1d(ozone_transmission_spectrum[:,0], ozone_transmission_spectrum[:,1])
    ozone_interp = np.zeros(np.shape(irradiance_spectrum[i_min_ozone+1:]))
    ozone_interp[:,0] = irradiance_spectrum[i_min_ozone+1:,0]
    ozone_interp[:,1] = f_interp_ozone(irradiance_spectrum[i_min_ozone+1:,0])
    ozone_attenuated = np.copy(irradiance_spectrum[i_min_ozone+1:])
    ozone_attenuated[:,1] = irradiance_spectrum[i_min_ozone+1:,1]*ozone_interp[:,1]
    # diff = np.copy(ozone_attenuated)
    # diff[:,1] = ozone_attenuated[:,1] - irradiance_spectrum[i_min_ozone+1:,1]
    return ozone_attenuated

def get_ozone_correction_factor(ozone_attenuated_am0, ref_spectrum=None, qe=None, interpolation_method='QE'):
    if isinstance(qe, list) ==False:
        qe = [qe]

    if ref_spectrum is None:
        ref_spectrum = pc.AM0_2019
    else:
        ref_spectrum= ref_spectrum

    ozone_correction_factor = []
    for q in qe:
        ref_jsc = get_jsc_from_quantum_efficiency(q, ref_spectrum, interpolation_method)
        ozone_ref_jsc = get_jsc_from_quantum_efficiency(q, ozone_attenuated_am0, interpolation_method)
        correction = (ref_jsc/ozone_ref_jsc)
        ozone_correction_factor.append(correction)

    if len(ozone_correction_factor) ==1:
        ozone_correction_factor = ozone_correction_factor[0]
    return ozone_correction_factor

def correct_current_for_ozone(current, ozone_correction_factor):
    ozone_corrected_current = current*ozone_correction_factor
    return ozone_corrected_current

def generate_ozone_transmission_spectrum(ozone_DU, zenith_angle=0):
    ozone_molecules_cm2 = ozone_DU * 2.69e16
    ozone_transmission = np.zeros(c_Se.ozone_absorption_coefficients.shape)
    ozone_transmission[:,0] = c_Se.ozone_absorption_coefficients[:,0]
    ozone_transmission[:,1] = np.exp(-c_Se.ozone_absorption_coefficients[:, 1] * (ozone_molecules_cm2 / np.cos(np.deg2rad(zenith_angle))))
    return ozone_transmission

def generate_gas_transmission_spectrum(DU, abs_coeff, zenith_angle=0):
    molecules_cm2 = DU * 2.69e16
    ozone_transmission = np.copy(abs_coeff)
    ozone_transmission[:,1] = np.exp(-abs_coeff[:, 1] * (molecules_cm2 / np.cos(np.deg2rad(zenith_angle))))
    return ozone_transmission

def filterCorrection(dataSpectrum, transmissionSpectraofFilter):
    """
    Corrects a spectrum by a given transmission spectrum. Interpolates the transmission spectrum to the same units
    as the dataSpectrum then the dataSpectrum is passed through the transmission spectrum given a spectrum corrected for
    a transmission spectrum of a filter

    Args:
        dataSpectrum (2-D array): The spectrum to be corrected by the filter
        transmissionSpectraofFilter (2-D array): Transmission spectra of a filter

    Returns:
        2-D array of a dataSpectrum corrected for the transmission spectrum of filter

    """
    # if (len(dataSpectrum[:,0]) > (len(transmissionSpectraofFilter))):
    #     dataSpectrum = interpolate_larger_data_to_smaller_data(dataSpectrum, transmissionSpectraofFilter)
    # else:
    #     transmissionSpectraofFilter = interpolate_larger_data_to_smaller_data(transmissionSpectraofFilter, dataSpectrum)
    correctedSpectrum = np.zeros(np.shape(dataSpectrum))
    correctedSpectrum[:, 0] = np.copy(dataSpectrum[:, 0])
    f = sp.interpolate.interp1d(transmissionSpectraofFilter[:, 0], transmissionSpectraofFilter[:, 1], kind='linear')
    interpolatedFilterSpectrum = f(dataSpectrum[:, 0]) / 100
    correctedSpectrum[:, 1] = dataSpectrum[:, 1] / interpolatedFilterSpectrum
    return correctedSpectrum


def get_temperature_coefficient(parameter, temperatures):
    slope, intercept, r_value, p_value, std_err = stats.linregress(temperatures, parameter)
    fits = {'slope':slope, 'intercept':intercept, 'r_value':r_value, 'p_value':p_value, 'std_err':std_err}
    return fits


### STS Spectrometer Functions

def calibrationCorrection(dataSpectrum, lampSpectrum, standardLampSpectrum, units = 'photon flux vs nm'):
    """
    Takes a given spectrum, such as an luminescence spectrum, and corrects it using a standard lamp spectrum.

    Args:
        dataSpectrum (2-D array): the spectrum to be corrected
        lampSpectrum (2-D array): the spectrum of a lamp taken with the spectrometer to be calibrated
        standardLampSpectrum (2-D array): the known/calibrated spectrum of the lamp used, i.e. NIST Calibration
        units (2-D array): what units you wish to convert the instrument response to: 'irradiance vs nm', 'photon flux vs nm'

    Returns:
        2-D array of dataSpectrum that has been corrected for a standard lamp spectrum
    """
    instrumentResponse = _instrumentResponseFunction(lampSpectrum, standardLampSpectrum, units)
    spectrumcorrectedforCalibration = _correctforInstrumentResponse(dataSpectrum, instrumentResponse)
    spectrumcorrectedforCalibration[np.isinf(spectrumcorrectedforCalibration[:,1]),1] = 0
    return spectrumcorrectedforCalibration

def _instrumentResponseFunction(lampSpectrum, standardLampSpectrum, units):
    """

    Args:
        lampSpectrum (2-D array): spectrum of lamp in counts or whatever units the spectrometer took the data in
        standardLampSpectrum (2-D array): a standard lamp spectrum of know absolute units, i.e. NIST calibrated lamp
        units: what units you wish to convert the instrument response to: 'irradiance vs nm', 'photon flux vs nm'

    Returns:
        2-D array of instrument response in units/counts

    """
    instrumentResponse = np.zeros(np.shape(lampSpectrum))
    instrumentResponse[:,0] = lampSpectrum[:, 0]

    if units == 'irradiance vs nm':
        interpolatedIrradianceofStandardLampSpectrum = irradianceSpectrum(standardLampSpectrum).interpolate_irradiance_spectrum_to_data(lampSpectrum)
        instrumentResponse[:, 1] = interpolatedIrradianceofStandardLampSpectrum[:,1] / lampSpectrum[:, 1]
        return instrumentResponse

    elif units in ('photon flux vs nm'):
        interpolatedPhotonFluxofStandardLampSpectrum = irradianceSpectrum(standardLampSpectrum).interpolate_photon_flux_spectrum_to_data(lampSpectrum)
        # lampSpectrum[lampSpectrum[:, 1] < 1e-10] = 0
        fixedLampSpectrum = lampSpectrum[:, 1]
        fixedLampSpectrum[fixedLampSpectrum[:]<1e-10]=0
        # instrumentResponse[:,1] = interpolatedPhotonFluxofStandardLampSpectrum[:,1] /fixedLampSpectrum# lampSpectrum[:,1]
        instrumentResponse[:,1] = np.divide(interpolatedPhotonFluxofStandardLampSpectrum[:,1], fixedLampSpectrum, out=np.zeros_like(interpolatedPhotonFluxofStandardLampSpectrum[:,1]), where = fixedLampSpectrum!=0)#
        # lampSpectrum[:,1]


        return instrumentResponse

    else:
        print('Fail')
        print(instrumentResponse)

    # elif units == 'irradiance vs eV':
    # elif units == 'photon flux vs eV':

def _correctforInstrumentResponse(dataSpectrum, instrumentResponse):
    """
    instrumentResponse must be same dimension as dataSpectrum

    Args:
        dataSpectrum (2-D array): data to be corrected by instrument response
        instrumentResponse(2-D array: the instrument response to a standard lamp spectrum

    Returns:
        2-D array of dataSpectrum corrected for instrument response

    """
    # instrumentResponseInterpolated = sp.interpolate.interp1d(instrumentResponse[:,0], instrumentResponse[:, 1], kind='linear')
    # instrumentResponseInterpolatedYNEW = instrumentResponseInterpolated(dataSpectrum[:,0])
    correctedforInstrumentResponse = np.zeros(np.shape(dataSpectrum))
    correctedforInstrumentResponse[:, 0] = dataSpectrum[:, 0]
    correctedforInstrumentResponse[:, 1] = dataSpectrum[:, 1] * instrumentResponse[:,1]
    return correctedforInstrumentResponse

###### Sun Sensor Equations

def yaw_from_sun_sensor(TL, BL, BR, TR, r, h):
    pre_apereture = ((TL+BL)-(TR+BR))/(TL+BL+BR+TR)
    yaw = np.rad2deg(np.arctan(pre_apereture*(r/h)))
    return yaw

def pitch_from_sun_sensor(TL, BL, BR, TR, r, h):
    pre_apereture = ((TL+TR)-(BL+BR))/(TL+BL+BR+TR)
    pitch = np.rad2deg(np.arctan(pre_apereture*(r/h)))
    return pitch

def correct_angle_coefficients(angle, coefficents):
    p = np.poly1d(coefficents)
    return p(angle)

def get_coeffecients(measured_angle, real_angle):
    p = np.polyfit(measured_angle, real_angle, deg=3, full=False)
    return p

### QE Data Tools

def get_jsc_from_quantum_efficiency(quantum_efficiency, irradiance_spectrum, interpolation_method='QE'):

    """
    Calculates the short circuit current from an give quantum efficiency curve and irradiance spectrum

    Args:
        quantum_efficiency (ndarray): 2D array of Quantum Efficiency data of shape x = wavelength, y = quantum efficiency (%)
        irradiance_spectrum (ndarray): 2D array that has x = nm, y = W/cm^2/nm
        interpolation_method (ndarray): 'QE' interpolates the irradiance spectrum to the QE spacing whereas 'Irr' interpolates the quantum efficiency spectrum to the irradiance spectrum

    Returns:
        Integrated current in mA/cm^2

    """

    irradianceSpectrum_object = irradianceSpectrum(irradiance_spectrum)

    if interpolation_method == 'QE':
        photonFluxSpectrum_interpolated_to_quantumEfficiency = irradianceSpectrum_object.interpolate_photon_flux_spectrum_to_data(quantum_efficiency)
        quantumEfficiecy_x_photonFluxSpectrum = (quantum_efficiency[:, 1] / 100) * photonFluxSpectrum_interpolated_to_quantumEfficiency[:, 1] * c.e * 0.1 #c.e and 0.1 are used to convert irradianceSpectrum to ma/cm^2
        JscFromIntegration = sp.integrate.trapz(quantumEfficiecy_x_photonFluxSpectrum, quantum_efficiency[:, 0])

    elif interpolation_method == 'Irr':
        quantum_efficiency_intorpolated_to_irradiance_spectrum = interpolate_larger_data_to_smaller_data(irradianceSpectrum_object.photonFluxSpectrumINnm(), quantum_efficiency)
        photonFluxSpectrum_interpolated_to_quantumEfficiency = irradianceSpectrum_object.interpolate_photon_flux_spectrum_to_data(quantum_efficiency_intorpolated_to_irradiance_spectrum)
        quantumEfficiecy_x_photonFluxSpectrum = (quantum_efficiency_intorpolated_to_irradiance_spectrum[:, 1] / 100) * photonFluxSpectrum_interpolated_to_quantumEfficiency[:, 1] * c.e * 0.1 #c.e and 0.1 are used to convert irradianceSpectrum to ma/cm^2
        JscFromIntegration = sp.integrate.trapz(quantumEfficiecy_x_photonFluxSpectrum, quantum_efficiency_intorpolated_to_irradiance_spectrum[:, 0])

    return JscFromIntegration #mA/cm^2

def get_jsc_from_spectral_response(spectral_response, irradiance_spectrum, interpolation_method='SR'):
    """
    Calculates the short circuit current density using give spectral response spectrum and irradiance spectrum

    Args:
        spectral_response (ndarray): spectral response data is x = nm and y = A/cm^2
        irradiance_spectrum (ndarray: 2D array that has x = nm, y = W/cm^2/nm
        interpolation_method (ndarray): 'SR' interpolates the irradiance spectrum to the spectral response spacing whereas 'Irr' interpolates the spectral response spectrum to the irradiance spectrum

    Returns:
        a single value that is in the units of mA/cm^2
    """

    irradianceSpectrum_object = irradianceSpectrum(irradiance_spectrum)

    if interpolation_method == 'SR':
        irradianceSpectrum_interpolated_to_spectralResponse = irradianceSpectrum_object.interpolate_irradiance_spectrum_to_data(spectral_response)
        spectral_response_x_irradiance_spectrum = spectral_response[:, 1] * irradianceSpectrum_interpolated_to_spectralResponse[:, 1]
        JscFromIntegration = sp.integrate.trapz(spectral_response_x_irradiance_spectrum, spectral_response[:, 0]) * 0.1 #0.1 converts to mA/cm^2

    if interpolation_method == 'Irr':
        spectral_response_interpolated_to_irradiance_spectrum = interpolate_larger_data_to_smaller_data(irradiance_spectrum, spectral_response)
        irradianceSpectrum_interpolated_to_spectralResponse = irradianceSpectrum_object.interpolate_irradiance_spectrum_to_data(spectral_response_interpolated_to_irradiance_spectrum)
        spectral_response_x_irradiance_spectrum = spectral_response_interpolated_to_irradiance_spectrum[:, 1] * irradianceSpectrum_interpolated_to_spectralResponse[:, 1]
        JscFromIntegration = sp.integrate.trapz(spectral_response_x_irradiance_spectrum, spectral_response_interpolated_to_irradiance_spectrum[:, 0]) * 0.1  # 0.1 converts to mA/cm^2

    return JscFromIntegration

def interpolate_larger_data_to_smaller_data(large_data, small_data):
    min_x = np.min(small_data[:,0])
    max_x = np.max(small_data[:,0])

    i_min = np.argmin(np.abs(min_x-large_data[:,0]))
    i_max = np.argmin(np.abs(max_x-large_data[:,0]))

    if large_data[i_min,0] < min_x:
        i_min = i_min + 1

    if large_data[i_max,0] > max_x:
        i_max = i_max - 1

    x_new = large_data[i_min:i_max,0]
    # intp_func = sp.interpolate.interp1d(small_data[:,0], small_data[:,1])
    # y_new = intp_func(x_new)
    y_new = np.interp(x_new, small_data[:,0], small_data[:,1])

    interpolated_large_data = np.zeros((len(x_new),2))
    interpolated_large_data[:,0] = x_new
    interpolated_large_data[:,1] = y_new

    return interpolated_large_data

def average_qe_spectra(qe_spectra = []):
    """

    Args:
        qe_spectra: list of 2d data

    Returns:

    """
    wavelengths = []
    for qe in qe_spectra:
        wavelengths = wavelengths+list(qe[:,0])
    wavelengths = list(np.unique(np.array(wavelengths)))
    avg_at_all_wavelengths = []
    for nm in wavelengths:
        avg_at_nm = []
        for qe in qe_spectra:
            if nm in qe[:,0]:
                index = np.argwhere(qe[:,0]==nm)
                avg_at_nm.append(qe[index,1])
        avg_at_all_wavelengths.append(np.mean(avg_at_nm))
    avg_at_all_wavelengths = np.array(avg_at_all_wavelengths)
    avg_spectra = np.vstack((wavelengths, avg_at_all_wavelengths)).T
    return avg_spectra

def sortTwoArrays(sortByThisArray, arrayToBeSorted):
    zippedValues = zip(sortByThisArray, arrayToBeSorted)
    zippedValues = sorted(zippedValues, key=itemgetter(0))
    # zippedValues.sort(key=itemgetter(0)) #python 2.7 way
    sortedArray1, sortedArray2 = zip(*zippedValues)
    return np.array(sortedArray1), np.array(sortedArray2)

def findIndicesofDuplicates(list = []):
    indices = []
    noDuplicateList = set(list)
    for item in noDuplicateList:
        indicesOfDuplicates = []
        for index, itemDuplicate in enumerate(list):
            if item == itemDuplicate:
                indicesOfDuplicates.append(index)
        indices.append(indicesOfDuplicates)
    return indices

### Analyzing log files

def concatDirectoryFiles(dirName):

    directory = os.path.join(os.getcwd(), dirName)

    df = pd.DataFrame()

    for subdir, dirs, files in os.walk(directory):

        for filename in files:
            # df = df.append(pd.read_csv(os.path.join(dirName,filename), sep='\t', index_col=False, header=0), ignore_index=True)
            df = pd.concat([df, pd.read_csv(os.path.join(dirName,filename), sep='\t', index_col=False, header=0)], ignore_index=True)

    return df

def high_freq_data_df(selenium_flight_data_folder_path, start_time=None):
    # LivSeDataContainer.__init__(self)
    folders = os.listdir(selenium_flight_data_folder_path)

    df_raw = concatDirectoryFiles(selenium_flight_data_folder_path)
    df_raw['datetime'] = df_raw['GPS Date'] + " " + df_raw['GPS Time']
    df_raw['UTC'] = pd.to_datetime(df_raw['Timestamp'], unit='s', utc=True)
    df_raw = df_raw.set_index(df_raw['UTC'])

    if os.path.exists(os.path.join(os.path.dirname(selenium_flight_data_folder_path), 'TEL')):
        telem_raw = concatDirectoryFiles(os.path.join(os.path.dirname(selenium_flight_data_folder_path), 'TEL'))
        telem_raw['datetime'] = telem_raw['GPS Date'] + " " + telem_raw['GPS Time']
        telem_raw['UTC'] = pd.to_datetime(telem_raw['UTC'],unit='s', utc=True)
        telem_raw = telem_raw.set_index(telem_raw['UTC'])

        df =  pd.merge(df_raw, telem_raw[['MS56 Pressure(Pa)']], left_index=True, right_index=True, how='outer')
        df['MS56 Pressure(Pa)'] = df['MS56 Pressure(Pa)'].interpolate()
        df = df.dropna(subset=['UTC'])

    else:
        df = df_raw

    if start_time != None:
        utc_time = pytz.utc.localize(dateutil.parser.parse(start_time))
        start_time_utc_seconds = datetime.timestamp(utc_time)

        df = df.set_index(df.index + pd.DateOffset(seconds=start_time_utc_seconds))

    if "Altitude(m)" in df.columns:
        df = df.rename(columns={"Altitude(m)":"Altitude (m)"})
    return df

def correct_datetime_index_if_gps_data_was_intermittent(dataframe):
    utc_df = pd.to_datetime(dataframe.index.asi8/1e9, unit='s')
    # utc_df = pd.to_datetime(utc_timestamps_seconds, unit='s')
    min_gps_time = utc_df[utc_df.year>2000].min() #looking for lower end of gps time
    max_gps_time = utc_df[utc_df.year>2000].max() #looking for upper end of gps time
    i_min = utc_df.get_loc(min_gps_time)
    i_max = utc_df.get_loc(max_gps_time)+1
    utc_df_min = utc_df[:i_min] + pd.DateOffset(seconds = min_gps_time.timestamp() - utc_df[:i_min].max().timestamp()-2)
    utc_df_max = utc_df[i_max:] + pd.DateOffset(seconds = max_gps_time.timestamp())
    utc_below_current_time = utc_df[utc_df.year>2000]
    new_utc_timestamps = pd.concat([pd.Series(utc_df_min), pd.Series(utc_below_current_time), pd.Series(utc_df_max)])
    dataframe = dataframe.set_index(new_utc_timestamps)
    return dataframe

def standardize_selenium_dataframe(dataframe):
    """
    Finds column names that may be labeled funny or similar from past naming conventions and standardizes them to a common naming convention

    Args:
        dataframe (pd.DataFrame): Pandas dataframe containing selenium data

    Returns:
        dataframe (pd.DataFrame): Pandas dataframe containing selenium data with standardized column names
    """
    for column_name in dataframe.columns:
        if column_name in ['MS56 Pressure(Pa)', 'Pressure (Pa)']:
            dataframe['Pressure'] = dataframe[column_name]

    return dataframe

def get_temperature_coefficient_Huber(parameter, temperatures):
    """
    Fits a HuberRegressor to the data and returns the slope, intercept, score, and r_value.  The slope is the temperature coefficient

    Args:
        parameter (np.ndarray): any solar parameter (e.g. Jsc, Voc, FF, PCE)
        temperatures (np.ndarray): temperature data

    Returns:
        fits (dict): dictionary containing the slope, intercept, score, and r_value of the fit where the slope is the temperature coefficient
    """
    fits = dict.fromkeys(['slope', 'intercept', 'score', 'r_value'])
    huber_jsc = HuberRegressor(epsilon=1.1)
    huber_jsc.fit(temperatures.reshape(-1, 1), parameter)
    fits['slope'] = huber_jsc.coef_
    fits['intercept'] = huber_jsc.intercept_
    fits['score'] = huber_jsc.score(temperatures.reshape(-1, 1), parameter)
    fits['r_value'] = pearl.analyzeGoodnessOfFit(parameter, fits['slope']*temperatures +fits['intercept']).r2
    return fits

