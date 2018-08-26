# -*- coding: utf-8 -*-
# 查看PyQt5源代码，最终才搞明白
# https://www.cnblogs.com/hhh5460/p/5189843.html
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget,QGraphicsScene,QGraphicsView,QLabel,QScrollArea,QSlider



from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

import numpy as np
import random

from CombineDesign.offlinescripts import plot_leadOne

class Figure_Canvas(FigureCanvas):   # 通过继承FigureCanvas类，使得该类既是一个PyQt5的Qwidget，又是一个matplotlib的FigureCanvas，这是连接pyqt5与matplot                                          lib的关键

    def __init__(self, parent=None, width=11, height=5, dpi=100):
        fig = Figure(figsize=(16, 9), dpi=100)  # 创建一个Figure，注意：该Figure为matplotlib下的figure，不是matplotlib.pyplot下面的figure
        FigureCanvas.__init__(self, fig) # 初始化父类
        self.setParent(parent)
        self.fig = fig

    def plotleadone(self, logname="C:/Users/admin/Desktop/0620-mkz1/raw_logs/zmq-1529460872.log"):
        # plot_leadOne.main(logname, self.fig, None)  #  第三个参数接口没有保留，新增加了一个fig接口
        ax = self.fig.add_subplot(111)
        ax.plot(np.random.rand(10))



class MyView(QtWidgets.QGraphicsView):
    def __init__(self):
        QtWidgets.QGraphicsView.__init__(self)

        scene = QtWidgets.QGraphicsScene(self)
        self.scene = scene

        self.canvas = Figure_Canvas()
        self.canvas.plotleadone()
        scene.addWidget(self.canvas)

        self.setScene(scene)

        # 为canvas 设置监听事件
        self.canvas.mpl_connect('button_press_event', self.onclick)

    def onclick(self, event):
        if event.inaxes is None:
            return
        print '%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' % ('double' if event.dblclick else 'single', event.button, event.x, event.y, event.xdata, event.ydata)

    def wheelEvent(self, event):
        # 属性设置 参看 GraphicsviewZoomTest
        # self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)  #  测试失败
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        zoom_in = 1.15
        zoom_out = 1.0 / zoom_in
        # if event.delta() > 0: # PyQt4
        if event.angleDelta().y() > 0:
            self.scale(zoom_in, zoom_in)
        else:
            self.scale(zoom_out, zoom_out)


class Window(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        # self.figure = plt.figure()
        # self.axes = self.figure.add_subplot(111)
        # # We want the axes cleared every time plot() is called
        # self.axes.hold(False)
        # self.canvas = FigureCanvas(self.figure)
        # self.canvas = Figure_Canvas()
        # self.canvas.plotleadone()

        self.viewer = MyView()

        self.toolbar = NavigationToolbar(self.viewer.canvas, self)
        # self.toolbar.hide()

        # Just some button
        self.button1 = QtWidgets.QPushButton('Plot')
        self.button1.clicked.connect(self.plot)

        self.button2 = QtWidgets.QPushButton('Zoom')
        self.button2.clicked.connect(self.zoom)

        self.button3 = QtWidgets.QPushButton('Pan')
        self.button3.clicked.connect(self.pan)

        self.button4 = QtWidgets.QPushButton('Home')
        self.button4.clicked.connect(self.home)

        # set the layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.toolbar)

        #
        # self.graphicview = QGraphicsView()  # 第一步，创建一个QGraphicsView
        # self.graphicview.setObjectName("figure_graphicview")
        # graphicscene = QGraphicsScene()  # 第三步，创建一个QGraphicsScene，因为加载的图形（FigureCanvas）不能直接放到graphicview控件中，必须先放到graphicScene，然后再把graphicscene放到graphicview中
        # graphicscene.addWidget(self.canvas)  # 第四步，把图形放到QGraphicsScene中，注意：图形是作为一个QWidget放到QGraphicsScene中的
        # self.graphicview.setScene(graphicscene)  # 第五步，把QGraphicsScene放入QGraphicsView
        # self.graphicview.show()  # 最后，调用show方法呈现图形！Voila!!



        layout.addWidget(self.viewer)
        # layout.addWidget(self.graphicview)
        # layout.addWidget(self.canvas)

        btnlayout = QtWidgets.QHBoxLayout()
        btnlayout.addWidget(self.button1)
        btnlayout.addWidget(self.button2)
        btnlayout.addWidget(self.button3)
        btnlayout.addWidget(self.button4)
        qw = QtWidgets.QWidget(self)
        qw.setLayout(btnlayout)
        layout.addWidget(qw)

        self.setLayout(layout)

    def home(self):
        self.toolbar.home()

    def zoom(self):
        self.toolbar.zoom()

    def pan(self):
        self.toolbar.pan()

    def plot(self):
        ''' plot some random stuff '''
        # data = [random.ra
        pass

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    main = Window()
    main.setWindowTitle('Simple QTpy and MatplotLib example with Zoom/Pan')
    main.show()

    sys.exit(app.exec_())