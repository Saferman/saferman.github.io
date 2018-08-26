#!/usr/bin/env python
# coding=utf8
# 开启进程 https://www.cnblogs.com/jokerbj/p/7424953.html

import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import numpy as np
import Queue
import threading
from multiprocessing import Process
import time

COLORS = {
    'white': 'white',
    'red': 'red',
    'yellow': 'yellow',
    'orange': 'orange',
    'blue': 'blue',
    'black': 'black',
    'grey': 'grey'
}  # 这部分需要修改

class MergeGraph(threading.Thread):
    def __init__(self, time_interval = 10, new_thread=True):
        if new_thread:
            super(MergeGraph, self).__init__()
            super(MergeGraph, self).setDaemon(True)
        self.time_interval = time_interval # 单位毫秒
        self.show = 1 # 是否画图
        self.numRows = 0 # 绘图区域被分为几行
        self.numCols = 0 # 绘图区域被分为几列
        # 然后按照从左到右，从上到下的顺序对每个子区域进行编号，左上的子区域的编号为1
        self.plotNum = 0 # 指定当前绘画图片的位置，对于ax_array下标从0开始
        self.ax_plot = [] # 放置ax.plot返回的第一个元素

        self.graphInfo = {} # 保存每幅图的信息
        self.newData = {} # 存放新进来每幅图的每条曲线的data数据
        self.backgrounds = [] # 存放每个画布背景
        self.fig = None
        self.width = 6.4
        self.height = 4.8
        self.dpi = 100

        # 只增加行，不按列增加
        self.numCols = 1

    def addGraph(self, name,
                 points = None,
                 dataMin=-1.0, dataMax=1.0,
                 xGrid=20, yGrid=None,
                 dataName=None,
                 color=COLORS['red'],
                 backgroundColor = COLORS['white'],
                 type="-"
                 ):
        points = self._getBestPoints(points)
        title = name + ' (%.1f~%.1f)' % (dataMin, dataMax)
        # data存放数据纵坐标
        if dataName == None:
            data = [None] * points
        else:
            data = {}
            for item in dataName:
                data[item] = [None] * points
        self.numRows += 1
        plot_num = self.plotNum
        self.ax_plot.append(None)
        self.plotNum += 1
        self.graphInfo[name] = [title,
                                points,
                                plot_num,
                                dataMin, dataMax,
                                xGrid, yGrid,
                                dataName, data,
                                color, backgroundColor,
                                type, name]
        if dataName == None:
            self.newData[name] = Queue.Queue()
        else:
            self.newData[name] = {}
            for dataname in dataName:
                self.newData[name][dataname] = Queue.Queue()
                # self.newData[name][dataname] = []

    def appendData(self, name, inputData):
        if isinstance(inputData, dict):
            for dataname,datavalue in inputData.items():
                self.newData[name][dataname].put(datavalue)
                # self.newData[name][dataname].append(datavalue)
        else:
            self.newData[name].put(inputData)

    def _OnTimer(self, ax_array):

        start = time.time()
        for name,value in self.newData.items():
            if isinstance(value, dict):
                # start = time.time()
                # start = time.time()
                plot_num = self.graphInfo[name][2]
                self.fig.canvas.restore_region(self.backgrounds[plot_num])
                ready = 0
                for dataname in self.graphInfo[name][7]:
                    if not value[dataname].empty():
                        ready +=1
                # end = time.time()  # 队列取出来性能瓶颈
                # print end - start
                # 如果画布设计的所有曲线都有新的数据的时候才绘制
                if ready == len(self.graphInfo[name][7]): # XXX
                    # start = time.time()
                    for dataname, datavalue in value.items():
                        # 此时self.graphInfo[name][8]是一个字典
                        # self.ax_plot[plot_num]也是一个字典
                        # 结果显示这一部分在数据比较的时候出现了延时达到0.06

                        # start = time.time()
                        newdata = datavalue.get()
                        # end = time.time()
                        # print end - start
                        self.graphInfo[name][8][dataname] = self.graphInfo[name][8][dataname][1:] + [newdata]

                        self.ax_plot[plot_num][dataname].set_ydata(self.graphInfo[name][8][dataname])

                        ax_array[plot_num].draw_artist(self.ax_plot[plot_num][dataname])

                        # ax_array[plot_num].figure.canvas.draw()
                    # end = time.time()  # 队列取出来性能瓶颈
                    # print end - start
                    # start = time.time()
                    self.fig.canvas.blit(ax_array[plot_num].bbox)
                    # end = time.time()  # 上200HZ的性能瓶颈
                    # print end - start
                else:
                    pass
                # end = time.time()  # 队列取出来性能瓶颈
                # print end - start

            else:
                # start = time.time()
                if not value.empty():
                    # start = time.time()
                    newdata = value.get()
                    # end = time.time()
                    # print end - start
                    # print newdata
                    # data = self.graphInfo[name][8]
                    # print self.graphInfo[name][8]

                    self.graphInfo[name][8] = self.graphInfo[name][8][1:] + [newdata]
                    plot_num = self.graphInfo[name][2]
                    # 这里是否需要考虑是字典，取决于下面代码的处理
                    self.fig.canvas.restore_region(self.backgrounds[plot_num])

                    self.ax_plot[plot_num].set_ydata(self.graphInfo[name][8])
                    ax_array[plot_num].draw_artist(self.ax_plot[plot_num])
                    # ax_array[plot_num].figure.canvas.draw()

                    self.fig.canvas.blit(ax_array[plot_num].bbox)
                # end = time.time()  # 队列取出来性能瓶颈
                # print end - start
        end = time.time()  # 队列取出来性能瓶颈
        print end - start


    def run(self):
        self._plotGraph()

    def _getBestPoints(self, points):
        # 如果points缺省则一个像素一个点
        if points == None:
            points = int(self.dpi * self.width)
        return points

    def _plotGraph(self):
        if self.numRows == 0:
            return
        else:
            common_sharex = None
        self.fig, ax_array = plt.subplots(self.numRows, self.numCols, sharex=True, figsize=(self.width,self.height)) # figsize = ()
        # figsize指定宽和高，单位是英寸
        # dpi参数指定绘图对象的分辨率,即每英寸多少个像素
        # print self.fig.get_figheight()
        # print self.fig.get_figwidth()
        # print self.fig.get_dpi() # 100.0
        self.fig.set_dpi(self.dpi)
        # self.fig.set_figheight()
        # self.fig.set_figwidth()
        # self.fig.show()
        # self.fig.canvas.draw()
        for_state = 0 # 这个用于记录下面for执行到第几次了（用于对图片做一些细节调整）
        max_for_state = len(self.graphInfo)
        for name,InfoTuple in self.graphInfo.items():
            for_state += 1
            title = InfoTuple[0]
            points = InfoTuple[1]
            plot_num = InfoTuple[2]
            dataMin = InfoTuple[3]
            dataMax = InfoTuple[4]
            xGrid = InfoTuple[5]
            yGrid = InfoTuple[6]
            dataName = InfoTuple[7]
            color = InfoTuple[9]
            backgroundColor = InfoTuple[10]
            type = InfoTuple[11]
            name = InfoTuple[12]

            # https://stackoverflow.com/questions/8955869/why-is-plotting-with-matplotlib-so-slow
            # self.backgrounds[plot_num] = self.fig.canvas.copy_from_bbox(ax_array[plot_num].bbox) # 不残影要素

            # 设置坐标轴范围
            ax_array[plot_num].set_ylim([dataMin, dataMax])
            ax_array[plot_num].set_xlim([0, points])
            # ax_array[plot_num].set_xticks(np.linspace(0,points,points))
            # ax_array[plot_num].set_xticks(range(points))
            # 如果不是最后一张图，不显示x坐标
            if for_state < max_for_state+1:
                # print "X"
                plt.setp(ax_array[plot_num].get_xticklabels(), visible=False)

            # ax_array[plot_num].set_xticklabels([]) # 不显示x刻度标注
            # ax_array[plot_num].set_yticklabels([])
            # 为避免y坐标tick重合，将最后一个设为不可见
            # if for_state > 1:
            #     yticks = ax_array[plot_num].yaxis.get_major_ticks()
            #     yticks[-1].label1.set_visible(False)
            # 设置坐标轴刻度，让matplotlib自适应
            # ax_array[plot_num].set_xticks([])
            # min_int = int(dataMin)
            # max_int = int(dataMax)
            # if (max_int - min_int) >= 20:
            #     step = 10
            # else:
            #     step = 1
            # ax_array[plot_num].set_yticks(range(min_int, max_int+1, step))
            # 设置坐标刻度
            # 启动网格
            # ax_array[plot_num].grid(True, linestyle="--", which='both')
            if dataName == None:
                # 参考https://www.cnblogs.com/webary/p/5813855.html
                if type in ['-','--','-.',':','.']:
                    # print range(points)
                    self.ax_plot[plot_num], = ax_array[plot_num].plot(range(points),self.graphInfo[name][8],color=color,
                                                                  linestyle=type, label = title, animated=True)
                elif type in ['o']:
                    self.ax_plot[plot_num], = ax_array[plot_num].plot(range(points), self.graphInfo[name][8],
                                                                      color=color,
                                                                      marker=type, label = title, animated=True)

                # https://blog.csdn.net/helunqu2017/article/details/78659490
                # 设置标题
                # ax_array[plot_num].set_title(title, color=COLORS['black'], fontsize='small')

            else:
                self.ax_plot[plot_num] = {}
                for dataname in dataName:
                    if type in ['-', '--', '-.', ':', '.']:
                        # print range(points)
                        self.ax_plot[plot_num][dataname], = ax_array[plot_num].plot(range(points), self.graphInfo[name][8][dataname],
                                                                          color=color[dataname],
                                                                          linestyle=type, label=dataname, animated=True)
                    elif type in ['o']:
                        self.ax_plot[plot_num][dataname], = ax_array[plot_num].plot(range(points), self.graphInfo[name][8][dataname],
                                                                          color=color[dataname],
                                                                          marker=type, label=dataname, animated=True)
            # 调整图例位置
            ax_array[plot_num].legend(loc="upper left", ncol=1, prop=font_manager.FontProperties(size=10))
            ax_array[plot_num].set_autoscale_on(False)
        self.fig.canvas.draw()
        self.backgrounds = [self.fig.canvas.copy_from_bbox(ax.bbox) for ax in ax_array]
        # 调整图像边框，使得各个图之间的间距为0
        plt.subplots_adjust(wspace=0, hspace=.2)
        timer = self.fig.canvas.new_timer(interval = self.time_interval)
        timer.add_callback(self._OnTimer, ax_array)
        timer.start()
        print "show before"
        # plt.ion()
        plt.show()
        # plt.show(block=False)
        print "show after"


class MergeGraphPack(object):
    def __init__(self, time_interval=1, new_thread=True):
        self.new_thread = new_thread
        self.g = MergeGraph(time_interval=1, new_thread=new_thread)

    def addGraph(self, name,
                 points=None,
                 dataMin=-1.0, dataMax=1.0,
                 xGrid=20, yGrid=None,
                 dataName=None,
                 color=COLORS['red'],
                 backgroundColor=COLORS['white'],
                 type="-"
                 ):
        self.g.addGraph(name=name,
                        points=points,
                        dataMin=dataMin,
                        dataMax=dataMax,
                        xGrid=xGrid,
                        yGrid=yGrid,
                        dataName=dataName,
                        color=color,
                        backgroundColor=backgroundColor,
                        type=type)

    def appendData(self, name, inputData):
        self.g.appendData(name, inputData)

    def show(self):
        if self.new_thread:
            self.g.start()
        else:
            self.g.run()
        # time.sleep(8)



if __name__ == "__main__":
    new_thread = True
    points = None
    g = MergeGraphPack(time_interval=1, new_thread=new_thread)  # 单位可能是毫秒，画图数据监听时间间隔
    g.addGraph(name="data 1",  points=points, dataMin=-1.0, dataMax=10.,type="-")
    g.addGraph(name="Figure 2", points=points, dataMin=-1, dataMax=1.0,type="-")
    g.addGraph(name="Figure 3",  points=points, dataName=['A','B'], color={'A':COLORS['red'],'B':COLORS['blue']},
               dataMin=-100.0, dataMax=100.0,type="-")
    g.show()
    # 需要解决的问题：输入数据要在图像准备好了再输入
    points = 300
    print "do some operations"
    data_1 = 0
    data_2 = 0
    x = np.linspace(0, np.pi, 300)
    y = np.sin(x)
    data_3 = 0
    data_4 = 0
    for i in xrange(0, points*3):
        # print "Here: ", i
        # start = time.time()  # 上200HZ的性能瓶颈
        g.appendData("data 1", data_1)
        g.appendData("Figure 2", data_2)
        g.appendData("Figure 3", {'A':data_3,
                                  'B':data_4})
        # print time.time() - start
        time.sleep(0.05)  # 一秒
        data_1 += 0.03
        data_2 = y[i%300]
        data_3 += 1
        data_4 += 2
    i = 0
    while i<50:
        i += 1
        time.sleep(1)
        # print "End"
