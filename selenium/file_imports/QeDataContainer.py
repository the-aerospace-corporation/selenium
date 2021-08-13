class QeDataContainer(object):
    """
    Data containter for QE files. Typical use includes this class to be inherited by other classes. Its a way to easily add attributes to any class that has inhertied this. Allows for easy management of new and old features that have exist with pearl data files over time, past, present and future
    """

    def __init__(self):
        self.qeData = []  #: all data from QE measurement
        self.file_name = []  #: file name
        self.model = []  #: solar cell model or technology
        self.cell_id = []  #: solar cell identification number or serial number
        self.measurement = []  #: QE (Quantum Efficiency)
        self.manufacturer = []  #: company that makes the solar cells
        self.datetime = []  #: datetime object combining date and time fields
        self.date = []  #: date data was taken in
        self.time = []  #: time data was taken
        self.notes = []  #: notes taken during measurment
        self.grating_type = []  #: grating used during measurement
        self.spare = []  #: not sure what this is, ask John Nocerino
        self.start_wavelength = []  #: wavelength where measurement was started
        self.stop_wavelength = []  #: wavelength where measurement was stopped
        self.wavelength_step = []  #: steps in nm
        self.cal_detector_file_name = []  #: calibration file of detector used to calibrate the QE system
        self.sys_cal_file_name = []  #: calibration file used to calibration QE for this measurement
        self.grating_lines_l_per_mm = []  #: lines per mm of the grating used
        self.slit_width_mm = []  #: slit width setting during measurement
        self.datapoints = []  #: number of datapoints taken
        self.junction = []  #: numerical junction of the solar cell with index starting at 0
        self.jsc = []  #: short circuit current density (mA/cm2). Current density at 0 volt (from file header)
        self.fluence = []  #: fluence of radiation particle (particles/cm2) if cell was irradiated
        self.energy = []  #: energy of radiation particle (MeV) if the solar cell was irradiated
        self.particle = []  #: partice type p for protons and e for electrons if solar cell was irradiated
        self.cell_temp = [] #: temperature of cell
        self.room_temp = [] #: room temperature when cell was measured
        self.cell_area_cm2 = [] #: area of cell in cm2
        self.relative_humidity = [] #: relative humidity during measurement
        self.energy = [] #: energy of partice used to irradiate cell
        self.fluence = [] #: fluence of particles from radiation
        self.dut_temp = []  #: temperature (C) of the sample plane when measurement was taken. This should be exactly the temperature of the cell
        self.aux_temp = []  #: temperature (C) of the external temperature sensor
        self.wavelength_nm = []  #: array of wavelength (nm) from the QE measurement
        self.quantum_efficiency = []  #: array quantum efficiency (percent)
        self.qee = []
        self.spectral_response = []  #: array quantum efficiency (A/W)
        self.sr = []
        self.system_calibration = []  #: array of syscal values I believe this is in Amps (A/W)
        self.syscal_w = []
        self.cell_current = []  #: current of solar cell as measured by lock-in amplifier during QE test
        self.cell_current_a = []
        self.reference_cell_current = []  #: current of reference photodiode as measured by lock-in amplifier during QE test
        self.ref_cell_current_a = []
