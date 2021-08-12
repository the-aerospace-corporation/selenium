import numpy as np
import matplotlib.pyplot as plt
import os

from selenium import selenium_analysis as sa
from .QeDataContainer import QeDataContainer
import selenium.solar_spectra as solar_spectra
import dateutil

class getQEsinglePEARLfileOrganized(QeDataContainer):
    """
    Opens and parses and single LIV file from Pearl Lab.  All parameters are pulled from the measurement and
    placed in the heard of the file, which are then broken into object attributes

    Args:
        qe_file_path (txt): Pearl data file from the light IV station.
    """
    
    def __init__(self, qe_file_path, irradiance_spectrum=None, interpolation_method=None):
        QeDataContainer.__init__(self)
        self.file_name = os.path.basename(qe_file_path)

        with open(qe_file_path, 'rU') as f:
            data = []
            for j in f:
                m = j.split('\t')

                if ('Jsc (A/cm^2)' in m) or ('Jsc_calc (A/cm^2)' in m):
                    self.jsc = (float(m[0+1]))

                elif ('date' in m):
                    self.date = m[0 + 1]

                elif ('cell area (cm^2)' in m):
                    self.cell_area_cm2 = m[0+1]

                elif ('cell temp (C)' in m):
                    self.cell_temp = float(m[0+1])

                elif ('time' in m):
                    self.time = m[0 + 1]

                elif ('notes' in m):
                    self.notes = m[0 + 1]

                elif ('grating type' in m):
                    self.grating_type = m[1]

                elif ('spare' in m):
                    self.spare = m[1]

                elif ('start wavelength' in m):
                    self.start_wavelength = (float(m[1]))

                elif ('stop wavelength' in m):
                    self.stop_wavelength = (float(m[1]))

                elif ('wavelength step' in m):
                    self.wavelength_step = (float(m[1]))

                elif ('cal detector file name' in m):
                    self.cal_detector_file_name = m[1]

                elif ('syscal file name' in m):
                    self.sys_cal_file_name = m[1]

                elif ('grating lines (l/mm)' in m):
                    self.grating_lines_l_per_mm = (float(m[1]))

                elif ('datapoints' in m):
                    self.datapoints = (float(m[1]))

                elif ('slit width (mm)' in m):
                    self.slit_width_mm = (float(m[1]))

                elif ('dut temp' in m):
                    self.dut_temp = (float(m[0+1]))

                elif ('aux temp' in m):
                    self.aux_temp = (float(m[0+1]))

                elif ('Irradiation (fluence,energy, particle)' in m):
                    self.fluence = (float(m[0+1]))
                    self.energy = (float(m[0+2]))
                    self.particle = m[3]

                elif ('fluence' in m):
                    self.fluence = float(m[0+1])

                elif ('energy' in m):
                    self.energy = float(m[0+1])

                elif ('particle' in m):
                    self.particle = m[1]

                elif any(terms in m for terms in ['Wavelength (nm)', 'Wavelength(nm)', 'WL(nm)']):
                    break

            for j in f:
                if j.strip():
                    m = j.split('\t')
                    if float(m[0])>0:
                        data.append([float(n) for n in m])
                    else:
                        f.close()
                        break
            self.qeData = np.array(data)

        if self.date and self.time:
            self.datetime = dateutil.parser.parse(self.date + ' ' + self.time)

        for i in range(np.shape(self.qeData)[1]):
            if i==0:
                self.wavelength_nm = self.qeData[:,0]
            elif i==1:
                self.qee = self.qeData[:,1]
                self.quantum_efficiency = self.qeData[:, [0, 1]]
            elif i == 2:
                self.sr = self.qeData[:,2]
                self.spectral_response = self.qeData[:, [0, 2]]
            elif i == 3:
                self.syscal_w = self.qeData[:,3]
                self.system_calibration = self.qeData[:, [0, 3]]
            elif i == 4:
                self.cell_current_a = self.qeData[:,4]
                self.cell_current = self.qeData[:, [0, 4]]
            elif i == 5:
                self.ref_cell_current_a = self.qeData[:,5]
                self.reference_cell_current = self.qeData[:, [0, 5]]

        if not self.fluence:
            self.fluence = 0

        if self.particle:
            if self.particle.rstrip("\n\r") in ['p+', 'P', 'P+' ,'proton', 'Proton']:
                self.particle = 'p'

            elif self.particle.rstrip("\n\r") in ['e-', 'E', 'E+', 'electron', 'Electron']:
                self.particle = 'e'

        if not self.jsc:
            self.jsc = self.jsc_quantum_efficiency(solar_spectra.AM0, interpolation_method='QE')

    def jsc_quantum_efficiency(self, irradiance_spectrum, interpolation_method='QE'):
        """

        Args:
            irradiance_spectrum (2D ndarray): Should be 2D xy data (nm vs W/m^2)
            interpolation_method (str): 'QE' interpolates the irradiance spectrum to the QE spacing whereas 'Irr' interpolates the quantum efficiency spectrum to the irradiance spectrum

        Returns:
            Short circuit current in mA/cm^2

        """
        return sa.get_jsc_from_quantum_efficiency(self.quantum_efficiency, irradiance_spectrum, interpolation_method=interpolation_method)

    def jsc_spectral_response(self, irradiance_spectrum):
        """
        Calculates short circuit current from the user defined irradiation spectrum and the spectral response of the solar cell
        
        Args:
            irradiance_spectrum (2D ndarray): Shoud be 2D xy data (nm vs W/m^2)

        Returns:
            Short circuit current in mA/cm^2
        """
        return sa.get_jsc_from_spectral_response(self.spectral_response, irradiance_spectrum)

    def plotQE(self, color='blue'):
        """
        Quick plot check of QE if needed
        """
        plt.plot(self.quantum_efficiency[:, 0], self.quantum_efficiency[:, 1], lw = 1, color=color, label = self.file_name)
