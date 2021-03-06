---
layout: post
title: PFRING 安装折腾笔记
date: 2017-07-15 10:23:40
tags:
- Linux
categories: Linux
description: 暑假折腾的一个程序的安装，可以提高抓包效率。
---

暑假折腾的一个程序的安装，可以提高抓包效率。

## PFRING 安装折腾笔记

**Author: Saferman**

### 一、PFRING 简介

#### 1. 简介
PF_RING™ is a new type of network socket that dramatically improves the packet capture speed, and that’s characterized by the following properties:  

官方网站：[http://www.ntop.org/products/packet-capture/pf_ring/](http://www.ntop.org/products/packet-capture/pf_ring/)  

#### 2. 特性

    Available for Linux kernels 2.6.32 and newer.
    No need to patch the kernel: just load the kernel module.
    10 Gbit Hardware Packet Filtering using commodity network adapters
    User-space ZC (new generation DNA, Direct NIC Access) drivers for extreme packet capture/transmission speed as the NIC NPU (Network Process Unit) is pushing/getting packets to/from userland without any kernel intervention. Using the 10Gbit ZC driver you can send/received at wire-speed at any packet sizes.
    PF_RING ZC library for distributing packets in zero-copy across threads, applications, Virtual Machines.
    Device driver independent.
    Support of Myricom, Intel and Napatech network adapters.
    Kernel-based packet capture and sampling.
    Libpcap support (see below) for seamless integration with existing pcap-based applications.
    Ability to specify hundred of header filters in addition to BPF.
    Content inspection, so that only packets matching the payload filter are passed.
    PF_RING™ plugins for advanced packet parsing and content filtering.


#### 3. 为什么需要 PF_RING
一切为了效率，按照其官方网站上的测试数据，在 Linux 平台之上，其效率至少高于 libpcap 50% - 60%，甚至是一倍。更好的是，PF\_RING 提供了一个修改版本的 libpcap，使之建立在 PF\_RING 接口之上。这样，原来使用 libpcap 的程序，就可以自然过渡了。


### 说明：
我犯了一个错误，一来就去查阅各种博文，其实官方给出了更简单的安装方法：[https://github.com/ntop/PF_RING/wiki](https://github.com/ntop/PF_RING/wiki)  
！！！！惨痛教训

### 二、安装环境
- 系统：Centos Linux release 7.3.1611 (Core)  
  查看方法：cat /etc/redhat-release
- PF\_RING: PF\_RING-6.6.0.tar.gz  
  来源：https://sourceforge.net/projects/ntop/files/PF_RING/  

### 三、安装步骤

#### 1. 依赖安装
很多 centos7 是最小化安装。这样很多 kernel 就没有安装全，而且很多开发库也没有。在安装 PF_RING 过程中，会缺少很多依赖。
```
    yum -y install subversion flex bison ethtool svn git`  
    yum -y install numactl  
    yum -y install numactl-devel  
    yum -y install kernel-devel  
    yum -y install wget
```


#### 2. 貌似 kernel 在连接上有些问题，可以自动修改一下

```
ln -s /usr/src/kernels/3.10.0-229.14.1.el7.x86_64 /lib/modules/3.10.0-229.el7.x86_64/build -f  
```

####
3. 用 wget 将 PF_RING 压缩包拷贝至虚拟机内
在 Windows 开启 HTTP 服务器 : 

```
python -m SimpleHTTPServer 80
```

然后使用 wget 命令下载  

PS: 注意选择不同的 PF_RING 版本还是有很大差异的，像新版本没有 e1000 网卡驱动，旧版本有，但是他们的 e1000 驱动不支持 centos7 的内核，因为太新了

#### 4. 编译安装 PF_RING 内核模块

```
tar \-zxf PF\_RING.6.6.0.tar.gz  
cd PF\_RINF.6.60/  
make     // 直接在跟目录下面 make, 进行全部编译  
cd PF\_RING.6.6.0/kernel  
make  
sudo make install  // 内核安装需要 root 用户权限  
insmod <PF\_RINGPATH>/kernel/pf\_ring.ko transparent\_mode=1  
```

注意：这里最后一步我是进入 /lib/modules/\`uname \-r\`/kernel/net/pf\_ring 执行的命令。也有说法是现按上述步骤执行，再进入我这个目录然后 sudo rmmod pf\_ring 卸载，再 sudo insmod pf\_ring.ko transparent\_mode=1 使能 PF\_RING。其中 transparent0,1,2 的选择也是有讲究的  
// 最好设置一下，官方解释是 2 的性能最好，但是有大神测试后发现差别并不是很大，具体的 mode 取值的测试可以参考这个链接：  

[http://jaseywang.me/2015/02/28/%E9%80%9A%E8%BF%87-tcpcopypf_ring-%E5%AF%B9-bcm-5719-%E5%B0%8F%E5%8C%85%E5%81%9A%E7%9A%84%E5%A4%9A%E7%BB%84-benchmark/](http://jaseywang.me/2015/02/28/%E9%80%9A%E8%BF%87-tcpcopypf_ring-%E5%AF%B9-bcm-5719-%E5%B0%8F%E5%8C%85%E5%81%9A%E7%9A%84%E5%A4%9A%E7%BB%84-benchmark/)

当 PF\_RING 激活时，会创建 /proc/net/pf\_ring 目录，使用 cat 命令查看 pf\_ring 的属性信息： 

```  
cat /proc/net/pf\_ring/info
```

注：为了编译 PF_RING 内核模块，你需要安装 Linux 内核的头文件（或者内核源代码）  

####5. 编译安装 PF_RING 所需依赖库  
进入到用户空间库 userland/lib 下，编译和安装。  

```  
cd ../userland/lib  
./configure  
make  
sudo make install
```

如果需要使用 libpcap 抓包分析，请卸载之前安装的 libpcap，然后进入 /userland/libpcap-xxx-ring/ 目录下配置、编译和安装驱动。  
卸载原来的 libpcap:  

```
rpm -qa libpcap          // 查看安装的 libpcap，如果有 libpcap 则强制卸载  
rpm --nodeps -e libpcap // 按照原文的报错，没有--nodefs 选项 , 使用的是--nodeps，不验证包依赖性， –e 选项，意思是擦除 erase  
```

安装 pf\_ring 的 libpcap:  

``` 
cd ../libpcap  
./configure  
make  
sudo make install  
```

注：为了使用 PF_RING 的优点，请使用 PF_RING 使能的 libpcap.a 重新编译应用。  

#### 6. 编译网卡的驱动
编译安装 PF\_RING 之前需要卸载原来的网卡驱动，卸载之前使用 ethtool 命令查看当前网卡的类型和驱动版本。这一步参考链接都是放在开头最早的一步完成的。  
先卸载之前的网卡驱动 :  

```
ifconfig  // 查看网卡的名称，如果是单网卡一般是 eth0, 双网卡的话，找到你要使用 pf_ring 的网卡名字替换下面的 eth0  
ethtool -i eth0  // 查看网卡的驱动名称  
lsmod | grep e1000e // 查看网卡驱动是否存在  
rmmod e1000e // 卸载电脑自动安装的网卡驱动   此处为 e1000e 驱动  
```

注：如果使用 ssh 远程卸载驱动会造成网络不能连接，务必现场操作。

进入到 drivers 目录下，根据 ethtool -i ethx 命令查看的网卡类型和驱动进入指定的目录进行编译和安装。  

```  
cd /root/soft/PF\_RING/PF\_RING-5.6.2/drivers/PF\_RING\_aware/intel/e1000e/e1000e-2.0.0.1/src  
make  
make install  
```

安装网卡驱动，进入到目录 /lib/modules/<redhat-version>/kernel/drivers/net 下进行网卡驱动安装  

```  
sudo insmod e1000e.ko  // 安装 pf_ring 网卡驱动  
sodu modprobe e1000e  // 只能载入 /lib/modules/<kernel ver>/ 中模块  
```

关于这一步如果出现错误可以参考：[http://blog.csdn.net/wl_fln/article/details/9465341](http://blog.csdn.net/wl_fln/article/details/9465341)，另外我是在上一步 make make install 那个目录执行的这儿行命令，感觉有些问题

安装完毕，查看驱动信息：

```  
dmesg | grep Ethernet  
```

####7. 测试网络的接收的包数
进入到 userland/examples 目录编译例子程序

```
cd <PF\_RING PATH>/userland/examples  
make  
./pfcount -i eth0     // 捕获 eth0 网口的数据报文  
```

使用 drivers/intel/ixgbe 下的驱动（支持 DNA 的 ixgbe 驱动的网卡）+DNA 驱动技术可以达到线速采集，PF_RING 模块必须在 DNA 驱动之前加载。  

#### 8. 常见错误及解决方法
1. 编译网卡模块驱动错误

       驱动所在目录：/root/soft/PF_RING/PF_RING-5.6.2/drivers/PF_RING_aware/intel/e1000e/e1000e-2.0.0.1/src
        
       错误信息：/root/soft/PF_RING/PF_RING-5.6.2/drivers/PF_RING_aware/intel/e1000e/e1000e-2.0.0.1/src/kcompat.h:3039: error: conflicting types for ‘netdev_features_t’
   
    解决方法：vim kcompat.h +3039　　　　// 注释掉第 3039 行
   
2. 网卡驱动模块所在目录：/root/soft/PF_RING/PF_RING-5.6.2/drivers/PF_RING_aware/intel/e1000e/e1000e-2.0.0.1/src
   
    加载网卡驱动模块：insmod e1000e.ko

### 四、参考链接：
[http://www.cnblogs.com/etangyushan/p/3679662.html](http://www.cnblogs.com/etangyushan/p/3679662.html)  
[http://blog.csdn.net/fan_hai_ping/article/details/6705170](http://blog.csdn.net/fan_hai_ping/article/details/6705170)  
[http://blog.csdn.net/fan_hai_ping/article/details/6705164](http://blog.csdn.net/fan_hai_ping/article/details/6705164)  
[http://www.cnblogs.com/sangli/p/4848361.html](http://www.cnblogs.com/sangli/p/4848361.html)