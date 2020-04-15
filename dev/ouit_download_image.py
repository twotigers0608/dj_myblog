# -*- coding:utf8 -*-
import os
import argparse
import zipfile
import wget
import getpass
import sys


def parse_args(arg_list):
    """osit runner arg parser"""
    parser = argparse.ArgumentParser(description="OS-independent test runner",
                                     epilog="Don't panic!")
    parser.add_argument("-u", dest="url", required=True,
                        action="store", help="download url")
    parser.add_argument("-b", dest="build_num",
                        action="store", help="jenkins build num")
    args = parser.parse_args(arg_list)
    return args


if __name__ == '__main__':
    USER_ROOT = getpass.getuser()
    args = parse_args(sys.argv[2:])
    kernel_build = args.build_num
    url = args.url
    kernel_package_dir = "/home/%s/kernel_package/%s/" % (USER_ROOT, kernel_build)
    if not os.path.exists(kernel_package_dir):
        os.chdir("/home/%s/kernel_package" % USER_ROOT)
        os.mkdir(kernel_build)
    # 指定输出文件, 相当于 `-O output`
    else:
        pass
    # os.chdir(kernel_package_dir)
    filename = wget.download(url, kernel_package_dir + kernel_build + '.log')
    print(filename)
