"""preProcess

Part of proespm: Data preparation functions.

(C) Copyright Nicolas Bock, licensed under GPL v3 
See LICENSE or http://www.gnu.org/licenses/gpl-3.0.html
"""

import sys
import re
import os
import fnmatch
import Tkinter 
import tkFileDialog
import numpy as np
import pandas
import config
import time
import shutil
from util import isFileType, queryYesNo


def promptFolder():
    """ Prompt for folder in which the data is stored. 
    
    Returns:
        input_files (list): Full path to the files in a list.
    """
    
    while True and 'dummy_var' not in locals():
        try:
            input_files = []
            root = Tkinter.Tk()
            initial_folder = tkFileDialog.askdirectory(initialdir = config.dialog_files['initialdir'])
            root.destroy()
            
            for p, dirs, files in os.walk(initial_folder, topdown = True):
                dirs[:] = [d for d in dirs if not d.startswith('_')]
                for f in files:
                    if f.endswith(tuple(config.allowed_file_types)) and p.split('/')[len(p.split('/'))-1][0] is not '_':
                        input_files.append(os.path.join(p, f))
            
            if len(input_files) == 0:
                raise IndexError
            
            return(input_files, initial_folder)
            
        except IndexError:
            if not queryYesNo('You have not picked any folder. Retry?'):
                sys.exit('No folder selected.')


def promptFiles():
    """ Prompt for the data with Tkinter GUI. 
    
    Returns:
        input_files (list): Full path to the files in a list.
    """
    
    while True and 'dummy_var' not in locals():
        try:
            input_files = []
            root = Tkinter.Tk()
            list_of_files = tkFileDialog.askopenfiles(mode='r', **config.dialog_files)
            root.destroy()
            
            for file in list_of_files:
                input_files.append(file.name)
            
            if len(input_files) == 0:
                raise IndexError
            
            dummy_var = 0
            
        except IndexError:
            if not queryYesNo('You have not picked any files. Retry?'):
                sys.exit('No files selected.')
    
    return(input_files)


def promptLabjournal():
    """ Prompt for Labjournal with Tkinter GUI.

    Returns:
        labjournal (np array): Labjournal as a numpy array
        path_labjournal (str): Full path to the labjournal.
    """
    
    while True and 'labjournal_pd' not in locals():
        try:
            root = Tkinter.Tk()
            path_labjournal = tkFileDialog.askopenfiles(
                              mode='rb', 
                              **config.dialog_labj)
            root.destroy()
            labjournal_pd = pandas.read_excel(path_labjournal[0], 
                                              sheet_name=config.labj_ws_name,
                                              dtypes=str,
                                              converters={'ID': str})
        
        except IndexError:
            if not queryYesNo('You have not picked any files. Retry?'):
                sys.exit('No Labjournal specified! You maybe want to change your config.')
    
    return(labjournal_pd, path_labjournal[0].name)


def grabLabjournal(path_labj):
    """ Grabs the labjournal from the given path
    
    Args:
        path_labjournal (str): Path to the folder, where the labjournal is.
    
    Returns:
        labjournal (np array): Labjournal as a numpy array
        path_labjournal (str): Full path to the labjournal.
    """
    
    xlsx_files = (file for file in os.listdir(path_labj) if file.endswith('.xlsx'))
    
    for file in xlsx_files:
        labj_file = os.path.join(path_labj, file)
        break
    else:
        sys.exit('No labjournal was found!')
    
    labjournal_pd = pandas.read_excel(labj_file, sheet_name=config.labj_ws_name)
    
    return(labjournal_pd, labj_file)


def checkNetworkFile(input_file):
    """ Check if files are on a network drive. 
    
    Paths starting with double backflash or "[F-Z]:/*" are most likely 
    network share.
    
    Args:
        input_file (str): Path to the file, which will be tested
        
    Returns:
        is_network_file (bool): True or False if the file is on network drive
    """
    
    for re in ["//*", "[F-Z]:/*", "*media*"]:
        if fnmatch.fnmatch(input_file, re):
            return(True)
    return(False)


def moveFilesTemp(input_files, temp_dir):
    """ Move files to a new created temporary folder on local drive.
    
    The function will first check, if there is temporary location on the OS.
    A folder 'python_xyz' will be created, where the files are moved to. The
    function returns a list of the file paths in the tempory folder.
    
    Args:
        input_files (list): Files which will be moved to a temporary folder.
        temp_dir (str): Path to temporary folder.
    
    Returns:
        process_files (list): List of paths to the files in a temporary folder.
    """
    
    if temp_dir is None:
        sys.exit("No temp directory was created!")
    else:
        process_files = []
        source_dir = os.path.dirname(input_files[0])
        for file in input_files:
            shutil.copy2(os.path.join(file), temp_dir)
            process_files.append(os.path.join(temp_dir, os.path.basename(file)))
    
    return(process_files)


def copyUserConfig(src_dir):
    """ Moves the UserConfig file along with the with processed data.
    
    Args:
        src_dir (str): Path to source directory.
    """
    
    config_path = os.path.join(os.path.split(sys.path[0])[0], 'config.yml')
    
    with open(config_path, "r") as f:
        log_f = f.read()
    
    with open(os.path.join(src_dir, '_config.log'), "a") as f:
        f.writelines("\n\n#[" + time.strftime('%Y-%M-%d %X') + "]" + "\n\n" + log_f)


def parFileName(data):
    """ Creates filename for Omicron par files.
    
    Args:
        data (str): path to file which should be read.
    
    Returns:
        orig_fs_name (list):
        proc_fs_name (list):
    """
    
    par_file = open(data, "r")
    par_file_data = {}
    orig_fs_name = []
    proc_fs_name = []
    line_counter = 1
    for line in par_file:       # import par-file into an array
        par_file_data[line_counter] = line
        line_counter = line_counter + 1
    par_file.close()
    
    for line in par_file_data:
        line_data = par_file_data[line]
        match_pattern = sysConfig.scala_name_hint
        
        # REGEX match for e.g. m2_ori.tb0
        if fnmatch.fnmatch(line_data, match_pattern):
            data_channel_orig_file_name = par_file_data[line+8]
            data_channel_orig_file_name = re.search(
                                        '.*(m\d+_ori\.t[b||f][0||1]).*', 
                                        data_channel_orig_file_name
                                        ).group(1) 
            orig_fs_name.append(data_channel_orig_file_name)
            
            # replace "m<whatever>" with "g<same_whatever_as_before>"
            proc_fs_name.append(re.sub('m(.*)', r"g\1", data_channel_orig_file_name))
    
    return(orig_fs_name, proc_fs_name)


def stmFileName(data, src_dir):
    """ Creates filename for spm files.
    
    Output file renaming for non-SCALA files: re.sub(FROM, TO, var).
    
    Args:
        data (str): path to file which should be read.
        src_dir (str): path to the log file.
    
    Returns:
        orig_fs_name (list):
        proc_fs_name (list):
    """
    
    orig_fs_name = []
    proc_fs_name = []
    
    orig_fs_name.append(os.path.basename(data))
    temp = os.path.basename(data)
    
    for pat in range(0, len(sysConfig.pat_out), 2):
        temp = re.sub(sysConfig.pat_out[pat], 
                      sysConfig.pat_out[pat + 1], 
                      temp)     
        
        if temp != os.path.basename(data): 
            break
    proc_fs_name.append(temp)
    
    return(orig_fs_name, proc_fs_name)


if __name__ == "__main__":
    labjournal = promptLabjournal()
    input_files = promptFolder()
