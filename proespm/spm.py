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
import numpy as np
from data import data
from ec import ec



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
        self.setSettings()
        self.container = gwy.gwy_file_load(self.file, gwy.RUN_NONINTERACTIVE)
        gwy.gwy_app_data_browser_add(self.container)
        self.img_topo_fwd = None
        self.img_topo_bwd = None
        self.topo_fwd_ch = self.returnTopoFwdCh()
        self.topo_bwd_ch = self.returnTopoBwdCh()
        self.size = None
        self.rotation = None
        self.line_time = None
        self.extractMeta(gwyddion.getMetaIDs(self.container)[0])
    
    
    def extractMeta(self, meta_id):
        """ Extracts all the meta data from the gwyddion container.
        
        Args:
            meta_id: Id where the meta data can be found.
        """
        
        pattern = {'self.size': ['IMAGE CONTROL::Scan:Size::Scan Control::Scan size', 'Image size'],
                   'self.rotation': ['IMAGE CONTROL::Scan:Size::Scan Control::Scan Rotation', 'Rotation'],
                   'self.line_time': ['IMAGE CONTROL::Scan:Size::Scan Control::Line time', 'Time/Line'],
                   'self.type': ['Op. mode', 'Image mode']}
        for k, pat_list in pattern.iteritems():
            for pat in pat_list:
                try:
                    exec("{} = self.container[{}]['{}']".format(k, meta_id, pat))
                except(KeyError):
                    pass
    
    
    def setSettings(self):
        """Sets the setting which are supplied by the user editable config file."""
        
        self.settings = gwy.gwy_app_settings_get()
        self.settings['/module/linematch/direction'] = int(gwy.ORIENTATION_HORIZONTAL)
        self.settings['/module/linematch/do_extract'] = config.do_extract
        self.settings['/module/linematch/do_plot'] = config.do_plot
        self.settings['/module/linematch/method'] = config.method
        self.settings['/module/linematch/masking'] = config.masking
        self.settings['/module/linematch/max_degree'] = config.max_degree
        self.settings['/module/median-bg/radius'] = config.radius
        self.settings['/module/median-bg/do_extract'] = config.do_extract
        self.settings['/module/rotate/angle'] = config.angle
        self.settings['/module/rotate/create_mask'] = config.create_mask
        self.settings['/module/rotate/interp'] = config.rotate_interp
        self.settings['/module/rotate/resize'] = config.resize
        self.settings['/module/rotate/show_grid'] = config.show_grid
        self.settings['/module/scale/interp'] = config.scale_interp
        self.settings['/module/scale/proportional'] = config.proportional   
        self.settings['/module/scale/aspectratio'] = config.aspectratio
        self.settings['/module/asciiexport/add-comment'] = config.add_comment
    
    
    def findChannel(self, match_list):
        """Finds the right data channel within a Gwyddion container.
        
        Args:
            container: Gwyddion container with several data channels.
            match_list (list): Names which will be searched. e.g. topography
        
        Returns:
            chn_ids (list): List of channel IDs.
        """
        
        self.ch_ids = []
        for self._data_title in match_list:
            self._match_ch = gwy.gwy_app_data_browser_find_data_by_title(self.container, self._data_title)
            self.ch_ids.extend(self._match_ch)
        
        return self.ch_ids
    
    
    def returnDataChTitle(self):
        """Returns data channel titel"""
        
        self.ch = gwy.gwy_app_data_browser_get_data_ids(self.container)
        return [self.container['/' + str(i) + '/data/title'] for i in self.ch]
    
    
    def returnTopoCh(self):
        """Returns topography channels"""
        
        self.topo_pat = ["Z", "Topo", "(\d*)"]
        self.topo_ch = []
        for ch in self.returnDataChTitle():
            # ~ for pat in self.topo_pat:
                # ~ if re.search(pat, ch):
                    # ~ self.topo_ch.append(ch) 
            self.topo_ch = [ch for pat in self.topo_pat if re.search(pat, ch)]
        print(self.topo_ch)
        return self.topo_ch
    
    
    def returnMatchCh(self, pat_list):
        """ Finds the matching data channel from channel list. 
        
        Args:
            pat_list: Pattern list, which identifies the desired channel.
        
        Returns:
            ch (list): Channel id.
        """
        
        for ch in self.returnTopoCh():
            for pat in pat_list:
                if re.search(pat, ch):
                    return gwy.gwy_app_data_browser_find_data_by_title(self.container, ch)
            
            # ~ self.gen = (ch for pat in pat_list if re.match(pat, self.returnDataChTitle(ch)))
            # ~ return [ch for pat in pat_list if re.search(pat, self.returnDataChTitle(ch))]
            # ~ for pat in self.gen:
                # ~ return ch
    
    
    def returnTopoFwdCh(self):
        """Returns tophography forward channel"""
        
        return self.returnMatchCh(['^.*[F||f]orward.*$', 
                                   '^.*[R||r]ight.*$', 
                                   '^.*fwd.*$',
                                   '(\d*)'])
    
    
    def returnTopoBwdCh(self):
        """Returns topography backwards channel"""
        
        return self.returnMatchCh(['^.*[B||b]ackward.*$', 
                                   '^.*[L||l]eft.*$', 
                                   '^.*bwd.*$'])
    
    
    def returnFileName(self, data):
        """Returns the file name Igor friendly.
        
        This is needed to make the SPM data functional with the IGOR 
        image processing addon.
        
        "blahblah12345.xzy" --> "g1234_ori.t" - t: topo
        "BLAH111_123456.BLA" --> "g123456_ori.t" - t: topo
        
        Args:
            data (str): Path to file.
        """
        
        self.name = os.path.basename(data)
        
        self.pat_out = ['^[a-z,A-Z]*.(\d{1,6})\..{3}$', r'g\1_ori.t',
                        '^[a-z,A-Z]*\d*_(\d{1,6})\..{3}$', r'g\1_ori.t']
        for pat in range(0, len(self.pat_out), 2):
            self.name = re.sub(self.pat_out[pat], 
                          self.pat_out[pat + 1], 
                          self.name)     # (0,1), (2,3), (4,5) ...
            # a pattern match has occured (should only ever be ONE)
            if os.path.basename(data) != self.name: 
                break
        
        return self.name
    
    
    def convertNP(self, channel_id):
        """Converts a Gwyddion container to a Numpy array. 
        
        Args:
            channel_id (int): ID of channel which will be converted.
        
        Returns:
            np_array (array): Numpy array of container channel.
        """
        
        # Makes a data field (channel) current/active in the data browser.
        gwy.gwy_app_data_browser_select_data_field(self.container, channel_id)
        self.key = gwy.gwy_app_get_data_key_for_id(channel_id)
        self.name = gwy.gwy_name_from_key(self.key)
        
        return gwyutils.data_field_data_as_array(self.container[self.name])
    
    
    def processTopo(self, data_ch_id):
        """Processes the data with Gwyddion Python module. 
        
        Gwyddion topography processing functions: see config file. 
        Before saving the image, the colorrange needs adjustment. The 
        colorrange settings are stored in the container for each spm 
        file. (see online gwyfile-format)
        
        Args:
            data_ch_id (int): Channel of the container should be processed.
        """
        
        gwy.gwy_app_data_browser_select_data_field(self.container, data_ch_id)
        
        self.run_gwy_func = {gwy.RUN_IMMEDIATE: config.run_gwy_immediate_func}
        for k, values in self.run_gwy_func.iteritems():
            [gwy.gwy_process_func_run(v, self.container, k) for v in values]
        
        self.match_ch_topo = '/' + str(data_ch_id) + '/base/range-type'
        self.container[self.match_ch_topo] = 2
    
    
    def processTopoFwd(self):
        """Process forward topography"""
        
        if self.topo_fwd_ch:
            for ch in self.topo_fwd_ch:
                print(ch)
                self.processTopo(ch)
    
    
    def processTopoBwd(self):
        """Process backward topography"""
        
        if self.topo_bwd_ch:
            self.processTopo(self.topo_bwd_ch[0])
    
    
    def saveTopoFwdImage(self, path):
        """Save forward topography image file.
        
        Args:
            path (str): File path where the file should be save.
        """
        
        self.img_topo_fwd = os.path.join(path, str(self.id) + '_tf.' + config.img_type_out)
        gwyddion.saveImageFile(self.container, self.img_topo_fwd)
    
    
    def saveTopoBwdImage(self, path):
        """Save backward topography image file.
        
        Args:
            path (str): File path where the file should be save.
        """
        
        self.img_topo_bwd = os.path.join(path, str(self.id) + '_tb.' + config.img_type_out)
        gwyddion.saveImageFile(self.container, self.img_topo_bwd)
    
    
    def saveTopoFwdData(self, path):
        """Save forward topography data file.
        
        Args:
            path (str): File path where the file should be save.
        """
        
        self.dat_topo_fwd = os.path.join(path, str(self.id) + '_fwd.' + config.dat_type_out)
        gwy.gwy_file_save(self.container, self.dat_topo_fwd, gwy.RUN_NONINTERACTIVE)
        
        if config.dat_type_igor:
            self.file_igor = os.path.join(path, 'g' + str(self.id) + '_ori.tf0')
            shutil.move(self.dat_topo_fwd, self.file_igor)
    
    
    def saveTopoBwdData(self, path):
        """Save backward topography data file.
        
        Args:
            path (str): File path where the file should be save.
        """
        
        self.dat_topo_bwd = os.path.join(path, str(self.id) + '_bwd.' + config.dat_type_out)
        gwy.gwy_file_save(self.container, self.dat_topo_bwd, gwy.RUN_NONINTERACTIVE)
        
        if config.dat_type_igor:
            self.file_igor = os.path.join(path, 'g' + str(self.id) + '_ori.tb0')
            shutil.move(self.dat_topo_bwd, self.file_igor)
    
    
    def spmPixelSize(self):
        """Returns the Image Size of the spm file in pixels."""
        
        self.key = gwy.gwy_app_get_data_key_for_id(0)
        self.name = gwy.gwy_name_from_key(self.key)
        self.data_tmp = gwyutils.data_field_data_as_array(self.container[self.name])
        
        return np.shape(self.data_tmp)
    
    
    def flushMemory(self):
        """Deletes all the data channels in a Gwyddion container. 
        
        This is needed as the memory will fill up quickly and a C memory 
        error will occur.
        """
        
        for data_ch_id in gwy.gwy_app_data_browser_get_data_ids(self.container):
            self.key = gwy.gwy_app_get_data_key_for_id(data_ch_id)
            self.container.remove(self.key)



class stm(spm):
    """Represents any stm data. Compared to spm data it also stores 
       tunnel current and tunnel voltage"""
    
    def __init__(self, file, **kwargs):
        spm.__init__(self, file, **kwargs)
        self.i_tun = self.iTunMean()
        self.u_tun = self.uTunMean()
    
    
    def uTunLine(self):
        """Returns the average tunnel voltage value for each stm line.
        
        So the 512x512 np array is getting averaged to 512x1,
        it's resolution is determined by the line time of the 
        stm image (50 - 300 ms). This could be improved in future by
        combination of forward and backward image data.
        """
        
        self._utun_ch_ids = spm.findChannel(self, ["*Utun*"])
        if len(self._utun_ch_ids) > 0:
            self.u_tun_array = self.convertNP(self._utun_ch_ids[0])
            return np.average(self.u_tun_array, axis=0)
    
    
    def uTunMean(self):
        """Returns the average tunnel voltage of one stm image."""
        
        if self.uTunLine() is not None:
            return np.mean(self.uTunLine())
        else:
            self.meta_id = gwyddion.getMetaIDs(self.container)[0]
            try:
                self.u_tun_string = self.container[self.meta_id]['Tip voltage']
                return re.sub('[^\d.]+', '', self.u_tun_string.replace(',', '.'))
            except(KeyError):  
                return None
    
    
    def saveUTunData(self, path):
        """Save the tunnel voltage data to a file."""
        
        self.dat_utun_file = os.path.join(path, str(self.id) + "_utun." + config.dat_type_out)
        np.savetxt(self.dat_utun_file, stm.uTunLine(self), delimiter = ';')
        
        if config.dat_type_igor:
            self.file_utun_igor = os.path.join(path, 'g' + str(self.id) + '_ori.ut0')
            shutil.move(self.dat_utun_file, self.file_utun_igor)
    
    
    def iTun(self):
        """Numpy array of all tunnel current values in the stm image."""
        
        self._itun_ch_ids = spm.findChannel(self, ["*Current*"])
        
        if len(self._itun_ch_ids) is not 0:
            return self.convertNP(self._itun_ch_ids[0])
        else:
            return np.full((512, 512), 0)
    
    
    def iTunMean(self):
        """Return averaged tunnel current."""
        
        return np.mean(self.iTun())
    
    
    def iTunDev(self):
        """Return standard deviation of tunnel current."""
        
        return np.std(self.i_tun)



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
        
        return self.returnDataChTitle(self._ecell_ch_id)
    
    
    def returnIcellChannel(self):
        """Return cell current channel."""
        
        return self.returnDataChTitle(self._icell_ch_id)
    
    
    def eCellData(self):
        """Electrochemical cell potential data.
        
        So the 512x512 np array is getting averaged to 512x1,
        it's resolution is determined by the line time of the 
        stm image (50 - 300 ms). This could be improved in future by
        combination of forward and backward image data.
        """
        
        if len(self._ecell_ch_id) > 0:
            self.e_cell_data = self.convertNP(self._ecell_ch_id[0])
            return np.average(self.e_cell_data, axis=0).tolist()
        else:
            return None
    
    
    def iCellData(self):
        """Electrochemical cell current data.
        
        So the 512x512 np array is getting averaged to 512x1,
        it's resolution is determined by the line time of the 
        stm image (50 - 300 ms). This could be improved in future by
        combination of forward and backward image data.
        """
        
        if len(self._icell_ch_id) > 0:
            self.i_cell_data = self.convertNP(self._icell_ch_id[0])
            return np.average(self.i_cell_data, axis=0).tolist()
        else:
            return None
    
    
    def saveEcData(self, path):
        """Save electrochemical cell potential to data file."""
        
        self.ec_data_file = os.path.join(path, str(self.id) + "_ec" + "." + config.dat_type_out)
        np.savetxt(self.ec_data_file, ecstm.eCellData(self), delimiter=';')
        
        if config.dat_type_igor:
            self.file_ec_igor = os.path.join(path, 'g' + str(self.id) + '_ori.ec0')
            shutil.move(self.ec_data_file, self.file_ec_igor)
    
    
    def saveIcData(self, path):
        """Save electrochemical cell current to data file."""
        
        self.ic_data_file = os.path.join(path, str(self.id) + "_ic" + "." + config.dat_type_out)
        np.savetxt(self.ic_data_file, self.icell, delimiter=';')
        
        if config.dat_type_igor:
            self.file_ic_igor = os.path.join(path, 'g' + str(self.id) + '_ori.ic0')
            shutil.move(self.ic_data_file, self.file_ic_igor)
    

class afm(spm):
    """Atomic force mircoscopy."""
    
    def __init__(self, file, **kwargs):
        spm.__init__(self, file, **kwargs)
    
    
    def returnPhaseCh(self):
        """Return phase channel."""
        
        return self.findChannel(["*Phase*"])
    
    
    def returnPhaseFwdCh(self):
        """Return forward phase channel."""
        self.pat_fwd = ['^.*[F||f]orward.*$', '^.*[R||r]ight.*$', '.*fwd.*']
        for ch in self.returnPhaseCh():
            self.gen = (ch for pat in self.pat_fwd if re.match(pat, self.returnDataChTitle(ch)))
            for pat in self.gen:
                return ch
    
    
    def returnPhaseBwdCh(self):
        """Return backward phase channel."""
        
        self.pat_bwd = ['^.*[B||b]ackward.*$', '^.*[L||l]eft.*$', '.*bwd.*']
        for ch in self.returnPhaseCh():
            self.gen = (ch for pat in self.pat_fwd if re.match(pat, self.returnDataChTitle(ch)))
            for pat in self.gen:
                return ch
    
    
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
