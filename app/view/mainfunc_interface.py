# coding:utf-8
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QFileDialog, QLabel
from PyQt5.QtGui import QPixmap, QImage
from qfluentwidgets import (ScrollArea, StateToolTip, FlowLayout, PushButton, SpinBox, ToolTipFilter, ToolButton, PrimaryPushButton, HyperlinkButton,
                            ComboBox, PixmapLabel, RadioButton, CheckBox, Slider, SwitchButton, MessageBox)

from .gallery_interface import GalleryInterface
from ..functions.colortool import ColorTool
from ..common.config import cfg

import cv2
import numpy as np
import threading
import os

class MainFuncInterface(GalleryInterface):
    """ 主要功能区 """
    # 完成信号
    finishSignal = pyqtSignal(str)
    def __init__(self, parent=None):
        super().__init__(
            parent=parent
        )
        self.colorTool = ColorTool()
        self.pix = None
        self.imgLabel = PixmapLabel(self)
        self.resultLabels = []
        self.resultWidget = QWidget(self)
        self.resultWidgetLayout = FlowLayout(self)
        self.resultWidget.setLayout(self.resultWidgetLayout)
        
        # 加载图片
        self.loadImg()
        
        # 定义 QPixmap 缓存
        self.pixmap_cache = QtGui.QPixmapCache()
        
        # 设置缩放滑动条
        self.slider = Slider(Qt.Horizontal, self)
        self.slider.setRange(0, 520)
        self.slider.setValue(260)
        self.vBoxLayout.addWidget(self.slider)
        # 连接 Slider 控件的 valueChanged 信号到缩放槽函数
        self.slider.valueChanged.connect(self.scaleImage)

        card = self.addExampleCard(
            self.tr('图片视窗'),
            self.imgLabel,
            stretch=0,
            align=Qt.AlignCenter
        )
        card.card.installEventFilter(ToolTipFilter(card.card, showDelay=520))
        card.card.setToolTip(self.tr('准备起飞！🚀'))
        card.card.setToolTipDuration(1200)
        
        # 分析结果
        self.addExampleCard(
            self.tr('分析结果'),
            self.resultWidget,
            stretch=1
        )

        self.button2Order = 'finish'
        self.stateTooltip = None
        self.button1 = PushButton('打开文件')
        self.button2 = PushButton('开始分析')
        self.addExampleCard(
            self.tr('导入与开始'),
            self.createWidgetRep(self.button1, self.button2, True),
            stretch=1
        )
        
        # 颜色模式和分类算法
        self.comboBox1 = ComboBox()
        self.comboBox1.addItems(['HSV', 'RGB'])
        self.comboBox1.setCurrentIndex(0)
        self.comboBox1.setMinimumWidth(210)
        self.comboBox2 = ComboBox()
        self.comboBox2.addItems(['K-Means', 'GMM', 'DBSCAN'])
        self.comboBox2.setCurrentIndex(0)
        self.comboBox2.setMinimumWidth(210)
        self.addExampleCard(
            self.tr('颜色模式与分类算法'),
            self.createWidgetRep(self.comboBox1, self.comboBox2, True),
            stretch=1
        )
        
        self.spinBox = SpinBox(self)
        self.spinBox.setValue(self.colorTool.color_num)
        self.addExampleCard(
            self.tr("颜色数量"),
            self.spinBox
        )
        
        self.comboBox3 = ComboBox()
        self.comboBox3.addItems(['H', 'S', 'V'])
        self.comboBox3.setCurrentIndex(0)
        self.comboBox3.setMinimumWidth(210)
        self.addExampleCard(
            self.tr('排序方式'),
            self.comboBox3
        )
        
        # 输出文件夹
        self.outputFolder = "./app/output"
        
        # 输出格式
        self.editReal = [52, 124, 0]
        
        self.initConnect()
    
    # 缩放图像
    def scaleImage(self, value):
        if self.pix == None:
            return
        # 计算缩放比例
        scale = value / 260.0
        
        # 计算缩放后的图片宽度
        scaled_width = self.pix.width() * scale

        # 根据窗口宽度和缩放比例计算缩放上下限
        min_width = self.view.width() * 0.1
        max_width = self.view.width() * 0.88

        # 根据缩放上下限对缩放比例进行调整
        if scaled_width < min_width:
            scale = min_width / self.pix.width()
        elif scaled_width > max_width:
            scale = max_width / self.pix.width()

        # 构建缓存标识符
        cache_id = "scaled_pix_{:.2f}".format(scale)

        # 尝试从缓存中获取已缓存的图像
        cached_pixmap = self.pixmap_cache.find(cache_id)
        
        if cached_pixmap is None:
            scaled_pix = self.pix.scaledToWidth(int(self.pix.width() * scale), Qt.SmoothTransformation)
            self.pixmap_cache.insert(cache_id, scaled_pix)
        else:
            scaled_pix = cached_pixmap
        
        # 设置缩放后的图像
        self.imgLabel.setPixmap(scaled_pix)
    
    # 子线程开启
    def thread(self, func, args):
        t = threading.Thread(target=func,args=args)#target接受函数对象  arg接受参数  线程会把这个参数传递给func这个函数
        t.setDaemon(True)#守护
        t.start()
    
    def initConnect(self):
        self.button1.clicked.connect(self.onOpenButtonClicked)
        self.button2.clicked.connect(self.onStateButtonClicked)
        
        self.comboBox1.currentTextChanged.connect(self.onColorTypeChanged)
        self.comboBox2.currentTextChanged.connect(self.onSortMethodChanged)
        self.comboBox3.currentTextChanged.connect(self.onQueueMethodChanged)
        
        self.spinBox.valueChanged.connect(self.onColornumChanege)
        
        self.finishSignal.connect(self.setButton1Order)
    
    # 清空widget，并添加列表内多个组件
    # 采用create返回的方法会导致布局消失
    @staticmethod
    def attachWidget(widget, widgetlist, animation=False):
        layout = widget.layout()

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setVerticalSpacing(20)
        layout.setHorizontalSpacing(10)
        
        for widget in widgetlist:
            layout.addWidget(widget)
    
    # 两组件在同一卡片内
    @staticmethod
    def createWidgetRep(widget1, widget2, animation=False):
        widget = QWidget()
        layout = FlowLayout(widget, animation)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setVerticalSpacing(20)
        layout.setHorizontalSpacing(10)

        layout.addWidget(widget1)
        layout.addWidget(widget2)
        
        return widget
    
    def onOpenButtonClicked(self):
        self.colorTool.path, _ = QFileDialog.getOpenFileName(self, self.tr('选择图片'),'.','图像文件(*.jpg *.png)')
        self.loadImg()
    
    def onStateButtonClicked(self):
        if self.stateTooltip:
            if self.order == 'analysising':
                self.stateTooltip.setTitle(self.tr('中止分析'))
                self.stateTooltip.setContent(
                    self.tr('分析已终止') + '🤐')
                self.button2.setText(self.tr('开始分析'))
                self.stateTooltip.setState(True)
                self.stateTooltip = None
            elif self.order == 'finish':
                self.stateTooltip.setTitle(self.tr('完成分析'))
                self.stateTooltip.setContent(
                    self.tr('分析已完成') + '😎')
                self.button2.setText(self.tr('开始分析'))
                self.stateTooltip.setState(True)
                self.updateResultLabels()
                # 消除状态框
                self.stateTooltip = None
        else:
            if self.colorTool.path == None:
                title = self.tr('温馨提示')
                content = self.tr("请先导入图片再执行其他操作")
                w = MessageBox(title, content, self.window())
                if w.exec():
                    self.onOpenButtonClicked()
                    return
                else:
                    return
            self.order = 'analysising'
            # self.order = 'finish'
            self.onStart()
            self.stateTooltip = StateToolTip(
                self.tr('正在分析'), self.tr('请稍等片刻')+'🧐', self.window())
            self.button2.setText(self.tr('停止分析'))
            self.stateTooltip.move(self.stateTooltip.getSuitablePos())
            self.stateTooltip.show()
    
    def onStart(self):
        self.thread(func=self.start, args=[self])
    
    @staticmethod
    def start(self):
        self.loadImg() # 包括ColorTool.loadImg
        self.colorTool.img2list()
        self.colorTool.sort()
        self.colorTool.queue()
        
        self.finishSignal.emit('finish')
        
    def setButton1Order(self, order):
        self.order = order
        self.onStateButtonClicked()
    
    def onColorTypeChanged(self, type):
        if type == 'HSV':
            self.colorTool.color_type = 0
        elif type == 'RGB':
            self.colorTool.color_type = 1
    
    def onSortMethodChanged(self, sort):
        if sort == 'K-Means':
            self.colorTool.sort_method = 0
        elif sort == 'GMM':
            self.colorTool.sort_method = 1
        elif sort == 'DBSCAN':
            self.colorTool.sort_method = 2
    
    def onColornumChanege(self, num):
        self.colorTool.color_num = num
    
    def onQueueMethodChanged(self, queue):
        if queue == 'H':
            self.colorTool.queue_method = 0
        elif queue == 'S':
            self.colorTool.queue_method = 1
        elif queue == 'V':
            self.colorTool.queue_method = 2
            
        self.colorTool.queue()
        self.updateResultLabels()
    
    @staticmethod
    def img2pix(rgb_img):
        y, x = rgb_img.shape[:-1]
        frame = QImage(rgb_img, x, y, x*3, QImage.Format_RGB888) # x*3防止倾斜
        pix = QPixmap.fromImage(frame)
        
        return pix
        
    def loadImg(self):
        if not self.colorTool.loadImg():
            return
        
        self.pix = self.img2pix(self.colorTool.ori_img)
        
        w = int(min(self.pix.width(),self.view.width()*0.88))
        h = self.pix.height()
        
        value = min(w/self.pix.width()*260, 520)
        self.slider.setValue(int(value))
        
        # 保持缩放比和平滑无锯齿
        self.imgLabel.setPixmap(self.pix.scaled(
            w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))
    
    @staticmethod
    def clearWidget(widget):
        layout = widget.layout()
        if layout:
            layout.takeAllWidgets()
    
    def updateResultLabels(self):
        self.resultLabels.clear()
        self.clearWidget(self.resultWidget)
        # 结果转为label导入
        colorlist = self.colorTool.colorlist
        h = cfg.BLOCK_H
        w = cfg.BLOCK_W
        singleimg = np.zeros((h, w, 3), np.uint8)
        
        for i in range(len(colorlist)):
            color = colorlist[i]
            color = tuple([int(x) for x in color]) # 转int元组防报错
            cv2.rectangle(singleimg, (0,0), (w, h), color, -1) # RGB格式
            pix = self.img2pix(singleimg)
            # label销毁问题
            label = PixmapLabel(self)
            label.setPixmap(pix)
            self.resultLabels.append(label)

        self.attachWidget(self.resultWidget, self.resultLabels, True)
        
    def onOutputFolderChange(self, path):
        self.outputFolder = path
        
    def onSave(self):
        filepath = os.path.basename(self.colorTool.path)  # 提取文件名
        filetitle, ext = os.path.splitext(filepath)  # 分离文件名和扩展名
        outputpath = self.outputFolder
        
        # 清除上一次导出的
        # 列出路径下的所有文件名
        files = os.listdir(outputpath)
        # 遍历所有文件名
        for filename in files:
            if filename.startswith(filetitle):
                # 如果文件名以filetitle开头，则删除该文件
                os.remove(os.path.join(outputpath, filename))
        
        colorlist = self.colorTool.colorlist
        [h, w, span] = self.editReal
        spanimg = np.full((h, span, 3), fill_value=255, dtype=np.uint8)
        totalimg = None
        
        for i, color in enumerate(colorlist):
            color = tuple(int(x) for x in color)
            # 创建并保存单个图片
            singleimg = np.full((h, w, 3), color, dtype=np.uint8)
            singleimg = cv2.cvtColor(singleimg, cv2.COLOR_BGR2RGB)
            name = filetitle + '_rgb_{}_{}_{}'.format(*color)
            cv2.imwrite(os.path.join(outputpath, name + '.png'), singleimg)
            # 将单个图片拼接到大图像中
            if i == 0:
                totalimg = singleimg
            else:
                totalimg = cv2.hconcat([totalimg, spanimg, singleimg])
        # 将大图像保存到磁盘
        cv2.imwrite(os.path.join(outputpath, filetitle+"_CARD.png"), totalimg)
        
    def onPltDraw(self):
        if self.colorTool.ori_img_hsv is not None:
            self.colorTool.histDraw()
        