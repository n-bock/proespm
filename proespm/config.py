"""config

Part of proespm: Import of the yml configuration.

(C) Copyright Nicolas Bock, licensed under GPL v3
See LICENSE or http://www.gnu.org/licenses/gpl-3.0.html
"""

import os
import sys
import yaml

config_file = os.path.abspath(
    os.path.join(os.path.join(sys.path[0], os.pardir), "config.yml")
)
with open(config_file) as f:
    config = yaml.safe_load(f)

is_single_f = config["import"]["single file import"]
is_labj = config["import"]["labjournal available"]
is_labj_prompt = config["import"]["ask for labjournal"]
m_type = config["import"]["fallback method"]
allowed_file_types = config["import"]["allowed file types"]
labj_ws_name = config["import"]["labjournal worksheet name"]

dialog_labj = {
    "title": "Open labjournal",
    "initialdir": config["import"]["initial directory prompt labjournal"],
    "filetypes": [("Excel after 2010 ", ".xlsx")],
}

dialog_files = {
    "title": "Open file(s)",
    "initialdir": config["import"]["initial directory prompt files"],
    "filetypes": [("All files", ".*")],
}

run_gwy_immediate_func = config["spm"]["immediate functions"]
do_extract = config["spm"]["align rows"]["do extract"]
do_plot = config["spm"]["align rows"]["do plot"]
method = config["spm"]["align rows"]["method"]
masking = config["spm"]["align rows"]["masking"]
max_degree = config["spm"]["align rows"]["max degree"]
radius = config["spm"]["median background"]["radius"]
do_extract = config["spm"]["median background"]["do extract"]
angle = config["spm"]["rotate"]["angle"]
create_mask = config["spm"]["rotate"]["create mask"]
rotate_interp = config["spm"]["rotate"]["interp"]
resize = config["spm"]["rotate"]["resize"]
show_grid = config["spm"]["rotate"]["show grid"]
scale_interp = config["spm"]["scale"]["interp"]
proportional = config["spm"]["scale"]["proportional"]
aspectratio = config["spm"]["scale"]["aspectratio"]
add_comment = config["spm"]["asciiexport"]["add comment"]

is_html_out = config["export"]["create html report"]
export_image_dialog = config["export"]["image export modification dialog"]
server_path = config["export"]["server path"]
hierarchy = config["export"]["move html to parent and rest in subfolder"]
force_override = config["export"]["Force overwrite excisting files"]
dat_type_out = config["export"]["export data type"]
dat_type_igor = config["export"]["export igor friendly"]
img_type_out = config["export"]["export image type"]
log_level = config["export"]["log level"]
log_f_name = config["export"]["log file name"]

win32_search_for = config["system"]["win32 gwy name"]
win32_path_gwyddion_hint = config["system"]["win32 gwy path hint"]
win32_gwyutils_rel_path = config["system"]["win32 gwyutils rel path"]
linux_gwyutils_path = config["system"]["linux gwyutils path"]
debug_modus = config["system"]["debug modus"]
