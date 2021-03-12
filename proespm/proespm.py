"""proespm.py

This file is the main script file. Execute this file to start the actual batch
processing.

Example:
    For execution of the batch process run the following command:

        $ python2 proespm.py


(C) Copyright Nicolas Bock, licensed under GPL v3
See LICENSE or http://www.gnu.org/licenses/gpl-3.0.html
"""

from __future__ import print_function
import os
import sys
import shutil
import config
import html
import prep
import tempfile
from os.path import dirname, abspath, join
from data import m_id, Image
from spm import Ecstm, Stm, Afm
from sem import Sem
from ec import Ec, Cv, Peis, Chrono
from spectroscopy import Raman, Xps
from util import progress_bar, multiple_move
from log import logging

os.chdir(sys.path[0])


def prompt():
    """Prompts for the files, which will be processed.

    Returns:
        input_fs (list): List of all files (full path) selected by the user.
        labjournal (str): Path to the labjournal.
        src_dir (str): Source directory.
    """

    if config.debug_modus:
        src_dir = join(
            dirname(dirname(abspath(__file__))), "tests/reference_files/data"
        )
        input_fs = [
            join(src_dir, "rhk/data1272.SM4"),
            join(src_dir, "rhk/data0271.SM4"),
            join(src_dir, "easyscan/Image00037.nid"),
            join(src_dir, "afm/200218_001.gwy"),
            join(src_dir, "xps_e20/448.dat"),
            join(src_dir, "cv_ec4/CV_162437_ 1.txt"),
            join(src_dir, "cv_ec4/CV_162509_ 2.txt"),
            join(src_dir, "cv_labview/test_001.lvm"),
            join(src_dir, "raman/MK19_autoclave.txt"),
            join(src_dir, "cv_biologic/a__02_CV_C02.mpt"),
            join(src_dir, "peis_biologic/a__01_PEIS_C02.mpt"),
            join(src_dir, "chrono_biologic/11_02_CA_C02.mpt"),
            join(src_dir, "xps_phi/xps_phi.csv"),
            join(src_dir, "sem/fei_sem.tif"),
            join(src_dir, "image/50x2.bmp"),
            join(src_dir, "mul/GrRu_RT.mul"),
        ]
    elif config.is_single_f:
        input_fs = prep.promptFiles()
        src_dir = os.path.dirname(input_fs[0])
    else:
        input_fs, src_dir = prep.prompt_folder()

    if config.is_labj and not config.is_labj_prompt and not config.debug_modus:
        labjournal, path_labj = prep.grab_labjournal(os.path.split(src_dir)[0])
        l.log_p(8, ">>> Imported labjournal from " + path_labj)
    elif config.is_labj and config.is_labj_prompt and not config.debug_modus:
        labjournal, path_labj = prep.prompt_labjournal()
        l.log_p(8, ">>> Imported labjournal from " + path_labj)
    elif config.debug_modus:
        labjournal, path_labj = prep.grab_labjournal(
            os.path.abspath(os.path.join(src_dir, os.pardir))
        )
        l.log_p(8, ">>> Imported labjournal from " + path_labj)
    else:
        labjournal = ""
        path_labj = ""

    l.log_p(4, ">>> Source directory: " + src_dir)

    return src_dir, input_fs, labjournal


def prepare(src_dir, input_fs, temp_dir):
    """Preparation of all the files for the actual data manipulation.

    Args:
        src_dir (str): Source directory.
        input_fs (list): List of paths to files, which should be prepared.
        temp_dir (str): The link to the temp_file. It created outside of the main loop, to
                        assure cleanup on raised error.
    Returns:
        proc_dir (str): Directory where the are copied and created while processing.
        proc_fs (list): List of paths to files, which will processed.
    """

    l.log_p(8, ">>> Starting data import")

    # Check if files are on network drive and if yes move to temporary folder
    if prep.check_network_file(input_fs[0]):
        l.log_p(2, ">>> Files are on a network drive")
        proc_fs = prep.move_files_temp(input_fs, temp_dir)
        l.log_p(3, ">>> Copied files to local TEMP directory: " + temp_dir)
    else:
        l.log_p(2, ">>> Files are stored locally")
        proc_fs = input_fs  # use the input files directly

    proc_dir = os.path.dirname(proc_fs[0])
    l.log_p(4, ">>> Processing directory: " + proc_dir)
    l.log_p(4, ">>> Creating userconfig.log in " + src_dir)
    prep.copy_user_config(src_dir)
    l.log_p(0, "")
    proc_fs = sorted(proc_fs, reverse=False)

    return proc_dir, proc_fs


def main(src_dir, proc_dir, proc_fs, labjournal):
    """Main loop which batch process the files, which are imported via the
    GUI file dialog.

    Args:
        src_dir (str): Path to the original folder of the files.
        proc_dir (str): Can be the same as src_dir, depends if files are on server.
        proc_fs (list): List of all files (with full path).
        labjournal (pd-df): Labjournal as pandas dataframe.
    """

    proc_items = []
    l.log_p(5, ">>> Starting data processing")

    for i, dat in enumerate(proc_fs):
        if config.log_level < 5:
            progress_bar(
                i + 1, len(proc_fs), prefix="Progress:", suffix="complete", length=50
            )

        is_append = True
        labjournal_error = False
        data_id = m_id(dat)
        if config.is_labj:
            # This is a workarround, as the 'ID' pandas colomn does not
            # contain str values only, but also int; The pandas.read_excel
            # function optional conversion does not work properly. The old
            # expression: add_arg = labjournal[labjournal['ID'] == data_id]
            for x in labjournal["ID"]:
                if str(x) == str(data_id):
                    add_arg = labjournal[labjournal["ID"] == x]
                    add_arg = add_arg.iloc[0].to_dict()
                    break
            else:
                labjournal_error = True

        if labjournal_error or not config.is_labj:
            try:
                exec("item = %s(dat)" % config.m_type)
                l.log_p(10, ">>> Data without labjournal loaded: " + str(data_id))
            except IndexError as error:
                l.log_p(4, ">>> Failed to import " + dat)
                raise error
        else:
            try:
                exec("item = %s(dat, **add_arg)" % add_arg["type"].capitalize())
                l.log_p(10, ">>> Data with labjournal loaded: " + str(data_id))
            except IndexError as error:
                l.log_p(
                    4, ">>> Failed to import " + dat + " with labjournal information"
                )
                raise error

        # STM specific functions
        if type(item).__name__ in ["Stm", "Ecstm", "Afm"]:
            item.process_topo_fwd()
            item.save_topo_fwd_image(proc_dir)
            item.save_topo_fwd_data(proc_dir)
            item.process_topo_bwd()
            item.save_topo_bwd_image(proc_dir)
            item.save_topo_bwd_data(proc_dir)

        # AFM specific functions
        if type(item).__name__ in ["Afm"]:
            if "item.type" in locals() and item.type is not "Dynamic Force":
                item.save_phase_bwd_image(proc_dir)
                item.save_phase_fwd_image(proc_dir)

        # ECSTM specific functions
        if type(item).__name__ in ["Ecstm"]:
            item.save_ec_data(proc_dir)
            item.save_ic_data(proc_dir)
            item.save_u_tun_data(proc_dir)

        # CV specific functions
        if type(item).__name__ in ["Cv"]:
            item.save_ec(proc_dir)
            if not item.m_id.endswith("1") and item.m_file.endswith(".txt"):
                x = len(proc_items) - 1
                proc_items[x].append_cycle(item.data, item.m_id, item.remark)
                l.log_p(4, ">>> CV files " + proc_items[x].m_id + " are combined.")

                # As data has been appended to previous item, do not add
                # it to the html report
                is_append = False

        # SEM specific functions
        if type(item).__name__ in ["Sem"]:
            item.save_image(proc_dir)

        if is_append:
            proc_items.append(item)

        # Workaround of Gwyddion bug: C RAM allocation fails
        if type(item).__name__ in ["Stm", "Ecstm", "Afm"]:
            item.flush_memory()

    l.log_p(8, "")
    l.log_p(8, ">>> Finished data processing.")

    if config.is_html_out:
        l.log_p(2, ">>> Create HTML report.")
        sorted_items = sorted(proc_items, key=lambda x: x.datetime, reverse=False)
        html.create_html(src_dir, proc_dir, sorted_items)
        l.log_p(2, ">>> HTML report created.")


def cleanup(src_dir, proc_dir):
    """The cleanup procedure after the data manipulation.

    Args:
        src_dir (str): Path to the original folder of the files.
        proc_dir (str): Can be the same as src_dir, depends if files are on server.
    """

    l.log_p(2, "")

    if config.hierarchy:
        l.log_p(9, ">>> Move data to final destination.")
        if not multiple_move(
            proc_dir, src_dir, ["ec.txt", "0"], hierarchy="sub", subfolder_name="_data"
        ):
            l.log_p(10, ">>> No data files were not moved.")
        if not multiple_move(
            proc_dir, src_dir, ["png"], hierarchy="sub", subfolder_name="_png"
        ):
            l.log_p(10, ">>> No images files were not moved.")
        if not multiple_move(proc_dir, src_dir, ["html"], hierarchy="parent"):
            l.log_p(10, ">>> No HTML report was moved.")
    elif is_network_file:
        l.log_p(9, ">>> Move data and remove temporary folder")
        multiple_move(proc_dir, src_dir, ["png", "0", "ec.txt", "html"])

    l.log_p(0, ">>>                  DONE                   <<<")


if __name__ == "__main__":
    temp_dir = tempfile.mkdtemp(prefix="python_", suffix="_temp")
    l = logging()

    try:
        src_dir, input_fs, labjournal = prompt()
        proc_dir, proc_fs = prepare(src_dir, input_fs, temp_dir)
        main(src_dir, proc_dir, proc_fs, labjournal)
        cleanup(src_dir, proc_dir)
        l.save_log(src_dir, config.log_f_name)
    finally:
        shutil.rmtree(temp_dir)
