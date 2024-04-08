"""spm.py

Part of proespm: Scanning probe microscopy data.

(C) Copyright Nicolas Bock, licensed under GPL v3
See LICENSE or http://www.gnu.org/licenses/gpl-3.0.html
"""

import shutil
import re
import os
import numpy as np
import config
import gwyddion
from data import Data
from ec import Ec
from util import import_helper, win32_helper

import_helper()

if "path_gwyddion" not in locals():
    win32_helper()

# pylint: disable=wrong-import-position
import gwy
import gwyutils

# pylint: enable=wrong-import-position


class Spm(Data):
    """Represents any SPM data which can be handled with Gwyddion software.

    The file format should be supported by the Gwyddion software.
    opt. arguments (str): tip, electrolyte, we, ce, re

    Args:
        file (str): Path to ecstm file.
    """

    def __init__(self, m_file, **kwargs):
        self.surface = None
        self.tip = None
        Data.__init__(self, m_file, **kwargs)
        self.set_settings()
        self.container = gwy.gwy_file_load(self.m_file, gwy.RUN_NONINTERACTIVE)
        gwy.gwy_app_data_browser_add(self.container)
        self.img_topo_fwd = None
        self.img_topo_bwd = None
        self.topo_fwd_ch = self.return_topo_fwd_ch()
        self.topo_bwd_ch = self.return_topo_bwd_ch()
        self.size = None
        self.rotation = None
        self.line_time = None
        self.bias = None
        self.current = None
        self.xoffset = None
        self.yoffset = None
        self.scan_duration = None
        self.extract_meta(gwyddion.get_meta_ids(self.container)[0])

    def extract_meta(self, meta_id):
        """Extracts all the meta data from the gwyddion container.

        Args:
            meta_id: Id where the meta data can be found.
        """

        pattern = {
            "size": [
                "IMAGE CONTROL::Scan:Size::Scan Control::Scan size",
                "Image size",
            ],
            "rotation": [
                "IMAGE CONTROL::Scan:Size::Scan Control::Scan Rotation",
                "Rotation",
                "Tilt",
            ],
            "line_time": [
                "IMAGE CONTROL::Scan:Size::Scan Control::Line time",
                "Time/Line",
            ],
            "type": [
                "Op. mode",
                "Image mode",
                "Mode",
            ],
            "bias": ["Bias"],
            "current": ["Current"],
            "xoffset": ["X-Offset"],
            "yoffset": ["Y-Offset"],
            "scan_duration": ["Scan duration"],
        }
        for k, pat_list in pattern.iteritems():
            for pat in pat_list:
                try:
                    setattr(self, k, self.container[meta_id][pat])
                except KeyError:
                    pass

    def set_settings(self):
        """Sets the setting which are supplied by the user editable config file."""

        self.settings = gwy.gwy_app_settings_get()
        self.settings["/module/linematch/direction"] = int(gwy.ORIENTATION_HORIZONTAL)
        self.settings["/module/linematch/do_extract"] = config.do_extract
        self.settings["/module/linematch/do_plot"] = config.do_plot
        self.settings["/module/linematch/method"] = config.method
        self.settings["/module/linematch/masking"] = config.masking
        self.settings["/module/linematch/max_degree"] = config.max_degree
        self.settings["/module/median-bg/radius"] = config.radius
        self.settings["/module/median-bg/do_extract"] = config.do_extract
        self.settings["/module/rotate/angle"] = config.angle
        self.settings["/module/rotate/create_mask"] = config.create_mask
        self.settings["/module/rotate/interp"] = config.rotate_interp
        self.settings["/module/rotate/resize"] = config.resize
        self.settings["/module/rotate/show_grid"] = config.show_grid
        self.settings["/module/scale/interp"] = config.scale_interp
        self.settings["/module/scale/proportional"] = config.proportional
        self.settings["/module/scale/aspectratio"] = config.aspectratio
        self.settings["/module/asciiexport/add-comment"] = config.add_comment

    def find_channel(self, match_list):
        """Finds the right data channel within a Gwyddion container.

        Args:
            container: Gwyddion container with several data channels.
            match_list (list): Names which will be searched. e.g. topography

        Returns:
            chn_ids (list): List of channel IDs.
        """

        self.ch_ids = []
        for self._data_title in match_list:
            self._match_ch = gwy.gwy_app_data_browser_find_data_by_title(
                self.container, self._data_title
            )
            self.ch_ids.extend(self._match_ch)

        return self.ch_ids

    def return_data_ch_titles(self):
        """Returns data channel titel"""

        self.ch = gwy.gwy_app_data_browser_get_data_ids(self.container)
        return [self.container["/" + str(i) + "/data/title"] for i in self.ch]

    def return_match_ch(self, pattern, channels):
        """Returns topography channels

        Args:
            pattern: Pattern list, which identifies the desired channel.
            channels: List of channels.

        Returns:
            ch (list): Channel ids.
        """

        for pat in pattern:
            self.topo_ch = [ch for ch in channels if re.search(pat, ch)]
            if len(self.topo_ch) > 0:
                break

        return [
            gwy.gwy_app_data_browser_find_data_by_title(self.container, ch)
            for ch in self.topo_ch
        ]

    def return_topo_fwd_ch(self):
        """Returns tophography forward channel"""

        self.ch_list = self.return_data_ch_titles()

        return self.return_match_ch(
            [
                r"^Topo|Z.*[Ff]orward.*",
                r"^Topo|Z.*[Rr]ight.*",
                r"^Topo|Z.*[Ff]wd.*",
                r"(\d*)",
            ],
            self.ch_list,
        )

    def return_topo_bwd_ch(self):
        """Returns topography backwards channel"""

        self.ch_list = self.return_data_ch_titles()

        return self.return_match_ch(
            [r"^Topo|Z.*[Bb]ackward.*$", r"^Topo|Z.*[Ll]eft.*$", r"^Topo|Z.*[Bb]wd.*$"],
            self.ch_list,
        )

    def return_file_name(self, data):
        """Returns the file name Igor friendly.

        This is needed to make the SPM data functional with the IGOR
        image processing addon.

        Example:
            "blahblah12345.xzy" --> "g1234_ori.t" - t: topo
            "BLAH111_123456.BLA" --> "g123456_ori.t" - t: topo

        Args:
            data (str): Path to file.
        """

        self.name = os.path.basename(data)

        self.pat_out = [
            r"^[a-z,A-Z]*.(\d{1,6})\..{3}$",
            r"g\1_ori.t",
            r"^[a-z,A-Z]*\d*_(\d{1,6})\..{3}$",
            r"g\1_ori.t",
        ]
        for pat in range(0, len(self.pat_out), 2):
            self.name = re.sub(
                self.pat_out[pat], self.pat_out[pat + 1], self.name
            )  # (0,1), (2,3), (4,5) ...
            # a pattern match has occured (should only ever be ONE)
            if os.path.basename(data) != self.name:
                break

        return self.name

    def convert_np(self, channel_id):
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

    def process_topo(self, data_ch_id):
        """Processes the data with Gwyddion Python module.

        Gwyddion topography processing functions: see config file.
        Before saving the image, the colorrange needs adjustment. The
        colorrange settings are stored in the container for each spm
        file. (see online gwyfile-format)

        Args:
            data_ch_id (int): Channel of the container should be processed.
        """
        for ch in data_ch_id:
            gwy.gwy_app_data_browser_select_data_field(self.container, ch)

            self.run_gwy_func = {gwy.RUN_IMMEDIATE: config.run_gwy_immediate_func}
            for k, funcs in self.run_gwy_func.iteritems():
                for func in funcs:
                    gwy.gwy_process_func_run(func, self.container, k)

            self.match_ch_topo = "/" + str(ch) + "/base/range-type"
            self.container[self.match_ch_topo] = 2

    def process_topo_fwd(self):
        """Process forward topography"""

        if self.topo_fwd_ch:
            for ch in self.topo_fwd_ch:
                self.process_topo(ch)

    def process_topo_bwd(self):
        """Process backward topography"""

        if self.topo_bwd_ch:
            self.process_topo(self.topo_bwd_ch[0])

    def save_topo_fwd_image(self, path):
        """Save forward topography image file.

        Args:
            path (str): File path where the file should be save.
        """

        self.img_topo_fwd = os.path.join(
            path, str(self.m_id) + "_tf." + config.img_type_out
        )
        gwyddion.save_image_file(self.container, self.img_topo_fwd)

    def save_topo_bwd_image(self, path):
        """Save backward topography image file.

        Args:
            path (str): File path where the file should be save.
        """

        self.img_topo_bwd = os.path.join(
            path, str(self.m_id) + "_tb." + config.img_type_out
        )
        gwyddion.save_image_file(self.container, self.img_topo_bwd)

    def save_topo_fwd_data(self, path):
        """Save forward topography data file.

        Args:
            path (str): File path where the file should be save.
        """

        self.dat_topo_fwd = os.path.join(
            path, str(self.m_id) + "_fwd." + config.dat_type_out
        )
        gwy.gwy_file_save(self.container, self.dat_topo_fwd, gwy.RUN_NONINTERACTIVE)

        if config.dat_type_igor:
            self.file_igor = os.path.join(path, "g" + str(self.m_id) + "_ori.tf0")
            shutil.move(self.dat_topo_fwd, self.file_igor)

    def save_topo_bwd_data(self, path):
        """Save backward topography data file.

        Args:
            path (str): File path where the file should be save.
        """

        self.dat_topo_bwd = os.path.join(
            path, str(self.m_id) + "_bwd." + config.dat_type_out
        )
        gwy.gwy_file_save(self.container, self.dat_topo_bwd, gwy.RUN_NONINTERACTIVE)

        if config.dat_type_igor:
            self.file_igor = os.path.join(path, "g" + str(self.m_id) + "_ori.tb0")
            shutil.move(self.dat_topo_bwd, self.file_igor)

    def spm_pixel_size(self):
        """Returns the Image Size of the spm file in pixels."""

        self.key = gwy.gwy_app_get_data_key_for_id(0)
        self.name = gwy.gwy_name_from_key(self.key)
        self.data_tmp = gwyutils.data_field_data_as_array(self.container[self.name])

        return np.shape(self.data_tmp)

    def flush_memory(self):
        """Deletes all the data channels in a Gwyddion container.

        This is needed as the memory will fill up quickly and a C memory
        error will occur.
        """

        for data_ch_id in gwy.gwy_app_data_browser_get_data_ids(self.container):
            self.key = gwy.gwy_app_get_data_key_for_id(data_ch_id)
            self.container.remove(self.key)


class Stm(Spm):
    """Represents any stm data. Compared to spm data it also stores
    tunnel current and tunnel voltage"""

    def __init__(self, m_file, **kwargs):
        Spm.__init__(self, m_file, **kwargs)
        self.i_tun = self.return_i_tun_mean()
        self.u_tun = self.return_u_tun_mean()

    def u_tun_line(self):
        """Returns the average tunnel voltage value for each stm line.

        So the 512x512 np array is getting averaged to 512x1,
        it's resolution is determined by the line time of the
        stm image (50 - 300 ms).
        """

        self._utun_ch_ids = Spm.find_channel(self, ["*Utun*"])
        if len(self._utun_ch_ids) != 0:
            self.u_tun_array = self.convert_np(self._utun_ch_ids[0])
            return np.average(self.u_tun_array, axis=0)

    def return_u_tun_mean(self):
        """Returns the average tunnel voltage of one stm image."""

        if self.u_tun_line() is not None:
            return np.mean(self.u_tun_line())
        else:
            self.meta_id = gwyddion.get_meta_ids(self.container)[0]
            try:
                self.u_tun_string = self.container[self.meta_id]["Tip voltage"]
                return re.sub(r"[^\d.]+", "", self.u_tun_string.replace(",", "."))
            except KeyError:
                return None

    def save_u_tun_data(self, path):
        """Save the tunnel voltage data to a file."""

        self.dat_utun_file = os.path.join(
            path, str(self.m_id) + "_utun." + config.dat_type_out
        )
        np.savetxt(self.dat_utun_file, Stm.u_tun_line(self), delimiter=";")

        if config.dat_type_igor:
            self.file_utun_igor = os.path.join(path, "g" + str(self.m_id) + "_ori.ut0")
            shutil.move(self.dat_utun_file, self.file_utun_igor)

    def return_i_tun(self):
        """Numpy array of all tunnel current values in the stm image."""

        self._itun_ch_ids = Spm.find_channel(self, ["*Current*"])

        if len(self._itun_ch_ids) != 0:
            return self.convert_np(self._itun_ch_ids[0])
        else:
            return np.full((512, 512), 0)

    def return_i_tun_mean(self):
        """Return averaged tunnel current."""

        return np.mean(self.return_i_tun())

    def i_tun_dev(self):
        """Return standard deviation of tunnel current."""

        return np.std(self.i_tun)


class Ecstm(Stm, Ec):
    """Ecstm measurement data."""

    def __init__(self, m_file, **kwargs):
        Stm.__init__(self, m_file, **kwargs)
        Ec.__init__(self, m_file, **kwargs)
        self._ecell_ch_id = Spm.find_channel(self, ["*VEC*"])
        self._icell_ch_id = Spm.find_channel(self, ["*IEC*"])
        self.icell = self.return_i_cell_data()
        self.file_ec_igor = None
        self.file_ic_igor = None

    def return_e_cell_ch(self):
        """Return cell potential channel."""

        return self.return_data_ch_title(self._ecell_ch_id)

    def return_i_cell_ch(self):
        """Return cell current channel."""

        return self.return_data_ch_title(self._icell_ch_id)

    def return_e_cell_data(self):
        """Electrochemical cell potential data.

        So the 512x512 np array is getting averaged to 512x1,
        it's resolution is determined by the line time of the
        stm image (50 - 300 ms).
        """

        if len(self._ecell_ch_id) != 0:
            self.e_cell_data = self.convert_np(self._ecell_ch_id[0])
            return np.average(self.e_cell_data, axis=0).tolist()
        else:
            return None

    def return_i_cell_data(self):
        """Electrochemical cell current data.

        So the 512x512 np array is getting averaged to 512x1,
        it's resolution is determined by the line time of the
        stm image (50 - 300 ms).
        """

        if len(self._icell_ch_id) != 0:
            self.i_cell_data = self.convert_np(self._icell_ch_id[0])
            return np.average(self.i_cell_data, axis=0).tolist()
        else:
            return None

    def save_ec_data(self, path):
        """Save electrochemical cell potential to data file."""

        self.ec_data_file = os.path.join(
            path, str(self.m_id) + "_ec" + "." + config.dat_type_out
        )
        np.savetxt(self.ec_data_file, self.return_e_cell_data(), delimiter=";")

        if config.dat_type_igor:
            self.file_ec_igor = os.path.join(path, "g" + str(self.m_id) + "_ori.ec0")
            shutil.move(self.ec_data_file, self.file_ec_igor)

    def save_ic_data(self, path):
        """Save electrochemical cell current to data file."""

        self.ic_data_file = os.path.join(
            path, str(self.m_id) + "_ic" + "." + config.dat_type_out
        )
        np.savetxt(self.ic_data_file, self.icell, delimiter=";")

        if config.dat_type_igor:
            self.file_ic_igor = os.path.join(path, "g" + str(self.m_id) + "_ori.ic0")
            shutil.move(self.ic_data_file, self.file_ic_igor)


class Afm(Spm):
    """Atomic force mircoscopy."""

    def __init__(self, m_file, **kwargs):
        Spm.__init__(self, m_file, **kwargs)

    def return_phase_ch(self):
        """Return phase channel."""

        return self.find_channel(["*Phase*"])

    def return_phase_fwd_ch(self):
        """Return forward phase channel."""

        self.pat_fwd = [r"^.*[F||f]orward.*$", r"^.*[R||r]ight.*$", r".*fwd.*"]
        for ch in self.return_phase_ch():
            for pat in self.pat_fwd:
                if re.match(pat, self.return_data_ch_title(ch)):
                    return ch

    def return_phase_bwd_ch(self):
        """Return backward phase channel."""

        self.pat_bwd = [r"^.*[B||b]ackward.*$", r"^.*[L||l]eft.*$", r".*bwd.*"]
        for ch in self.returnPhaseCh():
            for pat in self.pat_bwd:
                if re.match(pat, self.return_data_ch_title(ch)):
                    return ch

    def save_phase_fwd_image(self, path):
        """Save forward phase to image file."""

        gwy.gwy_app_data_browser_select_data_field(
            self.container, self.return_phase_fwd_ch()
        )
        self.img_phase_fwd = os.path.join(
            path, str(self.m_id) + "_pf." + config.img_type_out
        )
        gwyddion.save_image_file(self.container, self.img_phase_fwd)

    def save_phase_bwd_image(self, path):
        """Save backward phase to image file."""

        gwy.gwy_app_data_browser_select_data_field(
            self.container, self.return_phase_bwd_ch()
        )
        self.img_phase_bwd = os.path.join(
            path, str(self.m_id) + "_pb." + config.img_type_out
        )
        gwyddion.save_image_file(self.container, self.img_phase_bwd)
