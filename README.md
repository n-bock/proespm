proespm - Image and Data Processing 
====================================
Processing of electrochemical, spectral and imaging files with optional import 
of labjournals. So far the following measurements can be processed: STM, ECSTM,
AFM, SEM, CV, Chronoamperometry, XPS, Raman data and plain images. 


To do
--------------
- import sm4 via rhksm4 lib 
    ds = rhksm4.to_dataset('path/to/file.sm4') 
    ds.IDxxxxx
- convert all imported data to xarray cv etc



Usage as Script
----------------
Adjust the parameters in *config.yml* for your needs. The optional **xlsx-labjournal** file 
can contain several measurement informations, e.g. type (stm, ecstm, afm, cv, peis, xps
image or raman), day, surface, remark (see xlsx file in /tests). Each row must have an explicit ID 
corresponding to the file name of the measurement in order to read in the 
information properly. A [**html report**](https://htmlpreview.github.io/?https://github.com/n-bock/proespm_example/blob/master/data_report.html) can be created, which includes 
all the processed measurement data and the corresponding labjournal informations.



Installation for Script Mode
-----------------------------
**Linux**

    sudo apt-get install python, pip
    pip --install numpy, genshi, pandas, xlrd, bokeh, pyyaml, pint, rhksm4, xarray


Contact and Contribution
-------------------------
- Found a bug or need a feature: <nicolas.bock@tum.de>
