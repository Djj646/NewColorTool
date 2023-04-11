# coding:utf-8
import json

from PyQt5.QtCore import Qt, pyqtSignal, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QPainterPath
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

from qfluentwidgets import ScrollArea, isDarkTheme, FluentIcon
from ..common.config import cfg, HELP_URL, REPO_URL, EXAMPLE_URL, FEEDBACK_URL
from ..common.icon import Icon
from ..components.link_card import LinkCardView
from ..components.sample_card import SampleCardView


class BannerWidget(QWidget):
    """ Banner widget """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFixedHeight(336)
        self.vBoxLayout = QVBoxLayout(self)
        self.galleryLabel = QLabel('Color Tool', self)
        self.banner = QPixmap('app/resource/images/header1.png')
        self.linkCardView = LinkCardView(self)

        self.galleryLabel.setObjectName('galleryLabel')

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 20, 0, 0)
        self.vBoxLayout.addWidget(self.galleryLabel)
        self.vBoxLayout.addWidget(self.linkCardView, 1, Qt.AlignBottom)
        self.vBoxLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.linkCardView.addCard(
            'app/resource/images/logo.png',
            self.tr('快速开始'),
            self.tr('ColorTool可以做什么？'),
            HELP_URL
        )

        self.linkCardView.addCard(
            FluentIcon.GITHUB,
            self.tr('GitHub参考'),
            self.tr(
                '欢迎访问作者主页'),
            REPO_URL
        )

        self.linkCardView.addCard(
            Icon.CODE,
            self.tr('使用示例'),
            self.tr(
                '一些使用示例'),
            EXAMPLE_URL
        )

        self.linkCardView.addCard(
            FluentIcon.FEEDBACK,
            self.tr('制作者说'),
            self.tr('本软件完全开源，请勿商用'),
            FEEDBACK_URL
        )

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.SmoothPixmapTransform | QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)
        w, h = self.width(), 200
        path.addRoundedRect(QRectF(0, 0, w, h), 10, 10)
        path.addRect(QRectF(0, h-50, 50, 50))
        path.addRect(QRectF(w-50, 0, 50, 50))
        path.addRect(QRectF(w-50, h-50, 50, 50))
        path = path.simplified()

        # draw background color
        painter.fillPath(path, QColor(206, 216, 228))

        # draw banner image
        pixmap = self.banner.scaled(
            self.size(), transformMode=Qt.SmoothTransformation)
        path.addRect(QRectF(0, h, w, self.height() - h))
        painter.fillPath(path, QBrush(pixmap))


class HomeInterface(ScrollArea):
    """ Home interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.banner = BannerWidget(self)
        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)

        self.__initWidget()
        self.loadSamples()

    def __initWidget(self):
        self.__setQss()

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(self.view)
        self.setWidgetResizable(True)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 36)
        self.vBoxLayout.setSpacing(40)
        self.vBoxLayout.addWidget(self.banner)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

        cfg.themeChanged.connect(self.__setQss)

    def __setQss(self):
        self.view.setObjectName('view')
        theme = 'dark' if isDarkTheme() else 'light'
        with open(f'app/resource/qss/{theme}/home_interface.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def loadSamples(self):
        """ load samples """
        basicInputView = SampleCardView(
            self.tr("选择需要使用的功能模块"), self.view)
        basicInputView.addSampleCard(
            icon="app/resource/images/controls/Button.png",
            title="主功能区",
            content=self.tr(
                "主要功能区，对图片进行自定义规则色彩分析"),
            routeKey="mainfuncInterface",
            index=0
        )
        basicInputView.addSampleCard(
            icon="app/resource/images/controls/CheckBox.png",
            title="附加功能区",
            content=self.tr("自定义色块导出等其他功能"),
            routeKey="utilsInterface",
            index=1
        )
        self.vBoxLayout.addWidget(basicInputView)

        
