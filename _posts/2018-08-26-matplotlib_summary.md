---
title: matplotlib不常见的绘图技巧
date: 2018-08-26 11:23:45
tags:
- Python
categories: Python
description: 这部分内容是总结作者本人遇到的不常见的matplotlib画图技巧。内容主要以代码和效果图的形式展示。
---
这部分内容是总结作者本人遇到的不常见的matplotlib画图技巧，包括代码和展示图。

### 贝叶斯优化之不确定区域绘制

这里是使用贝叶斯优化实现的自动调参代码，是对Snort的配置文件中max-pattern-len参数进行的优化。最终以一种可见、美观的结果图展示，如下。

![](https://saferman.github.io/assets/img/matplotlib_summary/bayesian-optimization.png)

完整的代码可以参考 [贝叶斯优化完整代码](https://saferman.github.io/assets/code/bayesian-optimization.py)，以后再放上理论推导。

这里最想谈论的是如何去绘制上图的灰色部分区域。在Google搜索无果，想到直接去查找mateplotlib官方手册找到了这个函数fill_between：

```python
plt.fill_between(all_x, mu_f(all_x) + show * sigma_f(all_x), mu_f(all_x) - show * sigma_f(all_x), facecolor="lightgray",
                 label="不确定性")
```
### 绘制实时动图

这部分的代码主要实现接受进入的数据并实时绘制曲线的效果。（这里的代码是使用定时器，但是定时器的间隔很短最终实现只要有数据进入就能立即绘制曲线，可以接受的数据输入最大频率为200HZ）

完整代码可以看[绘制实时动图代码](https://saferman.github.io/assets/code/merge_graph_by_time.py)

在这份代码里主要涉及到的难点有二个：

1. 如何实时更新图像
2. 更新的效率问题

实时更新图像有二种技术：一是使用animation，二是使用self.fig.canvas.new_timer。这二种方法原理是比较相近的，我采用了后者。关键代码如下：

```python
timer = self.fig.canvas.new_timer(interval = self.time_interval)
timer.add_callback(self._OnTimer, ax_array)
timer.start()
```

### 这里设置了一个定时器，每过time_interval的时间间隔就执行self._OnTimer函数，参数是ax_array。这个函数会检测是否有新的需要绘制的数据然后使用ax的set_ydata重新设置y轴数据，最后使用画布的更新函数更新即可。其中time_interval设置的比持续接收到的数据频率要小。关键代码如下：

```python
self.ax_plot[plot_num].set_ydata(self.graphInfo[name][8])
ax_array[plot_num].draw_artist(self.ax_plot[plot_num])
```

第二个问题就是效率，直接使用draw()更新画布会很慢，draw_idle()会变快一些，但是对于要求绘制频率更快一点需求仍然不满足。最终的解决办法是使用canvas的blit，在使用前需要调用canvas的restore_region保存背景图像，这样可以避免重影，关键代码如下：

```Python
self.fig.canvas.restore_region(self.backgrounds[plot_num])
self.fig.canvas.blit(ax_array[plot_num].bbox)
```

关于draw()、draw_idle()和blit()效率差别的原因，浅显的讲就是第一个draw()会将画布上所有的元素（坐标轴、标签、X轴等）都会重新绘制，这个很浪费时间，尤其是整个画面数据点较多的时候，而blit只是将变化的部分重新绘制，会节约大量时间。更深层的原因需要剖析源代码，以后再说。

### 如何在QtWidgets.QGraphicsView中添加mateplotlib的导航栏

这部分Google很难找到，最终结合[https://www.cnblogs.com/hhh5460/p/5189843.html](https://www.cnblogs.com/hhh5460/p/5189843.html)才搞明白这个问题，阅读源码真的很关键！完整示例代码：[PyQtWithNavigationToolbar.py](https://saferman.github.io/assets/code/PyQtWithNavigationToolbar.py)

关键的就是一个类：

```Python
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
```

这个连接了PyQt和mateplotlib的导航栏。

### PyQt 结合 matplotlib的技术

这个Google挺多的关键类：

```Python
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
```

个人常用的使用方法：

```Python
# 通过继承FigureCanvas类，使得该类既是一个PyQt5的Qwidget，又是一个matplotlib的FigureCanvas，这是连接pyqt5与matplotlib的关键
class Figure_Canvas(FigureCanvas):                                            
    def __init__(self, parent=None, width=11, height=5, dpi=100):
        fig = Figure(figsize=(16, 9), dpi=100)  #注意：该Figure为matplotlib下的figure，不是pyplot下面的figure
        FigureCanvas.__init__(self, fig) # 初始化父类
        self.setParent(parent)
        self.fig = fig

    def plotleadone(self, logname=""):
        ax = self.fig.add_subplot(111)
        ax.plot(np.random.rand(10))
```

### 如何在QtWidgets.QGraphicsView中绘制多个场景

占坑以后填