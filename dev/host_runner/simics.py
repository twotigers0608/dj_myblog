#!/usr/bin/env python

#coding:utf-8
import os
import sys
import subprocess
import signal
import logging


def debug(msg):
    logging.info("\n++++++++ DEBUG ++++++++\n%s\n+++++++++++++++++++++++\n" % msg)


def cmd(command, is_shell=False):
    debug(command)
    dev_null = open(os.devnull, 'wd')
    return subprocess.Popen(command,
                            shell=is_shell,
                            stdout=dev_null,
                            stderr=subprocess.STDOUT)

def cmd_check(command, ignore=False):
    debug(command)
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError, e:
        if ignore:
            logging.error("The cmd failed(status: %d), ignored." % e.returncode)
        else:
            logging.error("The cmd failed(status: %d), terminated." % e.returncode)
            sys.exit(3)


def is_process_running(pid):
    return os.path.exists("/proc/%s" % pid)


class Simics:

    # class static variables - private
    __script_dir = os.path.dirname(os.path.abspath(__file__))
    __replacekernel_sh = "%s/replacekernel.sh" % __script_dir

    __SIMICS_BIN = "/opt/simics/simics-5.0.107/bin/simics"
    __SIMICS_SCRIPT = "/opt/simics/simics-icl-5.0.pre101/targets/x86-icl/default2.simics"
    __SIMICS_STARTUP_CMD = '%s -no-win %s -e disable-real-time-mode -e continue' % \
                             (__SIMICS_BIN, __SIMICS_SCRIPT)

    __VAR_DIR = "/var/tmp/osit-icl"
    __OSI_IMG_NM = "osit-simics_icl.img"
    __OSI_IMG = "%s/%s" % (__VAR_DIR, __OSI_IMG_NM)
    __OSI_IMG_TPL = "%s.tpl" % __OSI_IMG
    __OSI_IMG_ORI = "%s.ori" % __OSI_IMG
    __PID_FILE = "%s/.pid" % __VAR_DIR

    # class static variables - public
    LOG_FILE = "%s/simics.log" % __VAR_DIR
    UART_LOG = "%s/uart.log" % __VAR_DIR


    def __init__(self):
        self.proc = None


    @staticmethod
    def replace_kernel(kernel_path):
        if not os.path.exists(kernel_path):
            logging.error("Kernel build %s doesn't exist" % kernel_path)
            sys.exit(4)
        # check if OSI image is available
        if os.path.exists(Simics.__OSI_IMG):
            os.remove(Simics.__OSI_IMG)
        if os.path.exists(Simics.__OSI_IMG_ORI):
            os.rename(Simics.__OSI_IMG_ORI, Simics.__OSI_IMG)
        else:
            cmd_check("cp %s %s" % (Simics.__OSI_IMG_TPL, Simics.__OSI_IMG), True)
        # call shell script to replace kernel
        logging.info("Replacing kernel: %s" % kernel_path)
        rkel_cmd = "%s %s %s" % (Simics.__replacekernel_sh, kernel_path, Simics.__OSI_IMG)
        cmd_check(rkel_cmd)
        # set a cron job to make a copy of OSI image in advance
        cron_cmd = "echo 'cp %s %s.cp && mv %s.cp %s' | at now + 30minutes" % \
                     (Simics.__OSI_IMG_TPL,
                      Simics.__OSI_IMG_ORI,
                      Simics.__OSI_IMG_ORI,
                      Simics.__OSI_IMG_ORI)
        cmd(cron_cmd, is_shell=True)


    def start(self, force=False):
        pid = None
        if os.path.exists(self.__PID_FILE):
            with open(self.__PID_FILE, 'r') as pf:
                try:
                    pid = int(pf.read().rstrip())
                except ValueError:
                    pass
            if pid and is_process_running(pid):
                if force:
                    os.killpg(os.getpgid(pid), signal.SIGTERM)
                else:
                    logging.error("Simics is already running: %d, aborted" % pid)
                    return 2
        simics_startup_list = self.__SIMICS_STARTUP_CMD.split()
        self.proc = cmd(simics_startup_list, is_shell=False)
        with open(self.__PID_FILE, 'w') as pf:
            pf.write(str(self.proc.pid))
        return 0


    def stop(self):
        if self.proc and is_process_running(self.proc.pid):
            self.proc.kill()
        self.proc = None
        if os.path.exists(self.__PID_FILE):
            os.remove(self.__PID_FILE)
