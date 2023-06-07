class AMUDataContainer(object):
    def __init__(self):
        self.address = []  #: address of AMU
        self.manufacturer = []  #: company that makes the solar cells
        self.model = []  #: solar cell model or technology
        self.cell_id = []  #: solar cell identification number or serial number
        self.junction = []  #: numerical junction of the solar cell with index starting at 0
        self.tech = []  #: technology of solarcell. MJ, Isotype, Si, Perovskite, etc.
        self.coverglass = []  #: if 0 there is no coverglass else the number corresponds to the thickness
        self.fluence = []  #: fluence of radiation particle (particles/cm2) if cell was irradiated
        self.energy = []  #: energy of radiation particle (MeV) if the solar cell was irradiated
        self.firmware_version = []  #: firmware of amu used
        self.serial = []  #: serial number of device
        self.sweep_config = []  #: sweep configuration of device
        self.voltage_settings = []  #: voltage pga settings
        self.current_settings = []  #: current pga settings
        self.gain_correction = []  #: gain settings correction
        self.yaw_coeff = []  #: polynomial yaw coefficients
        self.pitch_coeff = []  #: polynomial pitch coefficients
        self.hval = []  #: hval for angle calculations
        self.rval = []  #: rval for angle calculations
        self.amu_number = []  #: AMU number corresponding this device.  this number is correlated with the ISC and VOC high frequency data

