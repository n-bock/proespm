"""gwyddion.py

Part of proespm: Gwyddion helper functions.

(C) Copyright Nicolas Bock, licensed under GPL v3 
See LICENSE or http://www.gnu.org/licenses/gpl-3.0.html
"""

from util import importHelper, WIN32_helper

importHelper()

if 'path_gwyddion' not in locals():
    WIN32_helper()

import gwy
import gwyutils
import config


def getMetaIDs(container):
    """Returns the IDs where meta data is stored within a Gwyddion file."""
    
    return list(filter(lambda x: 'Container' in type(container[x]).__name__, container.keys()))



def saveImageFile(container, save_file):
    """Saves image file through Gwyddion, with optional file dialog.
    
    Args:
        container (gwy-container): Gwyddion container which will be exported.
        save_file (str): Filepath how the file will be saved.
    """
    
    if config.export_image_dialog:
        gwy.gwy_file_save(container, save_file, gwy.RUN_INTERACTIVE)
    else:
        gwy.gwy_file_save(container, save_file, gwy.RUN_NONINTERACTIVE)
