"""sem.py

Part of proespm: Scanning electron microscopy data.

(C) Copyright Nicolas Bock, licensed under GPL v3 
See LICENSE or http://www.gnu.org/licenses/gpl-3.0.html
"""

from util import importHelper, WIN32_helper

importHelper()

if 'path_gwyddion' not in locals():
    WIN32_helper()

import gwy
import gwyddion
import config
import shutil
import re
import os
import numpy as np
from data import data


class sem(data):
    """Represents any SEM data which can be handled with Gwyddion software.
        
    Args:
        file (str): Path to sem file. The file format should be supported 
                    by the Gwyddion software.
        **kwargs (str): optional arguments like e.g. surface, remark
    """
    
    def __init__(self, file, **kwargs):
        self.surface = None
        data.__init__(self, file, **kwargs)
        self.container = gwy.gwy_file_load(self.file, gwy.RUN_NONINTERACTIVE)
        gwy.gwy_app_data_browser_add(self.container)
        self.channel_id = gwy.gwy_app_data_browser_find_data_by_title(self.container, '*SE*')[0]
        gwy.gwy_app_data_browser_select_data_field(self.container, self.channel_id)
        self.extractMeta(gwyddion.getMetaIDs(self.container)[0])
    
    
    def extractMeta(self, meta_id):
        """Extract Meta data of SEM file.
        
        Args:
            meta_id (int): Gwyddion ID where meta data is stored.
        """
        
        pattern = {'self.hv': ['EBeam::HV'],
                   'self.dwell': ['EScan::Dwell'],
                   'self.frame_time': ['EScan::FrameTime'],
                   'self.frame_size': ['EScan::HorFieldsize']}
        for k, pat_list in pattern.iteritems():
            for pat in pat_list:
                try:
                    exec("{} = self.container[{}]['{}']".format(k, meta_id, pat))
                except(KeyError):
                    pass
    
    
    def saveImage(self, path):
        """Saves SEM data to image file.
        
        Args:
            path (str): Path where image will be stored.
        """
        
        self.img = os.path.join(path, str(self.id) + '.' + config.img_type_out)
        self.match_ch_topo = '/' + str(self.channel_id) + '/base/range-type'
        self.container[self.match_ch_topo] = 2
        gwyddion.saveImageFile(self.container, self.img)

