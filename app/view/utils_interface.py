# coding:utf-8
from qfluentwidgets import (PushButton, SpinBox, MessageBox, TextWrap)

from .gallery_interface import GalleryInterface
from .mainfunc_interface import MainFuncInterface

from PyQt5.QtCore import Qt, pyqtSignal

class UtilsInterface(GalleryInterface):
    """ 附加功能区 """
    saveSignal = pyqtSignal()
    drawSignal = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(
            parent=parent
        )
        
        self.button1 = PushButton(self.tr('导出格式'))
        self.button2 = PushButton(self.tr('保存导出'))
        self.addExampleCard(
            self.tr('色块导出自定义'),
            MainFuncInterface.createWidgetRep(self.button1, self.button2, True),
            stretch=1
        )
        
        # 色彩分布直方图
        self.button3 = PushButton(self.tr('色彩分布直方图'))
        self.addExampleCard(
            self.tr('色彩分布'),
            self.button3
        )
        
        self.initConnect()
    
    def initConnect(self):
        self.button1.clicked.connect(self.showMessageDialog)
        self.button2.clicked.connect(lambda :self.saveSignal.emit())
        self.button3.clicked.connect(lambda :self.drawSignal.emit())
    
    def showMessageDialog(self):
        title = self.tr('导出自定义')
        content = self.tr(
            "功能暂未开放，敬请期待！")
        w = MessageBox(title, content, self.window())
        if w.exec():
            print('Yes button is pressed')
        else:
            print('Cancel button is pressed')