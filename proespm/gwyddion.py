"""gwyddion.py

Part of proespm: Gwyddion helper functions.

(C) Copyright Nicolas Bock, licensed under GPL v3
See LICENSE or http://www.gnu.org/licenses/gpl-3.0.html
"""

import os
import time
from datetime import datetime
import config
import data
from util import import_helper, win32_helper

import_helper()

if "path_gwyddion" not in locals():
    win32_helper()

# pylint: disable=wrong-import-position
import gwy

# pylint: enable=wrong-import-position


def get_meta_ids(container):
    """Returns the IDs where meta data is stored within a Gwyddion file."""

    return [i for i in container.keys() if "Container" in type(container[i]).__name__]


def save_image_file(container, save_file):
    """Saves image file through Gwyddion, with optional file dialog.

    Args:
        container (gwy-container): Gwyddion container which will be exported.
        save_file (str): Filepath how the file will be saved.
    """

    if config.export_image_dialog:
        gwy.gwy_file_save(container, save_file, gwy.RUN_INTERACTIVE)
    else:
        gwy.gwy_file_save(container, save_file, gwy.RUN_NONINTERACTIVE)


def mul_split(file_path):
    """Splits all data channels into single gwy files"""

    m_id = data.m_id(file_path)
    dir_path = os.path.dirname(os.path.abspath(file_path))
    con = gwy.gwy_app_file_load(file_path)
    ch_ids = gwy.gwy_app_data_browser_get_data_ids(con)

    def inner(_id):  # pylint: disable=missing-docstring
        new_container = gwy.Container()
        gwy.gwy_app_data_browser_add(new_container)
        gwy.gwy_app_data_browser_copy_channel(con, _id, new_container)
        file_name = str(m_id) + "_" + str(_id) + ".gwy"
        file_out = os.path.join(dir_path, file_name)
        meta_id = get_meta_ids(new_container)[0]
        time_extract = new_container[meta_id]["Date"]
        time_reformat = datetime.strptime(time_extract, "%Y-%m-%d %H:%M:%S")
        gwy.gwy_app_file_write(new_container, file_out)
        time_sec = time.mktime(time_reformat.timetuple())
        os.utime(file_out, (time_sec, time_sec))
        return file_out

    return [inner(ch_id) for ch_id in ch_ids]
