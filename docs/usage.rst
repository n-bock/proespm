
Quick Start
===========

Before the program is started, the parameters in the `config.yml <https://github.com/n-bock/proespm/blob/master/config.yml>`_ should be adjusted.

Data Import
--------------
You can select the import of single files or complete folder structures (including subfolders). ``_folder`` and unsupported formats are ignored.

 .. code-block:: yaml

    import:
        single file import: No      # select folders instead of single files


Labjournal
-------------
The optional **xlsx-labjournal** file can contain several measurement informations, e.g. type (stm, ecstm, afm, cv, peis, xps, image, sem, or raman), day, surface, or remark (see `xlsx file  in /tests <https://github.com/n-bock/proespm/blob/master/tests/reference_files/lab_journal.xlsx>`_). Each row must have an explicit ID corresponding to the file name of the measurement in order to read in the information properly.

.. list-table:: Labjournal Example
   :widths: 10 10 10 10 10 10
   :header-rows: 1

   * - date
     - ID
     - type
     - surface
     - atmosphere
     - remark
   * - 2020-11-16
     - data01
     - stm
     - carbon
     - vacuum
     - beautiful stm image
   * - 2020-11-16
     - data02
     - cv
     - carbon
     - H2SO4
     - beautiful cv

If you do not want to pass a labjournal set **labjournal available** and **fallback method** accordingly:

 .. code-block:: yaml
    :emphasize-lines: 3, 5

    import:
        single file import: No,
        labjournal available: No,
        ask for labjournal: Yes,
        fallback method: stm

If no labjournal is available, only one measurement type can be processed at the same time.


SPM Processing
---------------

SPM data is processed with Gwyddion non-GUI instance.

**How to change the SPM processing:**

#. Run the desired function on some data from within the Gwyddion GUI
#. Right click on the image and select **View Log**
#. Use the parameters found there to edit your config.yml file, for more information see `module list <http://gwyddion.net/module-list.en.php>`_


 .. code-block:: yaml

    spm:
        immediate functions:
            - level
            - align_rows
            - fix_zero


The parameter for each function are passed as well in the yaml file.

 .. code-block:: yaml

    align rows:
        max degree: 3
        do extract: No
        do plot: No
        method: 0
        masking: 2


Data Export
-----------
A `html report <https://htmlpreview.github.io/?https://github.com/n-bock/proespm_example/blob/master/data_report.html>`_ can be created, which includes
all the processed measurement data and the corresponding labjournal informations. Setting ``server path`` will create correct links in the html report for easy access to your raw data. The given path should overlap with the data path given during program runtime and will compensate for OS depending mounting (`/media/server-data` vs. `H:\\server-data`).

 .. code-block:: yaml
    :emphasize-lines: 2, 4

    export:
        create html report: Yes
        image export modification dialog: No
        server path: file://///nas.ads.mwn.de/tuch/pc1/Surface-Microscopy/SM-ECSTM
        move html to parent and rest in subfolder: Yes
        Force overwrite excisting files: Yes







Program execution
-----------------
Run the *proespm.py* file with Python 2.7.

.. code-block:: console

   $ python2 proespm.py

#. Prompts for files/folder
#. Asks for labjournal file (optional)
#. Files are matched with labjournal information if possible
#. Data files are saved in non-proprietary file formats
#. HTML report is generated
#. Files are moved to final server destination incl. subfolder structure
