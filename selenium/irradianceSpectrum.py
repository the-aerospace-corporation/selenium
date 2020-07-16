import numpy as np
import scipy as sp
from scipy import interpolate
from scipy import constants as c
# Takes a given irradiance spectrum in W/cm^2/nm then transforms the data in a variety of ways using the included methods.

class irradianceSpectrum:
    def __init__(self, irradianceSpectrum):
        self.irradianceSpectrum = irradianceSpectrum

    #Interplates giving irradiance spectrum for user defined spacing
    def irradianceSpectrum_interpolated(self, spacing=None):
        if spacing is None:
            spacing = 1  #Default Interpolation (1nm)
        intp_data = sp.interpolate.interp1d(self.irradianceSpectrum[:, 0], self.irradianceSpectrum[:, 1], kind='linear')
        xnew = np.arange(np.ceil(self.irradianceSpectrum[0, 0]), np.floor(self.irradianceSpectrum[-1, 0]), spacing)
        ynew = intp_data(xnew)
        AM_interpolated = np.zeros((len(xnew),2))
        AM_interpolated[:,0] = xnew
        AM_interpolated[:,1] = ynew
        return AM_interpolated

    #Returns the irradiance spectrum in units x = eV, y = W/cm^-2/nm
    def photonFluxSpectrumINnm(self):
        AM_Flux = np.zeros((self.irradianceSpectrum.shape))
        AM_Flux[:,0] = self.irradianceSpectrum[:, 0]
        AM_Flux[:,1] = (self.irradianceSpectrum[:, 1] / ((c.h * c.c) / (self.irradianceSpectrum[:, 0] * 1e-9)))
        return AM_Flux

    #Returns the irradiance spectrum in units x = eV, y = W/cm^-2/nm with a user defined interpolation.
    #Function first interpolates over nm then gives the respective units in eV.
    #May need to change this interpolate over eV or add a specific function that does that
    def photonFluxSpectrumINnm_interpolated(self, spacing=None):
        if spacing is None:
            spacing = 1  #Default Interpolation (1nm)
        AINT = self.irradianceSpectrum_interpolated(spacing)
        AM_Flux_INTP = np.zeros((AINT.shape))
        AM_Flux_INTP[:,0] = AINT[:,0]
        AM_Flux_INTP[:,1] = (AINT[:,1]/((c.h*c.c)/(AINT[:,0]*1e-9)))
        return AM_Flux_INTP

    #Returns the irradiance spectrum in units x = eV, y = photons/m^2
    def photonFluxSpectrumINeV(self):
        photoFluxSpectrumINeV = np.zeros((self.irradianceSpectrum.shape))
        photoFluxSpectrumINeV[:,0] = ((c.h/c.e)*c.c)/(self.irradianceSpectrum[:, 0] * 1e-9)
        photoFluxSpectrumINeV[:,1] = (self.irradianceSpectrum[:, 1] * 1e9 * (((self.irradianceSpectrum[:, 0] * 1e-9) ** 2) / ((c.h / c.e) * c.c))) / ((c.h * c.c) / (self.irradianceSpectrum[:, 0] * 1e-9))
        return photoFluxSpectrumINeV

    def photonFluxSpectrumINeV_interpolated(self, spacing=None):
        if spacing is None:
            spacing = 0.01  #Default Interpolation (1nm)
        photonFluxSpectrumINeV = self.photonFluxSpectrumINeV()[::-1]
        intp_data = sp.interpolate.interp1d(photonFluxSpectrumINeV[:, 0], photonFluxSpectrumINeV[:,1], kind='linear')
        xnew = np.arange(np.ceil(photonFluxSpectrumINeV[0, 0]*100)/100, np.floor(photonFluxSpectrumINeV[-1, 0]*100)/100, spacing)
        ynew = intp_data(xnew)
        photonFluxSpectrumINeV_interpolated = np.zeros((len(xnew),2))
        photonFluxSpectrumINeV_interpolated[:,0] = xnew[::-1]
        photonFluxSpectrumINeV_interpolated[:,1] = ynew[::-1]

        return photonFluxSpectrumINeV_interpolated

    #Takes a given data spectrum, such as quantum efficiency or transmission and interpolates the irradiance spectrum to have the same units as the data spectrum
    #Useful for getting irradiance spectrum in same units as any given spectrum
    #Units of x values must be in nm
    def interpolate_irradiance_spectrum_to_data(self, data_spectrum):
        intp_data = sp.interpolate.interp1d(self.irradianceSpectrum[:, 0], self.irradianceSpectrum[:, 1], kind='linear')
        xnew = data_spectrum[:, 0]
        ynew = intp_data(xnew)
        irradiance_spectrum_interpolated_to_data = np.zeros((len(xnew),2))
        irradiance_spectrum_interpolated_to_data[:,0] = xnew
        irradiance_spectrum_interpolated_to_data[:,1] = ynew
        return irradiance_spectrum_interpolated_to_data

    #Takes a given spectrum, such as quantum efficiency or transmission and interpolates the irradiance spectrum to have the same units as spectrum
    #Converts the spectrum to x = nm, y = photons/cm^2
    #Useful for getting irradiance spectrum in same units as any given spectrum
    #Units of x values must be in nm
    def interpolate_photon_flux_spectrum_to_data(self, data_spectrum):
        irradiance_spectrum_interpolated_to_data = self.interpolate_irradiance_spectrum_to_data(data_spectrum)
        irradiance_spectrum_interpolated_to_data_photon_flux = np.zeros((irradiance_spectrum_interpolated_to_data.shape))
        irradiance_spectrum_interpolated_to_data_photon_flux[:,0] = irradiance_spectrum_interpolated_to_data[:,0]
        irradiance_spectrum_interpolated_to_data_photon_flux[:,1] = (irradiance_spectrum_interpolated_to_data[:,1]/((c.h*c.c)/(irradiance_spectrum_interpolated_to_data[:,0]*1e-9)))
        return irradiance_spectrum_interpolated_to_data_photon_flux

    #this is useless
    # #Takes a given spectrum, such as quantum efficiency or transmission and interpolates the spectrum to have the same units as the irradiance spectrum
    # #Useful for getting quantum efficiency spectrum in same units as any given irradiance spectrum
    # #Units of x values must be in nm
    # def interpolate_data_to_irradiance_spectrum(self, spectrum):
    #     intp_data = sp.interpolate.interp1d(spectrum[:, 0], spectrum[:, 1], kind='linear')
    #     xnew = self.irradianceSpectrum[:, 0]
    #     ynew = intp_data(xnew)
    #     interpolated_spectrum = np.zeros((len(xnew),2))
    #     interpolated_spectrum[:,0] = xnew
    #     interpolated_spectrum[:,1] = ynew
    #     return interpolated_spectrum
    #
    # #Takes a given spectrum, such as quantum efficiency or transmission and interpolates the spectrum to have the same units as irradiance spectrum
    # #Converts the spectrum to x = nm, y = photons/cm^2
    # #Useful for getting irradiance spectrum in same units as any given spectrum
    # #Units of x values must be in nm
    # def interpolate_data_to_photon_flux_spectrum(self, spectrum):
    #     interpolated_spectrum = self.interpolate_data_to_irradiance_spectrum(spectrum)
    #     interpolated_spectrum_photon_flux = np.zeros((interpolated_spectrum.shape))
    #     interpolated_spectrum_photon_flux[:,0] = interpolated_spectrum[:,0]
    #     interpolated_spectrum_photon_flux[:,1] = (interpolated_spectrum[:,1]/((c.h*c.c)/(interpolated_spectrum[:,0]*1e-9)))
    #     return interpolated_spectrum_photon_flux
