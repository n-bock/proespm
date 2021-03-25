"""sem.py

Part of proespm: Scanning electron microscopy data.

(C) Copyright Nicolas Bock, licensed under GPL v3
See LICENSE or http://www.gnu.org/licenses/gpl-3.0.html
"""

import os
import gwyddion
import config
from data import Data
from util import import_helper, win32_helper

import_helper()

if "path_gwyddion" not in locals():
    win32_helper()

# pylint: disable=wrong-import-position
import gwy

# pylint: enable=wrong-import-position


class Sem(Data):
    """Represents any SEM data which can be handled with Gwyddion software.

    Args:
        file (str): Path to sem file. The file format should be supported
                    by the Gwyddion software.
        **kwargs (str): optional arguments like e.g. surface, remark
    """

    def __init__(self, m_file, **kwargs):
        self.surface = None
        Data.__init__(self, m_file, **kwargs)
        self.container = gwy.gwy_file_load(self.m_file, gwy.RUN_NONINTERACTIVE)
        gwy.gwy_app_data_browser_add(self.container)
        self.channel_id = gwy.gwy_app_data_browser_find_data_by_title(
            self.container, "*SE*"
        )[0]
        gwy.gwy_app_data_browser_select_data_field(self.container, self.channel_id)
        self.extract_meta(gwyddion.get_meta_ids(self.container)[0])

    def extract_meta(self, meta_id):
        """Extract Meta data of SEM file.

        Args:
            meta_id (int): Gwyddion ID where meta data is stored.
        """

        pattern = {
            "hv": "EBeam::HV",
            "dwell": "EScan::Dwell",
            "frame_time": "EScan::FrameTime",
            "frame_size": "EScan::HorFieldsize",
        }

        for k, pat in pattern.iteritems():
            try:
                setattr(self, k, self.container[meta_id][pat])
            except KeyError:
                pass

    def save_image(self, path):
        """Saves SEM data to image file.

        Args:
            path (str): Path where image will be stored.
        """

        self.img = os.path.join(path, str(self.m_id) + "." + config.img_type_out)
        self.match_ch_topo = "/" + str(self.channel_id) + "/base/range-type"
        self.container[self.match_ch_topo] = 2
        gwyddion.save_image_file(self.container, self.img)
