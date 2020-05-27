proespm - Image and Data Processing 
====================================
Processing of electrochemical, spectral and imaging files with optional import 
of labjournals. So far the following measurements can be processed: STM, ECSTM,
AFM, SEM, CV, Chronoamperometry, XPS, Raman data and plain images. 


Project status
--------------
This project is still under devolopment. It currently uses the Gwyddion
Python libary to process image data, which requires Python 2.7. This binding 
will be removed and this project will be converted to Python 3. 


Usage as Script
----------------
Adjust the parameters in *config.yml* for your needs. 
Run the *proespm.py* file with Python 2.7. The optional **xlsx-labjournal** file 
can contain several measurement informations, e.g. type (stm, ecstm, afm, cv, peis, xps
image or raman), day, surface, remark (see xlsx file in /tests). Each row must have an explicit ID 
corresponding to the file name of the measurement in order to read in the 
information properly. A **html report** can be created, which includes 
all the processed measurement data and the corresponding labjournal informations.

**How to change the SPM processing:**
1) Run the desired function on some data from withing Gwyddion
2) Right click on the image and select 'View Log'
3) Use the parameters found there to edit your config.py file, for more 
information see [module list](http://gwyddion.net/module-list.en.php)


Installation for Script Mode
-----------------------------
**Linux**

    sudo apt-get install gwyddion, python2.7, pip
    pip2 --install numpy, genshi, pandas, xlrd, bokeh, pyyaml, pint

**Windows**
1.  Use standard settings when asked
1.  Install Python 2.7
1.  Install [pycairo-1.8.10.win32-py2.7.msi](http://ftp.gnome.org/pub/GNOME/binaries/win32/pycairo/1.8/)
1.  Install [pygobject-2.28.3.win32-py2.7.msi](http://ftp.gnome.org/mirror/gnome.org/binaries/win32/pygobject/2.28/)
1.  Install [pygtk-2.24.0.win32-py2.7.msi](http://ftp.gnome.org/pub/GNOME/binaries/win32/pygtk/2.24/)
1.  Install [Gwyddion 2.52.win32](http://gwyddion.net/download.php#stable-windows)
1.  Open cmd and navigate with cd to Python27\scripts
        
        pip install numpy, pandas, genshi, xlrd, bokeh, pyyaml, pint


Build it yourself
-----------------
If you want to use this programm as standalone you cannot use the Gwyddion 
binding and therefore you cannot process spm files and sem only as images. 
Build it yourself with Python 2.7 after removing the spm and sem classes:

    python setup.py


Contact and Contribution
-------------------------
- Found a bug or need a feature: <nicolas.bock@tum.de>
