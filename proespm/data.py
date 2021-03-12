"""data.py

Part of proespm: General data and image types.

(C) Copyright Nicolas Bock, licensed under GPL v3
See LICENSE or http://www.gnu.org/licenses/gpl-3.0.html
"""

import re
import os
import datetime


def m_id(m_file):
    """Creates ID for each measurement from data file name.

    For SM4 and NID files IDs will be created from the digits. For all other
    file types just the file ending will be stripped.

    Args:
        file (string): Path to the data file.
    """

    if m_file.endswith("SM4"):
        x = int(re.search(r".*(\d{4})\.", m_file).group(1))
    elif m_file.endswith("nid"):
        x = int(re.search(r".*(\d{4})\..{3}$", m_file).group(1))
    else:
        x = re.search(r".*(\/|\\)(.*)\.\S{3}", m_file).group(2)

    return str(x)


class Data(object):
    """Represents any data. As optional arguments surface, remarks etc. is useful!"""

    def __init__(self, m_file, **kwargs):
        self.remark = "nan"
        self.m_file = m_file
        self.m_id = m_id(self.m_file)
        self.path = os.path.dirname(os.path.abspath(self.m_file))
        self.datetime = datetime.datetime.fromtimestamp(
            os.path.getmtime(self.m_file)
        ).strftime("%Y-%m-%d %H:%M:%S")
        self.meta = {}
        for key, value in kwargs.iteritems():
            self.var_name = "self." + key
            exec("%s = '%s'" % (self.var_name, value))
            self.meta[key] = value

    def __str__(self):
        return self.m_id

    def return_path(self):
        """Return path to data file."""

        return "file:///" + "/".join(self.m_file.split("/")[1:])


class Image(Data):
    """Represents any image."""

    def __init__(self, m_file, **kwargs):
        Data.__init__(self, m_file, **kwargs)
        self.surface = None
