"""spm.py

Part of proespm: Scanning probe microscopy data.

(C) Copyright Nicolas Bock, licensed under GPL v3 
See LICENSE or http://www.gnu.org/licenses/gpl-3.0.html
"""

from util import importHelper, WIN32_helper

importHelper()

if 'path_gwyddion' not in locals():
    WIN32_helper()

import gwy
import gwyutils
import gwyddion
import config
import shutil
import re
import os
import xarray
import rhksm4
import numpy as np
import matplotlib.pyplot as plt
from pint import UnitRegistry
from data import data
from ec import ec

ureg = UnitRegistry()

class spm(data):
    """Represents any SPM data which can be handled with Gwyddion software.
    
    The file format should be supported by the Gwyddion software.
    opt. arguments (str): tip, electrolyte, we, ce, re
    
    Args:
        file (str): Path to ecstm file.
    """
    
    def __init__(self, file, **kwargs):
        self.surface = None
        self.tip = None
        data.__init__(self, file, **kwargs)
        self.spm_data = self.importFile(file)
        self.img_topo_fwd = None
        self.img_topo_bwd = None
        self.size = None
        self.rotation = None
        self.line_time = None
    
    
    def importFile(self, file):
        """Function which decides which import function to use.
        
        Based on a file extension.
        
        Args:
            file (str): Path to file which will be imported.
        """
        
        if file endswith 'SM4':
            self.importSm4(file)
        elif file endswith 'gwy':
            pass
        
    
    def importSm4(self, file):
        """Function which import SM4 files from RHK devices to xarray.
        
        Args:
            file (str): Path to file which will be imported.
        """
        return(rhksm4.to_dataset(file))
    
    


import matplotlib.pyplot as plt

plt.imshow(self.spm_data['Topography_Forward'].data)
plt.show()






class stm(spm):
    """Represents any stm data. Compared to spm data it also stores tunnel current and tunnel voltage"""
    
    def __init__(self, file, **kwargs):
        spm.__init__(self, file, **kwargs)
        self.i_tun = iTunMean(self)
        self.u_tun = uTunMean(self)
    

    
    def uTunMean(self):
        """Returns the average tunnel voltage of one stm image."""
        
        try:
            return(self.spm_data['Utun__Forward'].data.mean())
        except(KeyError):  
            try:
                return(self.spm_data['Topography_Forward'].bias)
            except(KeyError):  
                return(None)
    
    
    def iTunMean(self):
        """Numpy array of all tunnel current values in the stm image."""
        
        try:
            return(self.spm_data['Current__Forward'].data.mean())
        except(KeyError):  
            try:
                return(self.spm_data['Topography_Forward'].biaRHK_Currents)
            except(KeyError):  
                return(None)



class ecstm(stm, ec):
    """Ecstm measurement data."""
    
    def __init__(self, file, **kwargs):
        stm.__init__(self, file, **kwargs)
        ec.__init__(self, file, **kwargs)
        self._ecell_ch_id = spm.findChannel(self, ["*VEC*"])
        self._icell_ch_id = spm.findChannel(self, ["*IEC*"] )
        self.icell = self.iCellData()
        self.file_ec_igor = None
        self.file_ic_igor = None
    
    
    def returnEcellChannel(self):
        """Return cell potential channel."""
        
        return(self.returnDataChTitle(self._ecell_ch_id))
    
    
    def returnIcellChannel(self):
        """Return cell current channel."""
        
        return(self.returnDataChTitle(self._icell_ch_id))
    
    
    def eCellData(self):
        """Electrochemical cell potential data.
        
        So the 512x512 np array is getting averaged to 512x1,
        it's resolution is determined by the line time of the 
        stm image (50 - 300 ms). This could be improved in future by
        combination of forward and backward image data.
        """
        
        if len(self._ecell_ch_id) > 0:
            self.e_cell_data = self.convertNP(self._ecell_ch_id[0])
            return(np.average(self.e_cell_data, axis=0).tolist())
    
    
    def iCellData(self):
        """Electrochemical cell current data.
        
        So the 512x512 np array is getting averaged to 512x1,
        it's resolution is determined by the line time of the 
        stm image (50 - 300 ms). This could be improved in future by
        combination of forward and backward image data.
        """
        
        if len(self._icell_ch_id) > 0:
            self.i_cell_data = self.convertNP(self._icell_ch_id[0])
            self.icell_line = np.average(self.i_cell_data, axis=0).tolist()
        else:
            self.icell_line = None
        
        return(self.icell_line)
    
    
    def saveEcData(self, path):
        """Save electrochemical cell potential to data file."""
        
        self.ec_data_file = os.path.join(path, str(self.id) + "_ec" + "." + config.dat_type_out)
        np.savetxt(self.ec_data_file, ecstm.eCellData(self), delimiter = ';')
        
        if config.dat_type_igor:
            self.file_ec_igor = os.path.join(path, 'g' + str(self.id) + '_ori.ec0')
            shutil.move(self.ec_data_file, self.file_ec_igor)
    
    
    def saveIcData(self, path):
        """Save electrochemical cell current to data file."""
        
        self.ic_data_file = os.path.join(path, str(self.id) + "_ic" + "." + config.dat_type_out)
        np.savetxt(self.ic_data_file, self.icell, delimiter = ';')
        
        if config.dat_type_igor:
            self.file_ic_igor = os.path.join(path, 'g' + str(self.id) + '_ori.ic0')
            shutil.move(self.ic_data_file, self.file_ic_igor)
    

class afm(spm):
    """Atomic force mircoscopy."""
    
    def __init__(self, file, **kwargs):
        spm.__init__(self, file, **kwargs)
    
    
    def returnPhaseCh(self):
        """Return phase channel."""
        
        return(self.findChannel(["*Phase*"]))
    
    
    def returnPhaseFwdCh(self):
        """Return forward phase channel."""
        self.pat_fwd = ['^.*[F||f]orward.*$', '^.*[R||r]ight.*$', '.*fwd.*']
        for ch in self.returnPhaseCh():
            self.gen = (ch for pat in self.pat_fwd if re.match(pat, self.returnDataChTitle(ch)))
            for pat in self.gen:
                return(ch)
    
    
    def returnPhaseBwdCh(self):
        """Return backward phase channel."""
        
        self.pat_bwd = ['^.*[B||b]ackward.*$', '^.*[L||l]eft.*$', '.*bwd.*']
        for ch in self.returnPhaseCh():
            self.gen = (ch for pat in self.pat_fwd if re.match(pat, self.returnDataChTitle(ch)))
            for pat in self.gen:
                return(ch)
        
        return(self.phase_bwd_ch)
    
    def savePhaseFwdImage(self, path):
        """Save forward phase to image file."""
        
        gwy.gwy_app_data_browser_select_data_field(self.container, self.returnPhaseFwdCh())
        self.img_phase_fwd = os.path.join(path, str(self.id) + '_pf.' + config.img_type_out)
        gwyddion.saveImageFile(self.container, self.img_phase_fwd)
    
    
    def savePhaseBwdImage(self, path):
        """Save backward phase to image file."""
        
        gwy.gwy_app_data_browser_select_data_field(self.container, self.returnPhaseBwdCh())
        self.img_phase_bwd = os.path.join(path, str(self.id) + '_pb.' + config.img_type_out)
        gwyddion.saveImageFile(self.container, self.img_phase_bwd)
