Proespm Documentation
========================
Processing of electrochemical, spectral and imaging files with optional import of labjournals. So far the following measurements can be processed: STM, ECSTM, AFM, SEM, CV, Chronoamperometry, XPS, Raman data, and Optical Microscope images.

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Installation

   install


Usage
-------------
Adjust the parameters in `config.yml <https://github.com/n-bock/proespm/blob/master/config.yml>`_ for your needs.


Run the *proespm.py* file with Python 2.7.

.. code-block:: console

   $ python2 proespm.py

The optional **xlsx-labjournal** file can contain several measurement informations, e.g. type (stm, ecstm, afm, cv, peis, xps, image, sem, or raman), day, surface, or remark (see xlsx file in /tests). Each row must have an explicit ID corresponding to the file name of the measurement in order to read in the information properly.

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

If you do not want to pass a labjournal set **labjournal available** and **fallback method** accordingly:

 .. code-block:: yaml
    :emphasize-lines: 3, 5

    import:
        single file import: No,
        labjournal available: No,
        ask for labjournal: Yes,
        fallback method: stm

If no labjournal is available, only one measurement type can be processed at the same time.

A `html report <https://htmlpreview.github.io/?https://github.com/n-bock/proespm_example/blob/master/data_report.html>`_ can be created, which includes
all the processed measurement data and the corresponding labjournal informations.

**How to change the SPM processing:**

#. Run the desired function on some data from within the Gwyddion GUI
#. Right click on the image and select **View Log**
#. Use the parameters found there to edit your config.yml file, for more information see `module list <http://gwyddion.net/module-list.en.php>`_



.. toctree::
   :maxdepth: 4
   :hidden:
   :caption: Data Types

   spm
   ec
   spectroscopy
   sem
   image






* :ref:`modindex`


.. toctree::
   :hidden:
   :caption: Indices

   genindex
