# -*- coding:utf8 -*-
import os
import shutil
import argparse
import wget
import getpass
import sys
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def parse_args(arg_list):
    """osit runner arg parser"""
    parser = argparse.ArgumentParser(description="OS-independent test runner",
                                     epilog="Don't panic!")
    parser.add_argument("-u", dest="url", required=True,
                        action="store", help="download url")
    args = parser.parse_args(arg_list)
    return args


def del_file(path):
    for i in os.listdir(path):
        path_file = os.path.join(path, i)  # 取文件绝对路径
        if os.path.isfile(path_file):
            os.remove(path_file)
        elif os.path.isdir(path_file):
            shutil.rmtree(path_file, True)


if __name__ == '__main__':

    USER_ROOT = getpass.getuser()
    args = parse_args(sys.argv[2:])
    url = args.url
    kernel_package_dir = "/home/%s/kernel_package/" % (USER_ROOT)
    # kernel_package_dir = "/data/kernel_package"
    if not os.path.exists(kernel_package_dir):
        # os.makedirs("/data/kernel_package")
        os.chdir("/home/{}".format(USER_ROOT))
        os.makedirs("kernel_package")
    else:
        del_file(kernel_package_dir)
        # os.mkdir(kernel_build)
    # 指定输出文件, 相当于 `-O output`
    # os.chdir(kernel_package_dir)
    # filename = wget.download(url, kernel_package_dir + kernel_build + '.tar.bz2')
    filename = wget.download(url, kernel_package_dir)

    print(filename)
