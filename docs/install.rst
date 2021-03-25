Linux
-------------

.. code-block:: console

    $ sudo apt-get install gwyddion, python2.7, pip
    $ pip install -r requirements.txt

Windows
-------------
Install the following packages and use standard settings when asked.

#. Install Python 2.7
#. Install `pycairo-1.8.10.win32-py2.7.msi <http://ftp.gnome.org/pub/GNOME/binaries/win32/pycairo/1.8/>`_
#. Install `pygobject-2.28.3.win32-py2.7.msi <http://ftp.gnome.org/mirror/gnome.org/binaries/win32/pygobject/2.28/>`_
#. Install `pygtk-2.24.0.win32-py2.7.msi <http://ftp.gnome.org/pub/GNOME/binaries/win32/pygtk/2.24/>`_
#. Install `Gwyddion 2.55.win32 <http://gwyddion.net/download.php#stable-windows>`_
#. Open cmd, navigate with cd to C:\\Python27\scripts and install the required Python libaries.

.. code-block:: console

    $ pip install -r <path-to-requirements.txt>


Set system parameters
--------------------------
Edit `config.yml <https://github.com/n-bock/proespm/blob/master/config.yml>`_ file to match the gwyddion executable. You can test the correct installation by setting ``debug modus: Yes`` and execute the program.

 .. code-block:: yaml

    system:
        win32 gwy name: gwyddion.exe
        win32 gwy path hint: C:\Program Files (x86)\Gwyddion\bin
        win32 gwyutils rel path: share\gwyddion\pygwy
        linux gwyutils path: /usr/share/gwyddion/pygwy
        debug modus: No
