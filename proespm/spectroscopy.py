"""spectroscopy.py

Part of proespm: Spectroscopy data.

(C) Copyright Nicolas Bock, licensed under GPL v3 
See LICENSE or http://www.gnu.org/licenses/gpl-3.0.html
"""

import numpy as np
from data import data
from pint import UnitRegistry

ureg = UnitRegistry()

class spectroscopy(data):
    """ Spectroscopy measurements."""
    
    def __init__(self, file, **kwargs):
        data.__init__(self, file, **kwargs)


class raman(spectroscopy):
    """ Raman measurements."""
    
    def __init__(self, file, **kwargs):
        spectroscopy.__init__(self, file, **kwargs)
        self.wavelength = None
        self.intensity = None
        self.importFile(file)
    
    
    def importRaman(self, file):
        """ Import Renishaw Raman data.
    
        Args:
            file (str): Full path to the data file.
        """
        
        self.data = np.loadtxt(file, usecols = (0,1), skiprows = 1)
        self.wavelength = self.data[:, 0].tolist()
        self.intensity = self.data[:, 1].tolist()
    
    
    def importFile(self, file):
        """ Decide which import function to apply.
    
        Args:
            file (str): Full path to the data file.
        """
        
        with open(file) as self.f:
            self._first_line = self.f.readline()
        
        if '#Wave' in self._first_line:
            self.importRaman(file)


class xps(spectroscopy):
    """ X-ray photon electron spectroscopy measurements."""
    
    def __init__(self, file, **kwargs):
        spectroscopy.__init__(self, file, **kwargs)
        self.xray = None
        self.e_pass = None
        self.e_kin = None
        self.signal = None
        self.scans = None
        self.intensity = None
        self.importFile(file)
        
        
    def importE20Xps(self, file):
        """ Import xps data from Agilent VEE.
    
        Args:
            file (str): Full path to the data file.
        """
        
        self.data = np.loadtxt(file, usecols=(0,1), delimiter=',')
        self.e_kin = self.data[:,0].tolist()
        self.intensity = self.data[:,1].tolist()
    
    
    def importPhiXps(self, file):
        """ Import xps data from PHI xps setups.
    
        Args:
            file (str): Full path to the data file.
        """
        
        self.data = np.loadtxt(file, usecols=(0,1), delimiter=',', skiprows=4)
        self.e_kin = self.data[:,0].tolist()
        self.intensity = self.data[:,1].tolist()
    
    
    def importFile(self, file):
        """ Decide which import function to apply.
        
        Args:
            file (str): Full path to the data file.
        """
        
        with open(file) as self.f:
            self._first_line = self.f.readline()
        
        if file.endswith('dat'):
            self.importE20Xps(file)
        elif file.endswith('csv'):
            self.importPhiXps(file)
    
    
    def correctWorkFunction(self, offset):
        """ Adds corrected XPS data by work function of sample.
        
        Args:
            offset (float): Work function of sample in [eV].
        """
        
        self.ekin_cor = [i - offset for i in self.ekin]
