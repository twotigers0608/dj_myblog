#! /bin/sh
#
# replacekernel.sh
# Copyright (C) 2017 linjianh <linjianh@desk08>
#
# Distributed under terms of the MIT license.
#

#set -x
kernel_path=$1
osiimg_path=$2

ws="$(dirname $osiimg_path)"
osiimg_nm="$(basename $osiimg_path)"
mp_boot=$ws/mp_boot
mp_root=$ws/mp_root
tmp_dir=$ws/temp

rm -rf $tmp_dir
mkdir -p $tmp_dir
test -d $mp_boot || mkdir $mp_boot 
test -d $mp_root || mkdir $mp_root

sudo umount $mp_boot 2>/dev/null
sudo umount $mp_root 2>/dev/null
for m in $(sudo mount | grep "$osiimg_nm" | awk '{print $3}'); do
    sudo umount $m
done
sudo mount -o loop,offset=1048576  $osiimg_path $mp_boot
sudo mount -o loop,offset=19922944 $osiimg_path $mp_root

tar -jxf $kernel_path -C $tmp_dir
sudo install -m 755 -o root -g root $tmp_dir/vmlinuz-* $mp_boot/vmlinuz
sudo rm -rf $mp_root/lib/modules/*-PKT*
sudo mv $tmp_dir/lib/modules/*-PKT* $mp_root/lib/modules/
sudo chown root:root $mp_root/lib/modules/*-PKT*

while (sudo umount $mp_root 2>&1 | grep "device is busy" >/dev/null); do
    sleep 1
done
while (sudo umount $mp_boot 2>&1 | grep "device is busy" >/dev/null); do
    sleep 1
done
rm -rf $tmp_dir

