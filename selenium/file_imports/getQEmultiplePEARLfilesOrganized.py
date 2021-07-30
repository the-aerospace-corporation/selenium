import os
import glob
import matplotlib.pyplot as plt
import numpy as np
from selenium import selenium_analysis as sa
from selenium.file_imports.getQEsinglePEARLfileOrganized import getQEsinglePEARLfileOrganized
import selenium.solar_spectra as solar_spectra
from selenium.file_imports.QeDataContainer import QeDataContainer
import pandas as pd

class getQEmultiplePEARLfilesOrganized(QeDataContainer):
    """
    Give it the folder path do a folder with a bunch of pearl QE txt files and it will parse, analyze and organize all the data in to an array for each attribute. See QeDataContainer to see documentation for all available attributes

    Args:
        folderpath (str): path to folder that has some pearl LIV txt files
    """

    def __init__(self, folderpath):
        QeDataContainer.__init__(self)
        os.chdir(folderpath)
        self.file_name = glob.glob('*.txt')
        attributes = list(self.__dict__.keys())
        self.data_objects = []

        for file in self.file_name:
            self.data_objects.append(getQEsinglePEARLfileOrganized(file))

        attributes.remove('file_name')
        for attr in attributes:
            attr_data = []
            for data_object in self.data_objects:
                if hasattr(data_object, attr):

                    if attr in ['qeData', 'wavelength_nm', 'qee', 'sr', 'syscal_w', 'cell_current_a', 'ref_cell_current_a', 'quantum_efficiency', 'spectral_response', 'system_calibration', 'cell_current', 'reference_cell_current']:
                        if len(getattr(data_object, attr))>0:
                            attr_data.append(getattr(data_object, attr))

                    elif attr in ['fluence', 'gridline_obscuration']:
                        attr_from_object = getattr(data_object, attr)
                        if isinstance(attr_from_object, str):
                            if attr_from_object in ['control', 'low V']:
                                attr_data.append(0)

                        elif getattr(data_object, attr) > -1:
                            attr_data.append(getattr(data_object, attr))

                    elif attr in ['gridline_obscuration']:
                        if getattr(data_object, attr) > -1:
                            attr_data.append(getattr(data_object, attr))

                    else:
                        attr_data.append(getattr(data_object, attr))
            setattr(self, attr, attr_data)

        self.make_dataframe()
        # self.groupedByCell_ID = self._groupByCell_ID()

    def jscQuantumEfficiency(self, Irradiance_Spectrum=None, interpolation_method='QE'):
        if Irradiance_Spectrum is None:
            Irradiance_Spectrum = solar_spectra.AM0

        else:
            Irradiance_Spectrum = Irradiance_Spectrum

        jsc = []
        for data in self.qeData:
            jsc.append(data.jsc_quantum_efficiency(Irradiance_Spectrum, interpolation_method=interpolation_method))
        return jsc

    def jscSpectralResponse(self, Irradiance_Spectrum):
        jsc = []
        for data in self.qeData:
            jsc.append(data.jsc_spectral_response(Irradiance_Spectrum))
        return jsc

    def jscIntQuantumEfficiency(self, Irradiance_Spectrum):
        jsc = []
        for data in self.qeData:
            x_new = np.arange(np.min(data.quantum_efficiency[:, 0]), np.max(data.quantum_efficiency[:, 0] + 1))
            y_new = np.interp(x_new, data.quantum_efficiency[:, 0], data.quantum_efficiency[:, 1])
            J2 = np.vstack((x_new, y_new)).T
            jsc.append(sa.get_jsc_from_quantum_efficiency(J2, Irradiance_Spectrum))
        return jsc

    def plotQE(self, cmap_colors=None, linestyle='-', color_single='blue', label=None):
        qe_by_cell_id = self._group_by_serial_number(self.quantum_efficiency)
        if cmap_colors != None:
            cmap = plt.get_cmap(name=cmap_colors)
            number_of_qe_plots = len(qe_by_cell_id)
            if number_of_qe_plots > 1:
                line_colors = cmap(np.linspace(0, 1, number_of_qe_plots))
        else:
            line_colors = [color_single] * len(qe_by_cell_id)
        cell_id = np.unique(self.cell_id)
        for i, qe_cell in enumerate(qe_by_cell_id):
            for j, junction in enumerate(qe_cell):
                if label == None:
                    if j == 0:
                        qe_label = cell_id[i]
                    else:
                        qe_label = None
                else:
                    if j == 0:
                        qe_label = label
                    else:
                        qe_label = None
                plt.plot(junction[:, 0], junction[:, 1], label=qe_label, lw=1, color=line_colors[i],
                         linestyle=linestyle)

    def plotQE_all(self, cmap_colors=None, linestyle='-', color_single='blue', label=None):
        qes_all = self.quantum_efficiency
        if cmap_colors != None:
            cmap = plt.get_cmap(name=cmap_colors)
            number_of_qe_plots = len(qes_all)
            if number_of_qe_plots > 1:
                line_colors = cmap(np.linspace(0, 1, number_of_qe_plots))
        else:
            line_colors = [color_single] * len(qes_all)
        cell_id = np.unique(self.cell_id)
        for i, qe_cell in enumerate(qes_all):
            if label == None:
                if self.junction[i] == 1:
                    qe_label = self.cell_id[i]
                else:
                    qe_label = None
            else:
                if self.junction[i] == 1:
                    qe_label = label
                else:
                    qe_label = None
            plt.plot(qe_cell[:, 0], qe_cell[:, 1], label=qe_label, lw=1.5, color=line_colors[i], linestyle=linestyle)

    def average_qes(self):
        junctions = np.unique(self.junction)
        averaged_qes = []
        for junc_unique in junctions:
            qe_jx = []
            for i, junc in enumerate(self.junction):
                if junc_unique == junc:
                    qe_jx.append(self.quantum_efficiency[i])
            averaged_qes.append(sa.average_qe_spectra(qe_jx))
        return averaged_qes

    def average_jsc(self):
        junctions = np.unique(self.junction)
        averaged_j = []
        for junc_unique in junctions:
            jx = []
            for i, junc in enumerate(self.junction):
                if junc_unique == junc:
                    jx.append(self.jsc[i])
            averaged_j.append(np.mean(jx))
        return averaged_j

    def maketable(self, param=None):
        if param == None:
            param = self.jsc
        table = []
        jsc_grouped_by_cell_id = self._group_by_serial_number(param)
        model_grouped_by_cell_id = self._group_by_serial_number(self.model)

        for i, cell_id in enumerate(np.unique(self.cell_id)):
            table.append(list([model_grouped_by_cell_id[i][0], cell_id] + list(jsc_grouped_by_cell_id[i])))
        return table

    def make_dataframe(self, list_of_items=None):
        """
        Makes a dataframe where the columns are the attributes of this object that you want in the dataframe.
        Args:
            list_of_items: Any attribute of the object. The defaults are ['file_name', 'manufacturer','model','cell_id', 'jsc','voc','imax','vmax','pmax','fill_factor','efficiency']

        Returns:
            A pandas dataframe where the colums of data are the what the user wants outputted
        """
        if list_of_items == None:
            list_of_items = ['file_name', 'manufacturer', 'model', 'cell_id', 'jsc']
        attributes = list(self.__dict__.keys())
        data_for_table = []
        for i, item in enumerate(list_of_items):
            if item in attributes:
                data_for_table.append(getattr(self, item))

        data_for_table = np.array(data_for_table, dtype=object).T
        self.dataframe = pd.DataFrame(data_for_table, columns=list_of_items)

    def _group_by_serial_number(self, param_to_be_grouped):
        indicesOfDuplicates = []
        cell_ids = np.unique(self.cell_id)
        for cell_id in cell_ids:
            indicesOfDuplicates.append(list(np.where(np.array(self.cell_id) == cell_id)[0]))
        grouped_by_cell_ID = []
        for index in indicesOfDuplicates:
            sorted_arrays = sa.sortTwoArrays(self.junction[min(index):max(index) + 1],
                                             param_to_be_grouped[min(index):max(index) + 1])
            grouped_by_cell_ID.append(sorted_arrays[1])
        return grouped_by_cell_ID

    def _groupByCell_ID(self):
        groupedByCell_ID = []
        cell_ids = self.cell_id
        indicesOfDuplicates = sa.findIndicesofDuplicates(cell_ids)
        for indices in indicesOfDuplicates:
            grouped = [self.data_objects[i] for i in indices]
            groupedByCell_ID.append(grouped)
        return groupedByCell_ID
