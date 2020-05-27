"""log.py

Part of proespm: Log creation.

(C) Copyright Nicolas Bock, licensed under GPL v3 
See LICENSE or http://www.gnu.org/licenses/gpl-3.0.html
"""

import config
import time
import sys
import os


class logging(object):
    """Represents one log session."""
    
    def __init__(self):
        self.logs = []
        self.logP(8, 'Log started')
    
    
    def logP(self, log_priority, text = ""):
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
                self.flushDelay()
            else:
                self.log_line = "[" + time.strftime('%Y-%M-%d %X') + "]" + ": " + text
                self.logs.append(self.log_line)
                print(self.log_line)
                self.flushDelay()
    
    
    def saveLog(self, log_file_path, log_f_name):
        """Function to write all log informations in a log file.
        
        Args:
            log_file_path (str): Path where log file should be saved.
            log_f_name (str): Information you would like to be logged.
        """
        
        with open(os.path.join(log_file_path, log_f_name), 'wt') as self.f:
            for self.line in self.logs:
                self.f.writelines("[" + time.strftime('%Y-%M-%d %X') + "]" + ": " + self.line + "\n")
    
    
    def flushDelay(self): 
        """Flush the Python terminal buffer.
        
        This is doine with a certain waiting time (default 10 ms), 
        this avoids synchronization problems.
        """
        
        sys.stdout.flush()
        time.sleep(0.01) 
