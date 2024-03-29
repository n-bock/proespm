﻿"""html.py

Part of proespm: Create HTML report.

(C) Copyright Nicolas Bock, licensed under GPL v3
See LICENSE or http://www.gnu.org/licenses/gpl-3.0.html
"""

import os
import re
import config
from genshi.template import TemplateLoader


def create_html_head(src_dir):
    """Creates HTML header for genshi template.

    Dictionary which can be processed by genshi to create HTML a
    navigation bar.

    Args:
        src_dir (str): Source directory where all raw files are stored.
    """

    try:
        # Create overlap between server path and source directory
        overlap = re.search(r".*\/(.*)$", config.server_path).group(1)
        trimmed_src_dir = re.search(overlap + "(.*)$", src_dir).group(1)
        link_files = config.server_path + trimmed_src_dir
        if config.hierarchy:
            link_images = link_files + "/_png/"
            link_ascii = link_files + "/_data/"
        else:
            link_images = link_files
            link_ascii = link_files

        link_proc_log = link_files + "/" + config.log_f_name
        link_userconfig = link_files + "/_config.log"
        head = [
            [link_files, "Open the folder where data files are stored", "Data Folder"],
            [link_images, "Open the folder where image files are stored", "Images"],
            [link_ascii, "Open the folder where ASCII files are stored", "ASCII files"],
            [link_proc_log, "Open processingLog file", "Log File"],
            [link_userconfig, "Open userConfigLog file", "Input Parameters"],
            [
                "https://github.com/n-bock/proespm",
                "Fork code from Github",
                "Fork the code!",
            ],
        ]
    except (AttributeError, IndexError):
        head = [
            ["#", "Open the folder where data files are stored", "Data Folder"],
            ["#", "Open the folder where image files are stored", "Images"],
            ["#", "Open the folder where ASCII files are stored", "ASCII files"],
            ["#", "Open processingLog file", "Log File"],
            ["#", "Open userConfigLog file", "Input Parameters"],
            [
                "https://github.com/n-bock/proespm",
                "Fork code from Github",
                "Fork the code!",
            ],
        ]

    return head


def create_html(src_dir, proc_dir, list_classes):
    """Creates HTML file by using the template and all processed data.

    Args:
        src_dir (str): Source directory where all raw files are stored.
        proc_dir (str): Directory where files are processed.
        list_classes (list): List of data classes.
    """

    templates_dir = os.getcwd()
    loader = TemplateLoader(templates_dir, auto_reload=False)
    tmpl = loader.load("template.html")

    file_name = os.path.basename(os.path.normpath(src_dir)) + "_report.html"
    file_path = os.path.join(proc_dir, file_name)

    stream = tmpl.generate(title=file_name, src_dir=src_dir, list_classes=list_classes)

    with open(file_path, "wb") as f:
        for output in stream.serialize("html"):
            f.write(output)
