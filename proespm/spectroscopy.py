"""spectroscopy.py

Part of proespm: Spectroscopy data.

(C) Copyright Nicolas Bock, licensed under GPL v3
See LICENSE or http://www.gnu.org/licenses/gpl-3.0.html
"""

import numpy as np
from data import Data


class Spectroscopy(Data):
    """ Spectroscopy measurements."""

    def __init__(self, m_file, **kwargs):
        Data.__init__(self, m_file, **kwargs)


class Raman(Spectroscopy):
    """ Raman measurements."""

    def __init__(self, m_file, **kwargs):
        Spectroscopy.__init__(self, m_file, **kwargs)
        self.wavelength = None
        self.intensity = None
        self.import_file(self.m_file)


    def import_raman(self, m_file):
        """ Import Renishaw Raman data.

        Args:
            file (str): Full path to the data file.
        """

        self.data = np.loadtxt(m_file, usecols=(0, 1), skiprows=1)
        self.wavelength = self.data[:, 0].tolist()
        self.intensity = self.data[:, 1].tolist()


    def import_file(self, m_file):
        """ Decide which import function to apply.

        Args:
            file (str): Full path to the data file.
        """

        with open(m_file) as self.f:
            self._first_line = self.f.readline()

        if '#Wave' in self._first_line:
            self.import_raman(m_file)


class Xps(Spectroscopy):
    """ X-ray photon electron spectroscopy measurements."""

    def __init__(self, m_file, **kwargs):
        Spectroscopy.__init__(self, m_file, **kwargs)
        self.xray = None
        self.e_pass = None
        self.e_kin = None
        self.signal = None
        self.scans = None
        self.intensity = None
        self.import_file(m_file)


    def import_e20_xps(self, m_file):
        """ Import xps data from Agilent VEE.

            Args:
                file (str): Full path to the data file.
        """

        self.data = np.loadtxt(m_file, usecols=(0, 1), delimiter=',')
        self.e_kin = self.data[:, 0].tolist()
        self.intensity = self.data[:, 1].tolist()


    def import_phi_xps(self, m_file):
        """ Import xps data from PHI xps setups.

            Args:
                file (str): Full path to the data file.
        """

        self.data = np.loadtxt(m_file,
                               usecols=(0, 1),
                               delimiter=',',
                               skiprows=4)
        self.e_kin = self.data[:, 0].tolist()
        self.intensity = self.data[:, 1].tolist()


    def import_file(self, m_file):
        """ Decide which import function to apply.

        Args:
            file (str): Full path to the data file.
        """

        with open(m_file) as self.f:
            self._first_line = self.f.readline()

        if m_file.endswith('dat'):
            self.import_e20_xps(m_file)
        elif m_file.endswith('csv'):
            self.import_phi_xps(m_file)


    def correct_work_function(self, offset):
        """ Adds corrected XPS data by work function of sample.

        Args:
            offset (float): Work function of sample in [eV].
        """

        self.ekin_cor = [i - offset for i in self.ekin]
