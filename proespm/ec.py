"""ec.py

Part of proespm: Electrochemical data.

(C) Copyright Nicolas Bock, licensed under GPL v3
See LICENSE or http://www.gnu.org/licenses/gpl-3.0.html
"""

import os
import config
import re
import pandas
import codecs
import numpy as np
import util
from pint import UnitRegistry
from data import Data

ureg = UnitRegistry()


class Ec(Data):
    """Represents any electrochemical conditions.

    As optional parameters surface (str), remark (str), electrolyte (str),
    pH (float), currentRange (int), re (str), ce (str) etc. can be given.
    For further details see or adjust template.html which will end up in
    the html report.
    """

    def __init__(self, m_file, **kwargs):
        self.electrolyte = None
        self.gas = None
        self.surface = None
        self.pH = None
        self.re = ""
        self.ce = None
        self.we = None
        self.ecell = None
        self.icell = None
        Data.__init__(self, m_file, **kwargs)

    def data_points(self):
        """Returns the number of data points"""

        return len(self.ecell)

    def i_cell_correction(self, cor):
        """Corrects the cell current by a division factor.

        Args:
            cor (int): Value current will be divided by.
        """

        self.jcell = icell.div(cor)
        self.cvdata = pandas.concat([self.cvdata, self.jcell], axis=1)

    def save_ec(self, path):
        """Saves electrochemical pandas dataframe to ASCII file.

        Args:
            path (str): Path where the file will be saved.
        """

        self.ec_data_file = os.path.join(
            path, str(self.m_id) + "_ec." + config.dat_type_out
        )
        self.cvdata.to_csv(self.ec_data_file, index=False)


class Cv(Ec):
    """Represents a cyclic voltammogram measurement."""

    def __init__(self, m_file, **kwargs):
        Ec.__init__(self, m_file, **kwargs)
        self.pop_next_file = 0
        self.rate = None
        self.vs = None
        self.v1 = None
        self.v2 = None
        self.sweeps = 1
        self.ecell = pandas.DataFrame()
        self.icell = pandas.DataFrame()
        self.cvdata = pandas.DataFrame()
        self.import_file(m_file)

    def append_cycle(self, data, id_new, remark):
        """Adds cv data as following sweeps to this CV class.

        This is needed as some measurement programms export for each CV
        cycle a new file.

        Args:
            data (numpy-df): Ecell and Icell data which will be appended.
            id_new (str): id of file which will be added.
            remark (str): Remark which will be added.
        """

        self.m_id = self.m_id + "; " + id_new
        self.remark = self.remark + "; " + remark
        self.sweeps = int(re.search("\d\_(.*\d)$", id_new).group(1).strip(" "))
        self.cycle = "Cycle " + str(self.sweeps)
        self.ecell_new = pandas.DataFrame({self.cycle + ": Ecell": data[:, 1].tolist()})
        self.cvdata = pandas.concat([self.cvdata, self.ecell_new], axis=1)
        self.icell_new = pandas.DataFrame({self.cycle + ": Icell": data[:, 2].tolist()})
        self.cvdata = pandas.concat([self.cvdata, self.icell_new], axis=1)

    def import_ec4(self, m_file):
        """Imports Nordic Electrochemistry EC4 file format.

        Args:
            file (str): Path to file which will be imported.
        """

        self.lines = util.read_lines(m_file, range(96))
        self.extract_par = [
            ["self.vs", "Start", "Start\s(\S*.\S)"],
            ["self.v1", "V1", "V1\s(\S*.\S)"],
            ["self.v2", "V2", "V2\s(\S*.\S)"],
            ["self.rate", "Rate", "Rate\s(\S*.\S)"],
        ]

        for x in util.extract_value(self.extract_par, self.lines.values()):
            exec(x[0] + '= ureg("' + x[1].replace(",", ".") + '")')

        self.data = np.loadtxt(m_file, usecols=(0, 1, 2), skiprows=96)
        self.ecell = pandas.DataFrame({"Cycle 1: Ecell": self.data[:, 1].tolist()})
        self.cvdata = pandas.concat([self.cvdata, self.ecell], axis=1)
        self.icell = pandas.DataFrame({"Cycle 1: Icell": self.data[:, 2].tolist()})
        self.cvdata = pandas.concat([self.cvdata, self.icell], axis=1)

    def import_labview(self, m_file):
        """Specific function to import Labview txt data.

        Args:
            file (str): Path to file which will be imported.
        """

        self.data = np.loadtxt(m_file, usecols=(0, 1, 2), skiprows=22)
        self.ecell_list = self.data[:, 1].tolist()
        self.icell_list = self.data[:, 2].tolist()
        self.vs = self.ecell_list[0] * ureg("volt")
        if self.ecell_list[0] < self.ecell_list[1]:  # scan direction vs < v1
            self.v1 = max(self.ecell_list) * ureg("volt")
            self.v2 = min(self.ecell_list) * ureg("volt")
        else:  # scan direction vs > v1
            self.v1 = min(self.ecell_list) * ureg("volt")
            self.v2 = max(self.ecell_list) * ureg("volt")
        self.total_time = self.data[len(self.ecell) - 1, 0] * ureg("seconds")
        self.rate = 2 * (abs(self.v1) + abs(self.v2)) / self.total_time

        self.ecell = pandas.DataFrame({"Cycle 1: Ecell": self.ecell_list})
        self.cvdata = pandas.concat([self.cvdata, self.ecell], axis=1)
        self.icell = pandas.DataFrame({"Cycle 1: Icell": self.icell_list})
        self.cvdata = pandas.concat([self.cvdata, self.icell], axis=1)

    def import_biologic(self, m_file):
        """Function to import mpt-CV files from Biologic potentiostats.

        Args:
            file (str): Path to file which will be imported.
        """

        self.lines = util.read_lines(m_file, range(53))
        if "Cyclic Voltammetry" in self.lines[3]:
            self.extract_par = [
                ["self.vs", "Ei", "Ei\s\(V\)\s*(\S*)"],
                ["self.v1", "E1", "E1\s\(V\)\s*(\S*)"],
                ["self.v2", "E2", "E2\s\(V\)\s*(\S*)"],
                ["self.rate", "dE/dt  ", "dt\s*(\S*)"],
                ["self.sweeps", "nc cycles", "cycles\s*(\S*)"],
                ["self.skiprows", "Nb header lines", "lines\s:\s*(\d*)\s*"],
            ]

            for x in util.extract_value(self.extract_par, self.lines.values()):
                exec(x[0] + '= ureg("' + x[1] + '")')

            self.file_trimmed = codecs.open(m_file, encoding="cp1252")
            self.data = np.loadtxt(
                self.file_trimmed,
                usecols=(7, 8, 9),
                skiprows=int(self.skiprows),
                delimiter="\t",
            )

            # Biologic files contain all sweeps of a CV in one file
            self.sweeps = int(max(self.data[:, 2]))
            for cycle in range(1, self.sweeps + 1):
                self.ecell = pandas.DataFrame(
                    {
                        "Cycle "
                        + str(cycle)
                        + ": Ecell": self.data[
                            np.where(self.data[:, 2] == cycle), 0
                        ].tolist()[0]
                    }
                )
                self.cvdata = pandas.concat([self.cvdata, self.ecell], axis=1)
                self.icell = pandas.DataFrame(
                    {
                        "Cycle "
                        + str(cycle)
                        + ": Icell": self.data[
                            np.where(self.data[:, 2] == cycle), 1
                        ].tolist()[0]
                    }
                )
                self.cvdata = pandas.concat([self.cvdata, self.icell], axis=1)

    def import_file(self, m_file):
        """Function which decides which import function to use.

        Based on a key word in the first line of the data file it will
        be decided which import function will be applied.

        Args:
            file (str): Path to file which will be imported.
        """

        with open(m_file) as self.f:
            self._first_line = self.f.readline()

        if "EC4" in self._first_line:
            self.import_ec4(m_file)
        elif "LabVIEW" in self._first_line:
            self.import_labview(m_file)
        elif "EC-Lab" in self._first_line:
            self.import_biologic(m_file)


class Peis(Ec):
    """Potentiostatic electrochemical impedance spectroscopy measurement."""

    def __init__(self, m_file, **kwargs):
        Ec.__init__(self, m_file, **kwargs)
        self.fi = None
        self.ff = None
        self.imgr = pandas.DataFrame()
        self.rer = pandas.DataFrame()
        self.peisdata = pandas.DataFrame()
        self.import_biologic(m_file)

    def import_biologic(self, m_file):
        """Function to import PEIS mpt files from Biologic potentiostats.

        Args:
            file (str): Path to file which will be imported.
        """

        self.lines = util.read_lines(m_file, range(83))
        if "Potentio Electrochemical Impedance Spectroscopy" in self.lines[3]:
            self.extract_par = [
                ["self.ecell", "E (V)", "E\s\(V\)\s*(\S*)"],
                ["self.fi", "fi                  ", "^fi\s*(\S*)"],
                ["self.fi_unit", "unit fi", "\sfi\s*(\S*)"],
                ["self.ff", "ff                  ", "^ff\s*(\S*)"],
                ["self.ff_unit", "unit ff", "\sff\s*(\S*)"],
                ["self.amplitude", "Va", "\(mV\)\s*(\S*)"],
                ["self.skiprows", "Nb header lines", "lines\s:\s*(\d*)\s*"],
            ]

            for x in util.extract_value(self.extract_par, self.lines.values()):
                exec(x[0] + '= str("' + x[1] + '")')

            self.file_trimmed = codecs.open(m_file, encoding="cp1252")
            self.data = np.loadtxt(
                self.file_trimmed,
                usecols=(0, 1, 2),
                skiprows=int(self.skiprows),
                delimiter="\t",
            )
            self.rer = pandas.DataFrame({"re R": self.data[:, 1].tolist()})
            self.imgr = pandas.DataFrame({"img R": self.data[:, 2].tolist()})
            self.peisdata = pandas.concat([self.peisdata, self.rer], axis=1)
            self.peisdata = pandas.concat([self.peisdata, self.imgr], axis=1)


class Chrono(Ec):
    """Chronoamperometry measurement."""

    def __init__(self, m_file, **kwargs):
        Ec.__init__(self, m_file, **kwargs)
        self.time = pandas.DataFrame()
        self.icell = pandas.DataFrame()
        self.chronodata = pandas.DataFrame()
        self.importBiologic(m_file)

    def importBiologic(self, m_file):
        """Function to import CA mpt files from Biologic potentiostats.

        Args:
            file (str): Path to file which will be imported.
        """

        self.lines = util.read_lines(m_file, range(57))
        if "Chrono" in self.lines[3]:
            self.extract_par = [
                ["self.ecell", "Ei", "Ei\s\(V\)\s*(\S*)"],
                ["self.skiprows", "Nb header lines", "lines\s:\s*(\d*)\s*"],
            ]

            for x in util.extract_value(self.extract_par, self.lines.values()):
                exec(x[0] + '= str("' + x[1] + '")')

            self.file_trimmed = codecs.open(m_file, encoding="cp1252")
            self.data = np.loadtxt(
                self.file_trimmed,
                usecols=(7, 10),
                skiprows=int(self.skiprows),
                delimiter="\t",
            )
            self.time = pandas.DataFrame({"time [s]": self.data[:, 0].tolist()})
            self.icell = pandas.DataFrame({"Icell [mA]": self.data[:, 1].tolist()})
            self.chronodata = pandas.concat([self.chronodata, self.time], axis=1)
            self.chronodata = pandas.concat([self.chronodata, self.icell], axis=1)
