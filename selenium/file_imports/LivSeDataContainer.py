import pandas as pd
import numpy as np
class LivSeDataContainer(object):
    """
    Data containter for LIV files. Typical use includes this class to be inherited by other classes. Its a way to easily add attributes to any class that has inhertied this. Allows for easy management of new and old features that have exist with pearl data files over time, past, present and future
    """
    def __init__(self):
        self.file_name = []  #: filename
        self.notes = []  #: notes taken during measurement
        self.manufacturer = []  #: company that makes the solar cells
        self.model = []  #: solar cell model or technology
        self.cell_id = []  #: solar cell identification number or serial number
        self.cell_name = [] #: manufacturer + model + cell_id
        self.junction = []  #: numerical junction of the solar cell with index starting at 0
        self.coverglass = []  #: if 0 there is no coverglass else the number corresponds to the thickness
        self.fluence = []  #: fluence of radiation particle (particles/cm2) if cell was irradiated
        self.energy = []  #: energy of radiation particle (MeV) if the solar cell was irradiated
        self.data = []  #: all 2d data collected
        self.xy = []  #: all data from sweep
        self.voltage = []  #: array of voltages from the IV sweep
        self.current = []  #: array of currents from the IV sweep
        self.voc = []  #: measured open circuit voltage in Volts (from file header)
        self.jsc = []  #: short circuit current density (mA/cm2). Current density at 0 volt (from file header)
        self.vmax = []  #: voltage at maximum power point in Volts (from file header)
        self.isc = []  #: short circuit current (A). Current at 0 volt (from file header)
        self.jmp = []  #: short circuit current density (mA/cm2) at maximum power point. (from file header)
        self.imax = []  #: short circuit current (A) at maximum power point. (from file header)
        self.pmax = []  #: maximum power (W) (from file header)
        self.fill_factor = []  #: fill factor of cell. Typically between 79 and 86 for multijunction cells and lower for single junction
        self.efficiency = []  #: solar conversion efficieny of solar cell in percent. Essential power produced divided by power of sun. See Am0 constant used to know which solar spectrum was used
        self.cell_temperature_celsius = []  #: temperature (C) of the sample plane when measurement was taken. This should be exactly the temperature of the cell
        self.cell_temperature_kelvin = []  #: temperature (K) of the sample plane when measurement was taken. This should be exactly the temperature of the cell
        self.cell_area_cm_2 = []  #: area (cm2) of the solar cell. This value is inputed at the time of test. It is needed to generate current density and power density. Sometimes the user forgets but this can be added later and rerun to correct this
        self.am0_constant_w_cm = []  #: solar constant used for effeciency calculations.
        self.x_angle = []
        self.y_angle = []
        self.yaw = []
        self.pitch = []
        self.x_angle_pre = []  #: x (yaw) angle at the start of the light IV sweep
        self.y_angle_pre = []  #: y (pitch) angle at the start of the light IV sweep
        self.x_angle_post = []  #: x (yaw) angle at the end of the light IV sweep
        self.y_angle_post = []  #: y (pitch) angle at the end of the light IV sweep
        self.date = []
        self.time = []
        self.amu = []  #: AMU id?
        self.address = []  #: address of AMU
        self.firmware_version = []  #: firmware of amu used
        self.altitude = []  #:  Pressure Sensor temp, pressure, humidity, coversion of pressure to altitude
        self.altitude_from_pressure = []  #: altitude calculate from pressure
        self.timestamp = []  #:timestamp from onboard clock in microseconds
        self.utc = []  #: utc time from timestamp
        self.gps_date_time = []  #: data and time from gps as a text string
        self.gps_datetime_object = []  #: gps_date_time converted to python datetime object
        self.gps_datetime_object_timestamp = []  #:timestamp converted to datetime object (poorly named gps)
        self.latitude = []  #: latitude from gps that the data was collected at
        self.longitude = []  #: longitude from gps that the data was collected at
        self.gps_altitude = []  #: altitude collected from gps data
        self.gps_speed = []  #: speed collecte from gps data
        self.gps_number_of_satellites = []  #: number of satellites on lock for gps signle
        self.telemetry = []
        self.sweep_points = []
        self.internal_voltage_raw = []
        self.internal_voltage_conv = []
        self.adc_temperature_celsius = []  #: temperature from analouge to digital converter
        self.pressure = []  #: pressure data was taken in mBar.  Can be from BME or MS5607. Defaults to MS5607 as it can go to lower pressures from high altitudes
        self.BME280 = []  #: pressure from this sensor. Very common barometric pressure sensor
        self.MS5607 = []  #: pressure from this sensor that can go to lower pressures mBarr
        self.pre_angle = []  #: list of data from quad photodiode sun sensor and calculated angle at start of measurement
        self.post_angle = []  #: list of data from quad photodiode sun sensor and calculated angle at end of measurement
        self.dataframe = []  #: dataframe of all relevant values (might polish this up a bit

    def make_dataframe(self): #TODO: Move this to LIV data container and use it for the telem data...maybe make a dictionary mapping the column human readable names to attributes.
        dataframe_dict = {"jsc": "Jsc (A/cm2)",
                          "isc" : "Isc (A)",
                          "voc": "Voc (V)",
                          "imax" :"Imax (A)",
                          "vmax" : "Vmax (V)",
                          "pmax" : "Pmax (W)",
                          "fill_factor" : "FillFactor",
                          "efficiency" : "Efficiency (%)",
                          "x_angle_pre" : "x angle pre",
                          "y_angle_pre" : "y angle pre",
                          "x_angle_post" : "x angle post",
                          "y_angle_post" : "y angle post",
                          "yaw" : "YAW",
                          "pitch" : "PITCH",
                          "gps_altitude" : "Altitude (m)",
                          "pressure" : "Pressure",
                          "altitude_from_pressure" : "Altitude_from_Pressure (m)",
                          "latitude" : "Latitude",
                          "longitude" : "Longitude",
                          "cell_temperature_kelvin" : "Temperature (K)",
                          "cell_temperature_celsius" : "Temperature (C)",
                          "adc_temperature_celsius" : "ADC Temperature (C)",
                          "gps_datetime_object" : "Date Time"
                          }
        attributes = list(self.__dict__.keys())
        df = pd.DataFrame()

        for key in dataframe_dict:
            if key in attributes:
                if isinstance(getattr(self, key), np.ndarray):
                    if getattr(self, key).size != 0:
                        df[dataframe_dict[key]] = getattr(self, key)
                        if (key == 'gps_datetime_object'):
                            df = df.set_index(pd.to_datetime(getattr(self, 'gps_datetime_object'), utc=True))
                elif isinstance(getattr(self, key), list):
                    if any(getattr(self, key)):
                        df[dataframe_dict[key]] = getattr(self, key)
                    if (key == 'gps_datetime_object'):
                        if getattr(self, 'gps_datetime_object'):
                            df = df.set_index(pd.to_datetime(getattr(self, 'gps_datetime_object'), utc=True))
        self.dataframe=df
        return df
