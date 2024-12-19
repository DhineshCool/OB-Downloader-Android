#!/bin/bash
if [ -z "$1" ]
then
    python updater.py forced
fi

rm main.py
rm updater.py
rm history.py
rm -rf OB-Downloader-Android
rm -rf bin
git clone https://github.com/DhineshCool/OB-Downloader-Android/ -b master --single-branch
cd OB-Downloader-Android
sh install.sh

#Cache Removal
rm -rf .cache
