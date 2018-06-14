---
title: Loadable modules introduction
date: 2018-06-14 14::11:20
tags:
- Linux
categories: System
description: 讲解Linux系统中的可加载模块
---
Essentially, modules are to Linux as drivers are to Windows.  

### What are loadable modules (drivers) ?
Essentially, modules are to Linux as drivers are to Windows.

Unlike Windows drivers, which are usually supplied by the hardware manufacturer, most modules come supplied with each Linux distribution.

The Linux kernel can be extended to have additional capabilities in two basic ways:
- Recompilation of the kernel with new capabilities permanently "compiled-in" and subsequent booting to the new kernel;
- Building of a kernel with loadable modules for occasional use. In order to use these modules' features, the modules must be added to the kernel- this can be done either automatically or manually. When a module is no longer wanted, it may be removed from the custom kernel manually or it can disappear automatically. 

During kernel configuration and building, features specified with a 'y' will have the necessary software to support those features as part of the kernel (the features will be "compiled into" the kernel and will consume memory permanently). If a feature is specified with an 'm' then the feature will be a loadable module that may be loaded and unloaded at will (and will use memory only if the module is loaded). If an 'n' is specified, then the feature will not be enabled in the kernel at all and will not be available. 

### Using loadable modules

The file **/etc/modules** configures which loadable modules are automatically loaded. Here is a sample: 

```
nano -w /etc/modules
# /etc/modules: kernel modules to load at boot time.
#
# This file contains the names of kernel modules that should be loaded
# at boot time, one per line. Lines beginning with "#" are ignored.

loop
lp
fuse
r8169
```

Changing **/etc/modules**: Let's say your eepro100 Ethernet device breaks and you buy a new Ethernet card that uses the **tulip** driver. In this case, the relevant line in **/etc/modules** file should be changed to: 

```
tulip
```

In  most cases, when you reboot with your new Ethernet card, Ubuntu's  configuration manager should automatically notice a new Ethernet card is  installed, and change the **/etc/modules** file for you. 

To view a list of loadable kernel modules on a system, as well as their status, run: 

```
lsmod
```

```
Module                  Size  Used by    Not tainted
i810_audio             26408   2 (autoclean)
ac97_codec             13768   0 (autoclean) [i810_audio]
soundcore               7108   2 (autoclean) [i810_audio]
scanner                10716   0 (unused)
mousedev                5688   0 (unused)
keybdev                 2944   0 (unused)
input                   6176   0 [mousedev keybdev]
hid                    11804   0 (unused)
usb-uhci               27436   0 (unused)
usbcore                81088   1 [scanner hid usb-uhci]
```

To see a list of the module files: 

```
modprobe --list
# for those who don't have the `--list' or `-l' option, use the command below:
# find /lib/modules/`uname -r` -type f -name "*.ko"
```

```
/lib/modules/2.4.20/kernel/drivers/block/floppy.o
/lib/modules/2.4.20/kernel/drivers/block/loop.o
/lib/modules/2.4.20/kernel/drivers/char/rtc.o
/lib/modules/2.4.20/kernel/drivers/input/input.o
/lib/modules/2.4.20/kernel/drivers/input/keybdev.o
/lib/modules/2.4.20/kernel/drivers/input/mousedev.o
/lib/modules/2.4.20/kernel/drivers/net/dummy.o
/lib/modules/2.4.20/kernel/drivers/scsi/atp870u.o
/lib/modules/2.4.20/kernel/drivers/scsi/scsi_mod.o
/lib/modules/2.4.20/kernel/drivers/scsi/st.o
/lib/modules/2.4.20/kernel/drivers/sound/ac97_codec.o
/lib/modules/2.4.20/kernel/drivers/sound/i810_audio.o
/lib/modules/2.4.20/kernel/drivers/sound/soundcore.o
/lib/modules/2.4.20/kernel/drivers/usb/dc2xx.o
/lib/modules/2.4.20/kernel/drivers/usb/hid.o
/lib/modules/2.4.20/kernel/drivers/usb/scanner.o
/lib/modules/2.4.20/kernel/drivers/usb/usb-uhci.o
/lib/modules/2.4.20/kernel/drivers/usb/usbcore.o
/lib/modules/2.4.20/kernel/fs/fat/fat.o
/lib/modules/2.4.20/kernel/fs/msdos/msdos.o
/lib/modules/2.4.20/kernel/fs/vfat/vfat.o
```

or to search: 

```
modprobe --list *8169*
```

```
/lib/modules/2.6.24-16-server/kernel/drivers/net/r'''8169'''.ko
```

To load a module, and any modules that it depends on, use **modprobe**: 

```
modprobe st
```

To remove a loaded module, use **rmmod**: 

```
rmmod st
```

To view information about a module, use **modinfo**: 

```
modinfo st
filename:    /lib/modules/2.4.20/kernel/drivers/scsi/st.o
description: "SCSI Tape Driver"
author:      "Kai Makisara"
license:     "GPL"
parm:        buffer_kbs int, description "Default driver buffer size (KB; 32)"
parm:        write_threshold_kbs int, description "Asynchronous write threshold (KB; 30)"
parm:        max_buffers int, description "Maximum number of buffer allocated at initialisation (4)"
parm:        max_sg_segs int, description "Maximum number of scatter/gather segments to use (32)"
parm:        blocking_open int, description "Block in open if not ready an no O_NONBLOCK (0)"
```

### Blacklisting Modules

For various reasons it may be desirable to stop a module from loading.  In this case a module can be blacklisted in **/etc/modprobe.d/blacklist** 

```
nano -w /etc/modprobe.d/blacklist
```

for example the line 

```
blacklist e100
```

should be added to prevent the 'e100' module (one of many Ethernet modules) from loading. 

Sometimes it is needed to update the drivers cache after editing the blacklist.conf file. To do this, run: 

```
sudo update-initramfs -u
```



From: [https://help.ubuntu.com/community/Loadable_Modules](https://help.ubuntu.com/community/Loadable_Modules)