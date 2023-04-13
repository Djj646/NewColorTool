import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb

from .coloranalysis import kmeans, dbscan, gaussi

class ColorTool():
    def __init__(self):
        self.path = None
        self.ori_img = None # RGB格式，便于绘制
        self.ori_img_hsv = None # hsv格式
        self.rawlist = None
        
        self.color_type = 0 # 颜色模式, 0为HSV, 1为RGB
        self.sort_method = 0 # 聚类方法, kmeans, 高斯混合, DBSCAN
        self.queue_method = 0 # 排序依据, H, S, V
        
        self.color_num = 1 # 颜色数量
        self.rawcolorlist = None # 暂存的分类好的颜色(未排序)
        # 排序好的颜色列表
        self.colorlist = np.array([
            [0, 0, 255],
            [237, 173, 158],
            [140, 199, 181],
            [120, 205, 205],
            [79, 148, 205],
            [205, 150, 205],
            [0, 255, 0],
        ])

    def loadImg(self):
        '''读取文件

        '''
        if self.path == None or self.path == '':
            return False
        img = cv2.imdecode(np.fromfile(self.path, dtype=np.uint8), -1) # 兼容中文路径
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # 将opencv默认BGR转为RGB
        self.ori_img = img_rgb
        self.ori_img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        return True
            
            
    def img2list(self):
        '''将rgb或hsv图片转化为三维数组便于聚类分析

        Args:
            ori_pic (ndarray): 原始格式(h, w, ch)

        Returns:
            ndarray : 转换后格式(h*w, ch)
        '''
        if self.color_type==1:
            img = self.ori_img
        elif self.color_type==0:
            img = self.ori_img_hsv
            
        ch1 = img[:, :, 0].flatten()
        ch2 = img[:, :, 1].flatten()
        ch3 = img[:, :, 2].flatten()
        
        rawlist = np.vstack((ch1, ch2, ch3))
        self.rawlist = rawlist.astype(np.double)
    
    def sort(self):
        '''颜色分析核心: 选择算法种类

        Args:
            rawlist_type (int): 颜色模式序号rgb或hsv, 若为rgb, 排序前需先转为hsv
            rawlist (ndarray): 待分类初始字符串
            sort_method (int): 聚类方法序号
            color_num (int): 待分类颜色数量

        Returns:
            list: 分类后的颜色列表, 最后都转化为hsv格式(等待排序)
        '''
        if self.sort_method == 2:
            self.rawcolorlist = dbscan(self.rawlist, self.color_num)
        elif self.sort_method == 0:
            self.rawcolorlist = kmeans(self.rawlist, self.color_num)
        elif self.sort_method == 1:
            self.rawcolorlist = gaussi(self.rawlist, self.color_num)

    def queue(self):
        # 变成3维形式，便于转化
        rawcolorlist = np.array(self.rawcolorlist)
        if len(rawcolorlist.shape)==2:
            w, ch = rawcolorlist.shape
            rawcolorlist = rawcolorlist.reshape(-1, w, ch).astype(np.float32)
        
        # 先全部转HSV
        queuecolorlist = cv2.cvtColor(rawcolorlist, cv2.COLOR_RGB2HSV)
            
        # 排序
        coe = np.zeros(3)
        if self.queue_method == 0:
            coe[0] = 1
        elif self.queue_method == 1:
            coe[1] = 1
        elif self.queue_method == 2:
            coe[2] = 1
        
        index = np.argsort(np.dot(queuecolorlist, coe)).reshape(-1)[::-1]
        list = rawcolorlist[:, index] # 排序好后的形状为[1, colors, 3]
        self.colorlist = list.reshape(-1, 3) # 形状整理为[colors, 3]
    
    def histDraw(self):
        # 设置窗口子图像高度比例
        fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(8, 6), sharex=True, gridspec_kw={'height_ratios': [1, 1, 2]})

        # 绘制 H 通道直方图分布曲线
        axes[0].hist(self.ori_img_hsv[:, :, 0].ravel(), bins=180, range=[0, 180], density=True)
        axes[0].set_title('H Channel')
        axes[0].set_xticks(range(0,180,15))

        # 绘制 S 通道直方图分布曲线
        axes[1].hist(self.ori_img_hsv[:, :, 1].ravel(), bins=256, density=True)
        axes[1].set_title('S Channel')
        axes[0].set_xticks(range(0,256,15))

        # 绘制 V 通道直方图分布曲线
        axes[2].hist(self.ori_img_hsv[:, :, 2].ravel(), bins=256, density=True)
        axes[2].set_title('V Channel')
        axes[0].set_xticks(range(0,256,15))

        # 调整子图像之间的距离
        plt.subplots_adjust(hspace=0.5)
        
        # 在整个图表上添加标题
        fig.suptitle('HSV Channel Histogram Distribution')

        
        # 显示窗口
        plt.show()