#!/usr/bin/env python
# coding:utf-8
"""
OSIT test module
include:
    1. deploy(replace kernel)
    2. reboot
    3. check_kernel_version
    4. get_basic_info
    5. runtest
    6. collect log
    7. check hang
    8. (TBD)
"""
import os
import sys
import re
import argparse
import logging
import tarfile
import time
import getpass
import csv
import multiprocessing
import shutil
from datetime import datetime
from relay_ctl import bxt_gp_power_on

from simics import Simics
from utils import run_command
from ssh_session import (
    SSHSession,
    SSHConnectionError
)

USER_ROOT = getpass.getuser()
CWD = os.getcwd()
DATE_FORMAT = datetime.now().strftime("%y%m%d%H%M")
KERNEL_INFO = "uname -r"
LINUX_INFO = "head -1 /etc/issue | awk '{print $1,$2,$3}'"
BIOS_INFO = "dmidecode -t 0 | awk '{if ($0 ~ /[Vv]ersion/) print $2}'"
OSIT_ROOT = "/opt/ltp-ddt"
TEST_DIR = os.path.join("/home", USER_ROOT)
RAWLOG_UPLOAD_PATH = "/data/kernel_test_report/osi_test_report/"
RAWLOG_PATH_ON_DEV = "%s/results/" % OSIT_ROOT
OSIT_LOG_PARSER = "osit-log-parser.awk"
HOST_MESSAGE_LOG = "host_message.log"
BUILD_INFO_FILE = "build_info.log"
REALTIME_OUTPUT_FILE = "realtime_output.log"
SERIAL_FILE = "serial.log"
KERNEL_TRACK = "/home/root/kernel_package/"
HOST_CONNECT = "sys_oak@desk08.bj.intel.com"

DEV_TIMEOUT_OTHER = {'joule': '3600',
                     'bxt_gp': '3600',
                     'bxt_gp_clr': '3600',
                     'icl_simics': '7200',
                     'kbl_u': '3600'}

DEV_TIMEOUT_FULL = {'joule': '14400',
                    'bxt_gp': '14400',
                    'bxt_gp_clr': '14400',
                    'icl_simics': '57600',
                    'kbl_u': '14400'}

log_format = '%(asctime)-15s UNITTEST %(name)-10s %(levelname)-8s %(message)s'
logging.basicConfig(format=log_format, level=logging.DEBUG)
osit_logger = logging.getLogger(__name__)
osit_logger = logging.getLogger("ositest")


def add_logger_hander(test_data_dir):
    if os.path.exists(test_data_dir):
        pass
    else:
        os.mkdir(test_data_dir)
    host_message_path = os.path.join(test_data_dir, HOST_MESSAGE_LOG)
    if os.path.exists(host_message_path):
        os.remove(host_message_path)
    log_filename = logging.FileHandler(host_message_path)
    log_formatter = logging.Formatter(log_format)
    log_filename.setFormatter(log_formatter)
    osit_logger.addHandler(log_filename)


class KernelErrorException(Exception):
    """ Base class for all exceptions """
    error_code = 0
    error_help = "Replace kernel error"
    error_type = "Kernel"


def parse_args(arg_list):
    """osit runner arg parser"""
    parser = argparse.ArgumentParser(description="OS-independent test runner",
                                     epilog="Don't panic!")
    parser.add_argument("-t", dest="template", required=True,
                        action="store", help="template: osi test type")
    parser.add_argument("-i", dest="target_list",
                        action="store",
                        help="targe list: single or multiple test case")
    parser.add_argument("-f", dest="scenario_name",
                        action="store",
                        help="scenario name: scenario file defined in runtest")
    parser.add_argument("-d", dest="ltp_dir",
                        action="store",
                        help="ltp directory: the ltp tool path")
    parser.add_argument("-b", dest="kernel_build", required=True,
                        action="store",
                        help="kernel build: kernel build num need replace")
    parser.add_argument("-p", dest="product", required=True,
                        action="store",
                        help="product: the product type")
    parser.add_argument("-D", dest="device_name", required=True,
                        action="store",
                        help="device name: testing device name")
    parser.add_argument("-U", dest="user", required=True,
                        action="store",
                        help="user: user of hostname you need to connect")
    parser.add_argument("-H", dest="hostname", required=True,
                        action="store",
                        help="hostname: hostname or IP you need to connect")
    parser.add_argument("-P", dest="password",
                        action="store",
                        help="password: password of hostname you need to connect")
    # Add default port value to prevent incorrect port usage.
    # TODO: refactor port usage in next week.
    parser.add_argument("-T", dest="port", default=22,
                        action="store",
                        help="port: port of hostname you need to connect")
    args = parser.parse_args(arg_list)
    return args


def replace_kernel(test_session, kernel_build, password=None):
    """
    tar-package format: branch_name-device_name-kernel_version-build_number.tar.bz2
            e.g: devbkc-bxt_gp-4.16.0-427.tar.bz2
    """
    kernel_package_dir = "/home/%s/kernel_package/%s" % (USER_ROOT, kernel_build)
    kernel_untar_dir = "/home/%s/kernel_untar/%s" % (USER_ROOT, kernel_build)
    dest_path_vmlinuz = "/boot/vmlinuz"
    dest_path_modules = "/lib/modules/"
    clr_rp_exe = "clr_rpls_kernel.sh"
    clr_tmp_dst = "/data/kernel/tmp_img/"
    file_to_send_vmlinuz = ""
    file_to_send_modules = ""
    file_to_send_config = ""

    os.chdir(kernel_package_dir)
    for name in os.listdir(kernel_package_dir):
        if name.endswith(".tar.bz2"):
            tar_bz2_filename = name
            osit_logger.info("-------------------- tar_bz2_filename: %s --------------------", tar_bz2_filename)
        else:
            raise KernelErrorException("Can't find kernel package!")

    if kernel_build in tar_bz2_filename:
        osit_logger.debug("start to decompression kernel package...")
        archive = tarfile.open(tar_bz2_filename, 'r:bz2')
        archive.debug = 1
        for tarinfo in archive:
            archive.extract(tarinfo, kernel_untar_dir)
        archive.close()

    os.chdir(kernel_untar_dir)
    for name in os.listdir(kernel_untar_dir):
        if name.startswith("bzImage"):
            file_to_send_vmlinuz = name
        elif name == "lib":
            for filename in os.listdir(os.path.join(name, "modules")):
                file_to_send_modules = os.path.join(name, "modules", filename)
                osit_logger.info("-------------------- filename: %s --------------------", filename)
        elif name.startswith("config"):
            file_to_send_config = name
    osit_logger.info("kernel is %s, module is %s, config is %s", file_to_send_vmlinuz, file_to_send_modules,
                     file_to_send_config)
    if not (file_to_send_vmlinuz and file_to_send_modules and file_to_send_config):
        osit_logger.info("image error: please check your kernel image")
        return False

    if test_session.host.startswith('bxt_gp_clr'):
        osit_logger.info("Do kernel replacement for %s", test_session.host)
        test_session.sendcommand("mkdir -p " + clr_tmp_dst, timeout=10)
        test_session.sendcommand("rm -rf %s/*" % clr_tmp_dst, timeout=10)
        for item in [file_to_send_vmlinuz, file_to_send_modules, file_to_send_config, clr_rp_exe]:
            test_session.scp_send(item, clr_tmp_dst, password, recursive=True, timeout=20)
        #拷贝文件
        test_session.scp_send(CWD + '/host_runner/' + clr_rp_exe, clr_tmp_dst, password, recursive=True, timeout=20)

        try:
            osit_logger.info("chmod 755 %s" % os.path.join(clr_tmp_dst, clr_rp_exe))
            test_session.sendcommand("chmod 755 %s" % os.path.join(clr_tmp_dst, clr_rp_exe))
            reply = test_session.sendcommand("/bin/bash %s -k %s -l %s -c %s " % \
                                             (os.path.join(clr_tmp_dst, os.path.basename(clr_rp_exe)),
                                              os.path.join(clr_tmp_dst, os.path.basename(file_to_send_vmlinuz)),
                                              os.path.join(clr_tmp_dst, os.path.basename(file_to_send_modules)),
                                              os.path.join(clr_tmp_dst, os.path.basename(file_to_send_config))))
            osit_logger.debug(reply[-2])
            osit_logger.info("------Value List: -------- \n %s\n %s\n %s\n" % \
                             (os.path.join(clr_tmp_dst, os.path.basename(clr_rp_exe)),
                              os.path.join(clr_tmp_dst, os.path.basename(file_to_send_vmlinuz)),
                              os.path.join(clr_tmp_dst, os.path.basename(file_to_send_modules))))
        except Exception as err:
            osit_logger.error("image replacement error. %s", str(err))
    else:
        rm_modules_path = os.path.join(dest_path_modules, "*")
        test_session.sendcommand("rm -fr " + rm_modules_path, timeout=30)
        osit_logger.debug("vmlinuz:%s", file_to_send_vmlinuz)
        osit_logger.debug("modules:%s", file_to_send_modules)
        for source, dest in zip([file_to_send_vmlinuz, file_to_send_modules, file_to_send_config],
                                [dest_path_vmlinuz, dest_path_modules]):
            test_session.scp_send(source, dest, password, recursive=True, timeout=20)

    os.chdir(CWD)
    return os.path.basename(file_to_send_modules)


def reboot_device(test_session, user, host, password=None):
    runcommand = "reboot"
    retest_session = None
    osit_logger.info("Reboot the device.")
    test_session.sendcommand(runcommand, timeout=60)
    time.sleep(10)  # wait 10 seconds for device totally power-off
    bxt_gp_power_on(host)
    count = 0
    while count < 3:
        osit_logger.info("Attempt to connect to device...")
        osit_logger.debug("count = %s" % count)
        try:
            time.sleep(60)
            retest_session = SSHSession(user, host, password)
            if retest_session:
                break
        except SSHConnectionError:
            osit_logger.debug("Enter to except !!")
            count += 1
    if not retest_session:
        raise SSHConnectionError("After reboot, the session not established!")
    else:
        return retest_session


def check_kernel_version(test_session, kernel_version_modules):
    """After replace kernel, need to check kernel version"""
    logs, _ = test_session.sendcommand(KERNEL_INFO, timeout=10)
    if kernel_version_modules in logs:
        osit_logger.info("Check kernel version passed!")
        return 0
    else:
        osit_logger.error("Check kernel version failed!")
        return 1


def get_basic_info(test_data_dir, test_session, device_name):
    logs_kernel, _ = test_session.sendcommand(KERNEL_INFO, timeout=10)
    logs_linux, _ = test_session.sendcommand(LINUX_INFO, timeout=10)
    logs_bios, _ = test_session.sendcommand(BIOS_INFO, timeout=10)
    str_logs_kernel = ('').join(logs_kernel)
    str_logs_linux = ('').join(logs_linux)
    str_logs_bios = ('').join(logs_bios)
    basic_log_filename = os.path.join(test_data_dir, BUILD_INFO_FILE)
    with open(basic_log_filename, 'w+') as fd:
        fd.write("Device name: %s\nKernel version: %s\nLinux version: %s\nBIOS version: %s\n" \
                 % (device_name, str_logs_kernel, str_logs_linux, str_logs_bios))


def run_device_runner(test_data_dir,
                      test_session,
                      device_name,
                      template,
                      target_list=None,
                      scenario_name=None,
                      ltp_dir=None):
    if ltp_dir:
        test_session.sendcommand("cd %s" % ltp_dir, timeout=10)
    else:
        test_session.sendcommand("cd %s" % OSIT_ROOT, timeout=10)
    runcommand = "python osit_runner.py -t %s" % template
    if target_list:
        runcommand += " -i %s" % target_list
    elif scenario_name:
        runcommand += " -f %s" % scenario_name
    osit_logger.debug(runcommand)
    if template == "full":
        logs, _ = test_session.sendcommand(runcommand, timeout=int(DEV_TIMEOUT_FULL[device_name]))
    else:
        logs, _ = test_session.sendcommand(runcommand, timeout=int(DEV_TIMEOUT_OTHER[device_name]))
    filename = os.path.join(test_data_dir, REALTIME_OUTPUT_FILE)
    with open(filename, 'w+') as fd:
        fd.write('\n'.join(logs))
    time.sleep(20)
    return 0


def update2lava(case_name, case_result):
    """Using lava-test-case cmd to update test result"""
    command = "lava-test-case %s --result %s" % (case_name, case_result)
    return run_command(command)


def parser_log(test_data_dir,
               std_log_fnm,
               test_session,
               kernel_build,
               device_name,
               template,
               product,
               password):
    """cp device test log to host"""
    osit_csv_file = ""
    rawlog_dir = os.path.join(test_data_dir, "raw")
    runcommand_grep = "ls %s | grep .csv" % RAWLOG_PATH_ON_DEV
    logs, _ = test_session.sendcommand(runcommand_grep, timeout=10)
    osit_logger.debug("logs: %s" % logs)
    if logs:
        osit_logger.debug("Find the csv file in device logs!")
    else:
        osit_logger.error("Can't find the csv file in device logs! Exit...")
        runcommand_ls = "ls -al %s" % RAWLOG_PATH_ON_DEV
        logs, _ = test_session.sendcommand(runcommand_ls, timeout=10)
        osit_logger.error("The log files in %s are %s" \
                          % (RAWLOG_PATH_ON_DEV, logs))
        sys.exit(1)
    if device_name == "icl_simics":
        scp_command = "scp -r %s %s:%s" % (RAWLOG_PATH_ON_DEV, HOST_CONNECT, rawlog_dir)
        logs, _ = test_session.sendcommand(scp_command, timeout=10)
        osit_logger.debug("logs: %s" % logs)
    else:
        test_session.scp_get(rawlog_dir,
                             RAWLOG_PATH_ON_DEV,
                             password,
                             recursive=True,
                             timeout=10)
    osit_logger.info("List osit raw log dir: %s" % str(os.listdir(rawlog_dir)))
    for name in os.listdir(rawlog_dir):
        if name.endswith(".csv"):
            osit_csv_file = name
            osit_logger.info("Got csv file: %s" % osit_csv_file)
            rawlog_path = os.path.join(rawlog_dir, osit_csv_file)
            osit_logger.debug("csv file %s" % rawlog_path)
            current_path = os.path.split(os.path.realpath(__file__))[0]
            osit_logger.debug("current path: %s" % current_path)
            # FIXME: add this var in constant.py
            log_parser = os.path.join(current_path, OSIT_LOG_PARSER)
            osit_logger.debug("Get osit-log-parser.awk")
            parsed_xml_path = os.path.join(test_data_dir, "final_result.xml")
            parsed_csv_path = os.path.join(test_data_dir, "final_result.csv")
            parse_log_xml_cmd = "awk -F',' -f %s arg_build=%s arg_dev=%s \
                                 arg_ttype=%s arg_prod=%s %s > %s" \
                                % (log_parser,
                                   kernel_build,
                                   device_name,
                                   template,
                                   product,
                                   rawlog_path,
                                   parsed_xml_path)
            parse_log_csv_cmd = "awk -F',' -f %s arg_build=%s arg_dev=%s \
                                 arg_ttype=%s arg_otype=csv arg_prod=%s %s > %s" \
                                % (log_parser,
                                   kernel_build,
                                   device_name,
                                   template,
                                   product,
                                   rawlog_path,
                                   parsed_csv_path)
            run_command(parse_log_xml_cmd)
            run_command(parse_log_csv_cmd)
            osit_logger.debug("Generate xml file: %s" % parsed_xml_path)
            osit_logger.debug("Generate csv file: %s" % parsed_csv_path)
    upload_log(test_data_dir, std_log_fnm, device_name, product, parsed_csv_path)


def upload_log(test_data_dir, std_log_fnm, device_name, product, parsed_csv_path=None):
    log_server_user = "irda"
    log_server_hostname = "otcpkt.bj.intel.com"
    log_server_password = "intel@123"
    log_server_session = SSHSession(log_server_user,
                                    log_server_hostname,
                                    log_server_password)
    log_upload_path = os.path.join(RAWLOG_UPLOAD_PATH, product)
    # upload the simics real time and uart logs to test_data_dir
    if device_name == "icl_simics":
        log_file = os.path.basename(Simics.LOG_FILE)
        uart_log = os.path.basename(Simics.UART_LOG)
        simics_log_file = os.path.join(test_data_dir, log_file)
        simics_uart_log = os.path.join(test_data_dir, uart_log)
        shutil.copyfile(Simics.LOG_FILE, simics_log_file)
        shutil.copyfile(Simics.UART_LOG, simics_uart_log)
    output = log_server_session.scp_send(test_data_dir,
                                         log_upload_path,
                                         log_server_password,
                                         recursive=True,
                                         timeout=20)
    report_path = "http://" + log_server_hostname + "/kernel_test_report/osi_test_report/" + product + "/" + std_log_fnm
    osit_logger.info("Upload to [otcpkt.bj.intel.com] log server successfully!")
    osit_logger.info("\nThe test report link is: %s\n" % report_path)
    # upload test result into Lava
    if parsed_csv_path:
        with open(parsed_csv_path) as fd:
            result_csv = csv.reader(fd, delimiter=',')
            for line in result_csv:
                update2lava(line[0], line[1])


def run_test(test_data_dir,
             std_log_fnm,
             kernel_build,
             product,
             template,
             device_name,
             user,
             host,
             password,
             port=22,
             target_list=None,
             scenario_name=None,
             ltp_dir=None):
    test_session = SSHSession(user, host, password, port=port)
    if test_session:
        get_basic_info(test_data_dir, test_session, device_name)
        ret_code = run_device_runner(test_data_dir,
                                     test_session,
                                     device_name,
                                     template,
                                     target_list,
                                     scenario_name,
                                     ltp_dir)
        if ret_code == 0:
            parser_log(test_data_dir,
                       std_log_fnm,
                       test_session,
                       kernel_build,
                       device_name,
                       template,
                       product,
                       password)


def start_ositest(test_data_dir,
                  std_log_fnm,
                  kernel_build,
                  product,
                  template,
                  device_name,
                  user,
                  host,
                  password,
                  port=22,
                  target_list=None,
                  scenario_name=None,
                  ltp_dir=None):
    proc_run = multiprocessing.Process(target=run_test, args=(test_data_dir,
                                                              std_log_fnm,
                                                              kernel_build,
                                                              product,
                                                              template,
                                                              device_name,
                                                              user,
                                                              host,
                                                              password,
                                                              port,
                                                              target_list,
                                                              scenario_name,
                                                              ltp_dir,))
    proc_run.daemon = True
    proc_run.start()
    return proc_run


def stop_ositest(proc_run, test_session):
    test_session.close_session()
    proc_run.join(1)


def start_simics(kernel_build, user, host, port, password):
    kernel_path = os.path.join(KERNEL_TRACK, kernel_build)
    for filename in os.listdir(kernel_path):
        osit_logger.info("%s" % filename)
        kernel_package = os.path.join(kernel_path, filename)

    simics_test = Simics()
    osit_logger.info("Start to replace kernel package!")
    Simics.replace_kernel(kernel_package)
    osit_logger.info("Replace kernel completely!")
    osit_logger.info("Start the simics...")
    simics_test.start()
    time.sleep(180)
    test_session = SSHSession(user, host, password, port=port)
    if not test_session:
        osit_logger.error("Can't connect to the icl simics, exit!")
        return 1
    else:
        osit_logger.info("Connect to the icl simics!")
    return simics_test


def main(arg_list):
    args = parse_args(arg_list)
    user = args.user
    host = args.hostname
    password = args.password
    port = args.port
    dead_counts = 0
    std_log_fnm = "%s-%s-%s" % (args.kernel_build,
                                args.device_name,
                                DATE_FORMAT)
    test_data_dir = os.path.join(TEST_DIR, std_log_fnm)
    add_logger_hander(test_data_dir)

    if args.device_name == "icl_simics":
        simics_test = start_simics(args.kernel_build, user, host, port, password)
    else:
        test_session = SSHSession(user, host, password)
        if not test_session:
            osit_logger.error("Can't connect to the test device, exit!")
            return 1
        kernel_verison_modules = replace_kernel(test_session,
                                                args.kernel_build,
                                                password)
        if not kernel_verison_modules:
            raise KernelErrorException("Wrong kernel image!")

        test_session = reboot_device(test_session,
                                     user,
                                     host,
                                     password,
                                     )
        check_kernel = check_kernel_version(test_session, kernel_verison_modules)

        if check_kernel == 1:
            raise KernelErrorException("Wrong kernel version!")
    runcommand_sync_rtc = "hwclock -w"
    logs, _ = test_session.sendcommand(runcommand_sync_rtc, timeout=10)
    proc_run = start_ositest(test_data_dir,
                             std_log_fnm,
                             args.kernel_build,
                             args.product,
                             args.template,
                             args.device_name,
                             user,
                             host,
                             password,
                             port,
                             args.target_list,
                             args.scenario_name,
                             args.ltp_dir,
                             )

    osit_logger.info("Test process started, now start check_hang loop.")
    if args.device_name == "icl_simics":
        osit_logger.info("The test device is icl_simics, so skip the check_hang!")
        while True:
            if not proc_run.is_alive():
                osit_logger.info("Test process finished, exit now...")
                osit_logger.info("Start to close simcis!")
                simics_test.stop()
                osit_logger.info("Close simcis complete!")
                break
    else:
        while True:
            time.sleep(60)
            if not test_session.check_hang(count=2):
                dead_counts += 1
                osit_logger.debug("dead_counts = %d" % dead_counts)
            if dead_counts > 3:
                osit_logger.info("Device Hang!!!")
                stop_ositest(proc_run, test_session)
                upload_log(test_data_dir, std_log_fnm, args.device_name, args.product)
                break
            if not proc_run.is_alive():
                osit_logger.info("Test process finished, exit now...")
                osit_logger.info("Reboot the machine after test finished...")
                test_session = SSHSession(user, host, password)
                reboot_device(test_session,
                              user,
                              host,
                              password,
                              )
                break


if __name__ == "__main__":
    main(sys.argv[1:])
