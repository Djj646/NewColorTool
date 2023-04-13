from typing import List
from PyQt5.QtCore import Qt, pyqtSignal, QEasingCurve
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QFrame, QWidget

from qfluentwidgets import (NavigationInterface, NavigationItemPostion, MessageBox,
                            isDarkTheme, PopUpAniStackedWidget)
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import FramelessWindow

from .title_bar import CustomTitleBar
from .gallery_interface import GalleryInterface
from .home_interface import HomeInterface
from .mainfunc_interface import MainFuncInterface
from .utils_interface import UtilsInterface

# 配置信息
from .setting_interface import SettingInterface, cfg

from ..components.avatar_widget import AvatarWidget
from ..common.icon import Icon
from ..common.signal_bus import signalBus

# 当前窗口类
class StackedWidget(QFrame):
    """ Stacked widget """

    currentWidgetChanged = pyqtSignal(QWidget)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.view = PopUpAniStackedWidget(self)

        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.view)

        self.view.currentChanged.connect(
            lambda i: self.currentWidgetChanged.emit(self.view.widget(i)))

    def addWidget(self, widget):
        """ add widget to view """
        self.view.addWidget(widget)

    def setCurrentWidget(self, widget, popOut=False):
        widget.verticalScrollBar().setValue(0)
        if not popOut:
            self.view.setCurrentWidget(widget, duration=300)
        else:
            self.view.setCurrentWidget(
                widget, True, False, 200, QEasingCurve.InQuad)

    def setCurrentIndex(self, index, popOut=False):
        self.setCurrentWidget(self.view.widget(index), popOut)

#主窗口类 
class MainWindow(FramelessWindow):
    
    def __init__(self):
        super().__init__()
        self.setTitleBar(CustomTitleBar(self))
        self.hBoxLayout = QHBoxLayout(self)
        self.widgetLayout = QHBoxLayout()

        self.stackWidget = StackedWidget(self)
        # 导航栏
        self.navigationInterface = NavigationInterface(self, True, True)
        
        # 交互界面
        self.homeInterface = HomeInterface(self)
        self.mainfuncInterface = MainFuncInterface(self)
        self.utilsInterface = UtilsInterface(self)
        
        self.settingInterface = SettingInterface(self)
        
        self.stackWidget.addWidget(self.homeInterface)
        self.stackWidget.addWidget(self.mainfuncInterface)
        self.stackWidget.addWidget(self.utilsInterface)
        
        self.stackWidget.addWidget(self.settingInterface)
            
        # initialize layout
        self.initLayout()

        # add items to navigation interface
        self.initNavigation()

        self.initWindow()
        
        # 信号连接
        self.initConnect()
        
    def initConnect(self):
        self.settingInterface.outputFolderChanged.connect(self.mainfuncInterface.onOutputFolderChange)
        self.utilsInterface.saveSignal.connect(self.mainfuncInterface.onSave)
        self.utilsInterface.drawSignal.connect(self.mainfuncInterface.onPltDraw)
    
    def initLayout(self):
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.navigationInterface)
        self.hBoxLayout.addLayout(self.widgetLayout)
        self.hBoxLayout.setStretchFactor(self.widgetLayout, 1)

        self.widgetLayout.addWidget(self.stackWidget)
        self.widgetLayout.setContentsMargins(0, 48, 0, 0)

        signalBus.switchToSampleCard.connect(self.switchToSample)

        self.navigationInterface.displayModeChanged.connect(
            self.titleBar.raise_)
        self.titleBar.raise_()
        
    def initNavigation(self):
        self.homeInterface.setObjectName('homeInterface')
        self.mainfuncInterface.setObjectName('mainfuncInterface')
        self.utilsInterface.setObjectName('utilsInterface')
        self.settingInterface.setObjectName('settingsInterface')

        # 主页
        self.navigationInterface.addItem(
            routeKey=self.homeInterface.objectName(),
            icon=Icon.HOME,
            text=self.tr('主页'),
            onClick=lambda t: self.switchTo(self.homeInterface, t)
        )
        self.navigationInterface.addSeparator() # 主页与其他功能区加区分
        
        # 主要功能区
        self.navigationInterface.addItem(
            routeKey=self.mainfuncInterface.objectName(),
            icon=FIF.PALETTE,
            text=self.tr('主功能区'),
            onClick=lambda t: self.switchTo(self.mainfuncInterface, t),
            position=NavigationItemPostion.SCROLL
        )
        # 附加功能区
        self.navigationInterface.addItem(
            routeKey=self.utilsInterface.objectName(),
            icon=Icon.LAYOUT,
            text=self.tr('附加功能区'),
            onClick=lambda t: self.switchTo(self.utilsInterface, t),
            position=NavigationItemPostion.SCROLL
        )
        
        # 用户与设置
        self.navigationInterface.addWidget(
            routeKey='avatar',
            widget=AvatarWidget('app/resource/images/bbcat.png'),
            onClick=self.showMessageBox,
            position=NavigationItemPostion.BOTTOM
        )

        self.navigationInterface.addItem(
            routeKey=self.settingInterface.objectName(),
            icon=FIF.SETTING,
            text='Settings',
            onClick=lambda t: self.switchTo(self.settingInterface, t),
            position=NavigationItemPostion.BOTTOM
        )
        
        #!IMPORTANT: don't forget to set the default route key if you enable the return button
        self.navigationInterface.setDefaultRouteKey(
            self.homeInterface.objectName())

        self.stackWidget.currentWidgetChanged.connect(
            lambda w: self.navigationInterface.setCurrentItem(w.objectName()))
        self.navigationInterface.setCurrentItem(
            self.homeInterface.objectName())
        self.stackWidget.setCurrentIndex(0)
        
    def initWindow(self):
        self.resize(960, 780)
        self.setMinimumWidth(760)
        self.setWindowIcon(QIcon('app/resource/images/logo.png'))
        self.setWindowTitle('ColorTool')
        self.titleBar.setAttribute(Qt.WA_StyledBackground)

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

        cfg.themeChanged.connect(self.setQss)
        self.setQss()

    def setQss(self):
        color = 'dark' if isDarkTheme() else 'light'
        with open(f'app/resource/qss/{color}/main_window.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def switchTo(self, widget, triggerByUser=True):
        self.stackWidget.setCurrentWidget(widget, not triggerByUser)

    def resizeEvent(self, e):
        self.titleBar.move(46, 0)
        self.titleBar.resize(self.width()-46, self.titleBar.height())

    def showMessageBox(self):
        w = MessageBox(
            self.tr('你好！欢迎'),
            self.tr('这是你的用户区'),
            self
        )
        w.exec()

    def switchToSample(self, routeKey, index):
        """ switch to sample """
        interfaces = self.findChildren(GalleryInterface)
        for w in interfaces:
            if w.objectName() == routeKey:
                self.stackWidget.setCurrentWidget(w)
                w.scrollToCard(index)
        