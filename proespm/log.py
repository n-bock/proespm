"""log.py

Part of proespm: Log creation.

(C) Copyright Nicolas Bock, licensed under GPL v3
See LICENSE or http://www.gnu.org/licenses/gpl-3.0.html
"""
from __future__ import print_function
import time
import sys
import os
import config


class Logging(object):
    """Represents one log session."""

    def __init__(self):
        self.logs = []
        self.log_p(8, "Log started")

    def log_p(self, log_priority, text=""):
        """Write a certain information in a log file and also print locally.

        Each information can be assign a priority which desides if the
        information is printed.

        Args:
            log_priority (int): Determines how much is log is acquired (10 = everything)
            text (str): Information you would like to be logged.
        """

        if config.log_level >= log_priority:
            if text == "":
                self.log_line = "\n"
                self.logs.append(self.log_line)
                print("")
                self.flush_delay()
            else:
                self.log_line = "[" + time.strftime("%Y-%M-%d %X") + "]" + ": " + text
                self.logs.append(self.log_line)
                print(self.log_line)
                self.flush_delay()

    def save_log(self, log_file_path, log_f_name):
        """Function to write all log informations in a log file.

        Args:
            log_file_path (str): Path where log file should be saved.
            log_f_name (str): Information you would like to be logged.
        """

        with open(os.path.join(log_file_path, log_f_name), "wt") as self.f:
            for self.line in self.logs:
                self.f.writelines(
                    "[" + time.strftime("%Y-%M-%d %X") + "]" + ": " + self.line + "\n"
                )

    def flush_delay(self):
        """Flush the Python terminal buffer."""

        sys.stdout.flush()
        time.sleep(0.01)
