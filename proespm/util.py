﻿"""util.py

Part of proespm: Helper functions.

(C) Copyright Nicolas Bock, licensed under GPL v3 
See LICENSE or http://www.gnu.org/licenses/gpl-3.0.html
"""

from __future__ import print_function
import os
import re
import sys
import itertools
import shutil
import config
from time import localtime, sleep


def FindGwyddion(path_hint, search_for):
    """Looks for the Gwyddion executable. 
    
    Args:
        PATH_HINT (str): Initial path to look.
        SEARCH_FOR (str): Looking for which file. 
    
    Returns:
        Path of the Gwyddion executable.
    
    """
    
    for root, dirs, files in os.walk(path_hint):
        for name in files:
            if name == search_for:
                return(os.path.abspath(root))
        else:
            sys.exit(">>> Gwyddion NOT found!")
    

def extractValue(nested_list, to_be_extracted):
    """Extract data values by match pattern.
    
    Args:
        nested_list (list of list): e.g. [['v1', 'E1', '.*'], ['icell', 'i', '.*/.']]
        to_be_extracted (str): 'E1       0.2'
    """
    
    output = []
    [output.append([x[0], re.search(x[2], string).group(1)]) for string in to_be_extracted for x in nested_list if x[1] in string]
    
    return(output)


def getPath():
    """Returns the current path, where the executed file is stored."""
    
    PAT = str(pat).split()[3][1:-9] # PATH extracted..
    
    sig = None
    
    try:
        sig = os.remove(PAT + 'pat.pyc')# get_rid...
    except OSError:
        PAT = PAT +'/'
        sig = os.remove(PAT + 'pat.pyc')# Fix for mutiple calls..  
    
    return(PAT)


def importHelper():
    """Adds current working directory to 'sys.path'."""
    
    if os.getcwd() not in sys.path:
        sys.path.append(os.getcwd())


def WIN32_helper():
    """Import 'gwy' module painless for Win32."""
    
    if 'win32' in sys.platform:
        path_gwyddion = FindGwyddion(config.win32_path_gwyddion_hint, config.win32_search_for)
        if not sys.path.__contains__(path_gwyddion): 
            sys.path.append(path_gwyddion)
            path_gwyutils = os.path.join(os.path.split(path_gwyddion)[0], config.win32_gwyutils_rel_path)
            sys.path.append(path_gwyutils)
    else:
        sys.path.append(config.linux_gwyutils_path)


# def WIN32_helper():
    # """Import 'gwy' module painless for Win32."""
    
    # if 'win32' in sys.platform:
        # path_gwyddion = FindGwyddion(config.win32_path_gwyddion_hint, config.win32_search_for)
        # if 'path_gwyddion' is not None:
            # # only add the result to 'sys.path' IF needed
            # if not sys.path.__contains__(path_gwyddion): 
                # sys.path.append(path_gwyddion)
                # gwyutils_path = os.path.join(os.path.split(path_gwyddion)[0],
                                             # config.win32_gwyutils_rel_path)
                # sys.path.append(gwyutils_path)
        # else:
            # sys.exit(">>> Gwyddion NOT found!")
    # else:
        # if not sys.path.__contains__('gwyutils'):
            # sys.path.append(config.linux_gwyutils_path)


def readLines(file, lines):
    """Function to read specific lines from a text file.
    
    Args:
        file (file): Input text file, which will be read.
        line (list): List of lines which will be read
    """
    
    output = {}
    with open(file) as f: 
        for i, line in enumerate(f):
            for j in lines:
                if i == j:
                    output[j] = line
                elif i > max(lines):
                    break
    return(output)


def printProgressBar (iteration, total, prefix='', suffix='', decimals=1, length=100, fill='|'):
    """Call in a loop to create terminal progress bar
    
    Copyright by Cris Luengo and Greenstick (stackoverflow)
    
    Args:
        iteration (int): current iteration
        total (int): total iterations
        prefix (str): prefix string
        suffix (str): suffix string
        decimals (str): positive number of decimals in percent complete
        length (int): character length of bar
        fill (str): bar fill character
    """
    
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total: 
        print()


def isFileType(file_name, file_type):
    """Function to check if a certain file is of certain type.
    
    Args:
        file_name (int): File to be checked.
        file_type (str): File type which is looked for.
    
    Returns:
        bool: True for s (filetype is the asked one), False otherwise.
    """
    
    return(re.search('.*\.(.*)$', file_name).group(1) == file_type)


def queryYesNo(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.
    
    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
    It must be "yes" (the default), "no" or None (meaningan answer is 
    required of the user).
        
    The "answer" return value is True for "yes" or False for "no".
    
    Copyright http://code.activestate.com/recipes/577058/
    """
    
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)
    
    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def moveSubfolder(source_dir, destination, filetype):
    """Moves all files of a certain type to specified subfolder.
    
    Args:
        source_dir: Path to look for.
        filetyp: Which filetype should be moved e.g. ".png".
        subfolder: String of the subfolder name
    """
    
    for filetype in filetypes:
        if not os.path.exists(os.path.join(source_dir, filetype)): 
            os.makedirs(os.path.join(source_dir, filetype))
        for files in os.listdir(source_dir):
            if files.endswith(filetype):
                shutil.move(os.path.join(source_dir, files), 
                            os.path.join(source_dir,
                            subfolder))
    

def moveParentfolder(source_dir, filetype):
    """Moves all files of a certain type to specified parent folder. 
    
    Args:
        source_dir: Path to look for.
        filetyp: Which filetype should be moved e.g. ".png". 
    """
    
    for files in os.listdir(source_dir):
        if files.endswith(filetype):
            parent_folder_link = os.path.split(source_dir)[0]
            shutil.move(os.path.join(source_dir, files), os.path.join(parent_folder_link, files))


def multipleMove(source, destination, filetypes, hierarchy = '', subfolder_name = 'sub'):
    """Moves all files of a certain type to specified destination folder.
    
    It can optionaly take a hierarchy. You will be prompted and asked if you want 
    to overwrite files.
    
    Args:
        source (str): Path to look for.
        destination (str): Path to copy to.
        filetypes (str): Which filetype should be moved e.g. ".png". 
        hierarchy (str): Can either be 'sub', 'parent' or not given. 
                         The subfolder will be created and named after 
                         the given filetype.
        subfolder_name (str): Name of subfolder, default: sub.
    """
    
    s = False
    for filetype in filetypes:
        list_dir = (x for x in os.listdir(source) if x.endswith(filetype))
        if hierarchy == 'sub':
            sub_destination = os.path.join(destination, subfolder_name)
            if not os.path.exists(sub_destination): 
                os.makedirs(sub_destination)
            
            for item in list_dir:
                try:
                    shutil.move(os.path.join(source, item), sub_destination)
                    s = True
                except shutil.Error:
                    if s or config.force_override or queryYesNo(filetype + ' already exist. Overwrite all?'):
                        shutil.move(os.path.join(source, item), os.path.join(sub_destination, os.path.basename(item)))
                        s = True
                    else:
                        s = False
                        break
        
        elif hierarchy == 'parent':
            parent_destination = os.path.split(destination)[0]
           
            for item in list_dir:
                try:
                    shutil.move(os.path.join(source, item), parent_destination)
                    s = True
                except shutil.Error:
                    if s or config.force_override or queryYesNo(filetype + ' already exist. Overwrite all?'):
                        dst_filename = os.path.join(parent_destination, os.path.basename(item))
                        shutil.move(os.path.join(source, item), dst_filename)
                        s = True
                    else:
                        s = False
                        break
        
        else:
            for item in list_dir:
                try:
                    shutil.move(os.path.join(source, item), destination)
                except shutil.Error:
                    if s or config.force_override or queryYesNo(filetype + ' already exist. Overwrite all?'):
                        shutil.move(os.path.join(source, item), os.path.join(destination, os.path.basename(item)))
                        s = True
                    else:
                        s = False
                        break
    
    return(s)


def blockPrint():
    """Stops terminal output. """
    
    sys.stdout = open(os.devnull, 'w')


def enablePrint():
    """Resumes terminal output. """
    
    sys.stdout = sys.__stdout__
