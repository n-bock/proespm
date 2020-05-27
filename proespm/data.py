"""data.py

Part of proespm: General data and image types.

(C) Copyright Nicolas Bock, licensed under GPL v3 
See LICENSE or http://www.gnu.org/licenses/gpl-3.0.html
"""

import numpy as np
import re
import os
import datetime


def id(file):
    """ Creates ID for each measurement from data file name.
        
    For SM4 and NID files IDs will be created from the digits. For all other
    file types just the file ending will be stripped.
        
    Args:
        file (string): Path to the data file.
    """
    
    if file.endswith('SM4'):
        id = int(re.search('.*(\d{3})\.', file).group(1))
    elif file.endswith('nid'):
        id = int(re.search('.*(\d{4})\..{3}$', file).group(1))
    else:
        id = re.search('.*(\/|\\\)(.*)\.\S{3}', file).group(2)
    
    return(str(id))


class data(object):
    '''Represents any data. As optional arguments surface, remarks etc. is useful!'''
    
    def __init__(self, file, **kwargs): 
        self.remark = 'nan'
        self.file = file
        self.id = id(self.file)
        
        self.path = os.path.dirname(os.path.abspath(self.file))
        self.datetime = datetime.datetime.fromtimestamp(os.path.getmtime(file)).strftime('%Y-%m-%d %H:%M:%S')
        self.meta = {}
        for key, value in kwargs.iteritems():
            self.varName = 'self.' + key
            exec("%s = '%s'" % (self.varName, value))
            self.meta[key] = value
    
    
    def __str__(self):
        return(self.id)
    
    
    def returnPath(self):
        '''Return path to data file.'''
        
        return('file:///' + '/'.join(self.file.split('/')[1:])) 
    


class image(data):
    '''Represents any image.'''
    
    def __init__(self, file, **kwargs):
        data.__init__(self, file, **kwargs)
        self.surface = None

