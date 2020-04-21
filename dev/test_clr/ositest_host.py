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
import argparse
import logging
import tarfile
import time
import getpass
from datetime import datetime
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
    parser.add_argument("-b", dest="kernel_build", required=True,
                        action="store",
                        help="kernel build: kernel build num need replace")
    # parser.add_argument("-p", dest="product", required=True,
    #                     action="store",
    #                     help="product: the product type")
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


def del_file(path):
    for i in os.listdir(path):
        path_file = os.path.join(path, i)  # 取文件绝对路径
        if os.path.isfile(path_file):
            os.remove(path_file)
        else:
            del_file(path_file)


def replace_kernel(test_session, kernel_build, password=None):
    """
    tar-package format: branch_name-device_name-kernel_version-build_number.tar.bz2
            e.g: devbkc-bxt_gp-4.16.0-427.tar.bz2
    """
    kernel_package_dir = "/data/kernel_package/"
    kernel_untar_dir = "/data/kernel_untar/"
    dest_path_vmlinuz = "/boot/vmlinuz"
    dest_path_modules = "/lib/modules/"
    clr_rp_exe = "/data/workspace/replace-kernel-image/clr_rpls_kernel.sh"
    clr_tmp_dst = "/data/kernel/tmp_img/"
    file_to_send_vmlinuz = ""
    file_to_send_modules = ""
    file_to_send_config = ""
    # if not os.path.exists(kernel_package_dir):
    #     os.makedirs(kernel_untar_dir)
    os.chdir(kernel_package_dir)
    for name in os.listdir(kernel_package_dir):
        if name.endswith(".tar.bz2"):
            tar_bz2_filename = name
            osit_logger.info("-------------------- tar_bz2_filename: %s --------------------", tar_bz2_filename)
        else:
            raise KernelErrorException("Can't find kernel package!")
    # Does the folder exist
    if not os.path.exists(kernel_untar_dir):
        os.makedirs(kernel_untar_dir)
    else:
        del_file(kernel_untar_dir)
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
    # if not (file_to_send_vmlinuz and file_to_send_modules and file_to_send_config):
    #     osit_logger.info("image error: please check your kernel image")
    #     return False

    if test_session.host:
        osit_logger.info("Do kernel replacement for %s", test_session.host)
        test_session.sendcommand("mkdir -p " + clr_tmp_dst, timeout=10)
        test_session.sendcommand("rm -rf %s/*" % clr_tmp_dst, timeout=10)
        for item in [file_to_send_vmlinuz, file_to_send_modules, file_to_send_config, clr_rp_exe]:
            test_session.scp_send(item, clr_tmp_dst, password, recursive=True, timeout=20)
        # 拷贝文件
        test_session.scp_send(CWD + '/host_runner/' + clr_rp_exe, clr_tmp_dst, password, recursive=True, timeout=20)

        try:
            osit_logger.info("chmod 755 %s" % os.path.join(clr_tmp_dst, clr_rp_exe))
            test_session.sendcommand("chmod 755 %s" % os.path.join(clr_tmp_dst, clr_rp_exe))
            # reply = test_session.sendcommand("/bin/bash %s -k %s -l %s -c %s " % \
            #                                  (os.path.join(clr_tmp_dst, os.path.basename(clr_rp_exe)),
            #                                   os.path.join(clr_tmp_dst, os.path.basename(file_to_send_vmlinuz)),
            #                                   os.path.join(clr_tmp_dst, os.path.basename(file_to_send_modules)),
            #                                   os.path.join(clr_tmp_dst, os.path.basename(file_to_send_config))))
            reply = test_session.sendcommand("/bin/bash %s -k %s -l %s" % \
                                             (os.path.join(clr_tmp_dst, os.path.basename(clr_rp_exe)),
                                              os.path.join(clr_tmp_dst, os.path.basename(file_to_send_vmlinuz)),
                                              os.path.join(clr_tmp_dst, os.path.basename(file_to_send_modules))))
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
    # bxt_gp_power_on(host)
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
    logs = test_session.sendcommand(KERNEL_INFO, timeout=10)
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


def main(arg_list):
    args = parse_args(arg_list)
    user = args.user
    host = args.hostname
    password = args.password
    port = args.port
    dead_counts = 0
    # std_log_fnm = "%s-%s-%s" % (args.kernel_build,
    #                             args.device_name,
    #                             DATE_FORMAT)
    # test_data_dir = os.path.join(TEST_DIR, std_log_fnm)
    # add_logger_hander(test_data_dir)

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
    # todo 解决替换kernel后的检查信息
    check_kernel = check_kernel_version(test_session, kernel_verison_modules)
    if check_kernel == 1:
        raise KernelErrorException("Wrong kernel version!")
    # runcommand_sync_rtc = "hwclock -l"


if __name__ == "__main__":
    main(sys.argv[1:])
