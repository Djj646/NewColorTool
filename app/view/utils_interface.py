# coding:utf-8
from qfluentwidgets import (PushButton, MessageBox)

from .gallery_interface import GalleryInterface
from .mainfunc_interface import MainFuncInterface

class UtilsInterface(GalleryInterface):
    """ 附加功能区 """
    
    def __init__(self, parent=None):
        super().__init__(
            title="附加功能区",
            subtitle='其他功能',
            parent=parent
        )
        
        button1 = PushButton(self.tr('导出格式'))
        button1.clicked.connect(self.showMessageDialog)
        button2 = PushButton(self.tr('保存导出'))
        self.addExampleCard(
            self.tr('色块导出自定义'),
            MainFuncInterface.createWidgetRep(button1, button2, True),
            stretch=1
        )
        
        # 色彩分布直方图
        self.addExampleCard(
            self.tr('色彩分布'),
            PushButton(self.tr('色彩分布直方图'))
        )
        
    def showMessageDialog(self):
        title = self.tr('导出自定义')
        content = self.tr(
            "这是一个遮罩对话框")
        w = MessageBox(title, content, self.window())
        if w.exec():
            print('Yes button is pressed')
        else:
            print('Cancel button is pressed')