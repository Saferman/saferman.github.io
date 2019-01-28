---
layout: post
title: ubuntu 安装 PF_RING 折腾笔记
date: 2017-07-15 10:23:40
tags:
- Linux
categories: Linux
description: 暑假折腾的一个程序的安装，可以提高抓包效率。
---
暑假折腾的一个程序的安装，可以提高抓包效率。

## ubuntu 安装 PF_RING 折腾笔记

**Author:Saferman**

### 安装心得
信 ubuntu 得永生！！！  
ubuntu 安装 PF\_RING 的错误比 centos 少多了，总体说来相当顺利
也是实习期间最顺利的一次安装了，想想就开心

### 1、安装 Build-essential、SVN、Flex、Libnuma-dev、bison
ubuntu 中：sudo apt-get install build-essential subversion flex libnuma-dev bison  
centos 中：yum install subversion flex bison numactl-devel

### 2、下载 PF_RING
svn co https://svn.ntop.org/svn/ntop/trunk/PF\_RING/ PF\_RING

### 3、卸载本机网卡驱动
#### （1）检查当前网卡
ethtool -i 指定网卡（eth0）
#### （2）卸载网卡驱动
sudo rmmod vmxnet
### 4、编译安装 kernel
（1）进入 PF_RING 目录里的 kernel 目录中  
（2） make 编译，sudo make install 安装
### 5、编译安装库
（1）进入 PF_RING 目录里的 userland/lib

（2）配置 ./configure，make 编译，sudo make install 安装
### 6、编译安装 PF_RING 可用的 libpcap
（1）进入 userland/libpcap  
（2）配置 ./configure，make 编译，sudo make install 安装
### 7、安装设备驱动
（1）我的情况是进入 PF\_RING/drivers/ZC/intel/e1000e/e1000e-3.0.4.1-zc/src  
（2） make 编译，sudo make install 安装
### 8、激活 PF\_RING 使其加载到内核工作
（1） cd /lib/modules/`uname -r`/kernel/net/pf\_ring  
（2） sudo insmod pf\_ring.ko transparent\_mode=1 （若已经激活，可以使用 sudo rmmod prf\_ring 卸载）
### 9、激活驱动
（1）我的情况是进入 /lib/modules/`uname -r`/kernel/drivers/net/ethernet/intel/e1000e  
（2） sudo insmod e1000e.ko
### 大功告成
至此 PF\_RING 安装完毕  
当 PF\_RING 激活，会创建一个新的入口 /proc/net/pf\_ring  
cat /proc/net/pf\_ring/info  
cat /proc/net/pf\_ring/plugins\_info  
链接 PF\_RING 的应用程序必须有 libpfring 和 libpcap 库，也需要依赖于-lpthread 库  
注意：PF\_RING 可以使用任何的 NIC 驱动，但是必须使用专用的驱动以便获得最大化的性能

