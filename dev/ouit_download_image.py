# -*- coding:utf8 -*-
import os
import zipfile
import requests

def __check_zip_file_zsq(func):
    def inner(*args, **kwargs):
        while True:
            return_value = func(*args, **kwargs)
            if zipfile.is_zipfile(return_value[0]):
                return return_value[0]
            elif os.path.getsize(return_value[0]) == return_value[1]:
                return return_value[0]
            os.remove(return_value[0])
            print('下载镜像失败,尝试再次下载')

    return inner


@staticmethod
@__check_zip_file_zsq
def download_img_with_progressBar(download_url, file_save_path):
    '''
    下载镜像有进度条显示
    :param download_url: 下载镜像地址  http://***/gordon_peak-flashfiles-16.zip
    :param file_save_path: 文件保存地址
    :return: 镜像文件保存路径
    '''
    fileName = '/'.join((file_save_path, download_url.split('/')[-1]))
    # print('@@@@@@@@@@@@@@@@@@@@@' + fileName)
    r = requests.get(download_url, stream=True, verify=False)
    # 得到文件总大小
    total_size = int(r.headers['Content-Length'])
    temp_size = 0
    print('[File Path]: %s' % fileName)
    print('[File Info]: %s' % download_url.split('/')[-1], flush=True)
    print('[File Size]: %dMB' % (total_size / 1024 / 1024), flush=True)

    with open(fileName, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                temp_size += len(chunk)  # 当前已经下载的大小
                f.write(chunk)
                if (temp_size / total_size * 100) % 10 == 0:
                    print('\r[Download Progress]: %s  %.2f%%' %
                          ('>' * int(temp_size * 50 / total_size), float(temp_size / total_size * 100)),
                          end='', flush=True)
        print('\nDone', flush=True)
    r.close()
    return (fileName, total_size)
