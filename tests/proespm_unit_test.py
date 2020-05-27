"""proespmUnitTest.py

Run this file to check the functionality of the proespm software.

(C) Copyright Nicolas Bock, licensed under GPL v3 
See LICENSE or http://www.gnu.org/licenses/gpl-3.0.html
"""

from __future__ import print_function
import os, sys

dirname = os.path.dirname(__file__)
path = os.path.join(dirname, '../proespm/')
sys.path.insert(0, path)

from util import importHelper, WIN32_helper

importHelper()

if 'path_gwyddion' not in locals():
    WIN32_helper()

import gwy
import gwyutils
import unittest
import re
import shutil
import config
import html
import prep
import spm
import data
import ec
import spectroscopy
import numpy as np
from shutil import copy2, move
from itertools import count
from os.path import dirname, abspath, join


src_dir = join(dirname(dirname(abspath(__file__))), 'tests/reference_files/data')
input_fs = [join(src_dir, 'rhk/data0272.SM4'),
            join(src_dir, 'rhk/data0271.SM4'),
            join(src_dir, 'easyscan/Image00037.nid'),
            join(src_dir, 'afm/200218_001.gwy'),
            join(src_dir, 'xps_e20/448.dat'),
            join(src_dir, 'cv_ec4/CV_162437_ 1.txt'),
            join(src_dir, 'cv_ec4/CV_162509_ 2.txt'),
            join(src_dir, 'cv_labview/test_001.lvm'),
            join(src_dir, 'raman/MK19_autoclave.txt'),
            join(src_dir, 'cv_biologic/a__02_CV_C02.mpt'),
            join(src_dir, 'peis_biologic/a__01_PEIS_C02.mpt'),
            join(src_dir, 'chrono_biologic/11_02_CA_C02.mpt'),
            join(src_dir, 'xps_phi/xps_phi.csv'),
            join(src_dir, 'sem/fei_sem.tif'),
            join(src_dir, 'image/50x2.bmp')
            ]

class labjournalTest(unittest.TestCase):
    def setUp(self):
        self.dirname = os.path.abspath(os.path.dirname(__file__))
        self.input_f = os.path.join(self.dirname, 'reference_files')
        self.labjournal, self.path_labj = prep.grabLabjournal(self.input_f) 
    
    def testConditionFromLabjournal(self):
        self.assertEqual(self.labjournal['ID'][1], 'CV_164101_ 2')


class nidStmTest(unittest.TestCase):
    def setUp(self):
        self.dirname = os.path.abspath(os.path.dirname(__file__))
        self.input_file = os.path.join(self.dirname, 'reference_files/data/Image00037.nid')
        self.item = data.stm(self.input_file)
    
    def testStmFwdIsPngFileCreated(self):
        self.test_folder_png = os.path.join(self.dirname, 'reference_files/data/_png')
        self.item.saveTopoFwdImage(self.test_folder_png)
        self.test_file_fwd = os.path.join(self.dirname, 'reference_files/data/_png/271_tf.png')
        self.assertTrue(os.path.isfile(self.test_file_fwd))
    
    def testStmBwdIsDatFileCreated(self):
        self.test_folder_0 = os.path.join(self.dirname, 'reference_files/data/_0')
        self.item.saveTopoBwdData(self.test_folder_0)
        self.test_file_bwd = os.path.join(self.dirname, 'reference_files\data\_0\g271_ori.tb0')
        self.assertTrue(os.path.isfile(self.test_file_bwd))
    
    def tearDown(self):
        pass
        # remove files



class sm4stmTest(unittest.TestCase):
    def setUp(self):
        self.dirname = os.path.abspath(os.path.dirname(__file__))
        self.input_file = os.path.join(self.dirname, 'reference_files/data/data0271.SM4')
        self.item = spm.stm(self.input_file)
        self.item.processTopo(8)
    
    def testPixelSize(self):
        self.assertEqual(self.item.spmPixelSize()[0], 512)
    
    def testStmFwdIsPngFileCreated(self):
        self.test_folder_png = os.path.join(self.dirname, 'reference_files/data/_png')
        self.item.saveTopoFwdImage(self.test_folder_png)
        self.test_file_fwd = os.path.join(self.dirname, 'reference_files/data/_png/271_tf.png')
        self.assertTrue(os.path.isfile(self.test_file_fwd))
    
    def testStmBwdIsPngFileCreated(self):
        self.test_folder_png = os.path.join(self.dirname, 'reference_files/data/_png')
        self.item.saveTopoBwdImage(self.test_folder_png)
        self.test_file_bwd = os.path.join(self.dirname, 'reference_files\data\_png\\271_tb.png')
        self.assertTrue(os.path.isfile(self.test_file_bwd))
    
    def testStmFwdIsDatFileCreated(self):
        self.test_folder_0 = os.path.join(self.dirname, 'reference_files/data/_0')
        self.item.saveTopoFwdData(self.test_folder_0)
        self.test_file_fwd = os.path.join(self.dirname, 'reference_files\data\_0\g271_ori.tf0')
        self.assertTrue(os.path.isfile(self.test_file_fwd))
    
    def testStmBwdIsDatFileCreated(self):
        self.test_folder_0 = os.path.join(self.dirname, 'reference_files/data/_0')
        self.item.saveTopoBwdData(self.test_folder_0)
        self.test_file_bwd = os.path.join(self.dirname, 'reference_files\data\_0\g271_ori.tb0')
        self.assertTrue(os.path.isfile(self.test_file_bwd))
    
    def testStmUtunIsDatFileCreated(self):
        self.test_folder_0 = os.path.join(self.dirname, 'reference_files/data/_0')
        self.item.saveUTunData(self.test_folder_0)
        self.test_file_utun = os.path.join(self.dirname, 'reference_files\data\_0\g271_ori.ut0')
        self.assertTrue(os.path.isfile(self.test_file_utun))
    
    def tearDown(self):
        pass
        # remove files



class sm4ecstmTest(unittest.TestCase):
    def setUp(self):
        self.dirname = os.path.abspath(os.path.dirname(__file__))
        self.input_file = os.path.join(self.dirname, 'reference_files\data\data0271.SM4')
        self.item = spm.ecstm(self.input_file)
    
    def testUTunSm4Ec(self):
        self.assertEqual(self.item.uTunMean(), -2.6751987205352634)
    
    def testITunSm4Ec(self):
        self.assertEqual(self.item.iTunMean(), 3.650117683737664e-08)
    
    def testIsEcTxtFileCreated(self):
        self.test_folder_0 = os.path.join(self.dirname, 'reference_files\data\_0')
        self.item.saveEcData(self.test_folder_0)
        self.test_file_ec = os.path.join(self.dirname, 'reference_files\data\_0\g271_ori.ec0')
        self.assertTrue(os.path.isfile(self.test_file_ec))
    
    def testIsEcTxtFileCreated(self):
        self.test_folder_0 = os.path.join(self.dirname, 'reference_files\data\_0')
        self.item.saveIcData(self.test_folder_0)
        self.test_file_ic = os.path.join(self.dirname, 'reference_files\data\_0\g271_ori.ic0')
        self.assertTrue(os.path.isfile(self.test_file_ic))
    
    def testIsHtmlFileCreated(self):
        pass
    
    def tearDown(self):
        pass



class cvTest(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main(verbosity = 2)

