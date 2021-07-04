"""spectroscopy.py

Part of proespm: Spectroscopy data.

(C) Copyright Nicolas Bock, licensed under GPL v3
See LICENSE or http://www.gnu.org/licenses/gpl-3.0.html
"""

import numpy as np
import json
import os
from data import Data
import data

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
        """Import Renishaw Raman data.

        Args:
            file (str): Full path to the data file.
        """

        self.data = np.loadtxt(m_file, usecols=(0, 1), skiprows=1)
        self.wavelength = self.data[:, 0].tolist()
        self.intensity = self.data[:, 1].tolist()

    def import_file(self, m_file):
        """Decide which import function to apply.

        Args:
            file (str): Full path to the data file.
        """

        with open(m_file) as self.f:
            self._first_line = self.f.readline()

        if "#Wave" in self._first_line:
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
        self.xps = None
        self.e_bind = None
        self.counts = None
        self.start = None
        self.end = None
        self.sweeps = None
        self.dwell = None
        self.mode = None
        self.import_file(m_file)

    def import_e20_xps(self, m_file):
        """Import xps data from Agilent VEE.

        Args:
            file (str): Full path to the data file.
        """

        self.data = np.loadtxt(m_file, usecols=(0, 1), delimiter=",")
        self.e_kin = self.data[:, 0].tolist()
        self.intensity = self.data[:, 1].tolist()

    def import_phi_xps(self, m_file):
        """Import xps data from PHI xps setups.

        Args:
            file (str): Full path to the data file.
        """

        self.data = np.loadtxt(m_file, usecols=(0, 1), delimiter=",", skiprows=4)
        self.e_kin = self.data[:, 0].tolist()
        self.intensity = self.data[:, 1].tolist()

    def import_vtstm_xps(self, m_file):
        """Import xps data from which software?

        """
        with open(m_file) as json_file:
            self.data = json.load(json_file)
        
        for key, value in self.data['meta_data'].items():
            setattr(self, key.lower(), value) 

        for key, value in self.data['xps_data'].items():
            setattr(self, key.lower(), value)

        self.e_pass = self.data['meta_data']['CAE/CRR']
        
    def import_file(self, m_file):
        """Decide which import function to apply.

        Args:
            file (str): Full path to the data file.
        """

        with open(m_file) as self.f:
            self._first_line = self.f.readline()

        if m_file.endswith("dat"):
            self.import_e20_xps(m_file)
        elif m_file.endswith("csv"):
            self.import_phi_xps(m_file)
        elif m_file.endswith("json"):
            self.import_vtstm_xps(m_file)

    def correct_work_function(self, offset):
        """Corrects for the XPS analyzer work function.

        Args:
            offset (float): Work function [eV].
        """

        self.ekin_cor = [i - offset for i in self.ekin]


def xps_vt_split(filepath):
    """ Splits the VT-STM-xps .txt-file in json files for each scan

    Args:

    """
    m_id = data.m_id(filepath)
    print(m_id)
    with open(filepath) as f:
        scan_num = f.read().count('Region')
        f.seek(0) 

        meta_data = dict(xps='vtstm')
        json_out_files = []
        for i in range(scan_num):
            line1 = f.readline().split('\t')
            line1 = [x.rstrip('\n') for x in line1]
            line2 = f.readline().split('\t')
            line2 = [x.rstrip('\n') for x in line2]

            meta_data.update(dict(zip(line1,line2)))

            line3 = f.readline().split('\t')
            line3 = [x.rstrip('\n') for x in line3]
            line4 = f.readline().split('\t')
            line4 = [x.rstrip('\n') for x in line4]

            meta_data.update(dict(zip(line3,line4)))

            data_header = f.readline().split('\t')
            data_header = [x.rstrip('\n') for x in data_header]

            start = float(meta_data['Start'])
            end = float(meta_data['End'])
            step = float(meta_data['Step'])

            num_lines = int(abs(start - end) / step)

            data_lst = [[float(x) for x in f.readline().split('\t')]]
            for _ in range(num_lines):
                line = [float(x) for x in f.readline().split('\t')]
                data_lst.append(line)
                
            e_bind = [x[0] for x in data_lst]
            counts = [x[1] for x in data_lst]
        
            xps_data = dict(e_bind=e_bind, counts=counts)
            scan = dict(meta_data=meta_data, xps_data=xps_data)
            
            dir_path = os.path.dirname(os.path.abspath(filepath))
            file_out_name = "{}_scan{}.json".format(m_id, i+1)
            file_out_path = os.path.join(dir_path, file_out_name)
            with open(file_out_path, 'w') as json_file:
                json.dump(scan, json_file)

            json_out_files.append(file_out_path)
            
    return json_out_files
