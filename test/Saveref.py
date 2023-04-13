import os
import cv2
import numpy as np

def saveimgs(self):
    path = "./imgs"
    # 获取所有 PNG 格式的图片文件名
    files = [os.path.splitext(f)[0] for f in os.listdir(path) if f.endswith(".png")]

    # 遍历颜色列表生成图片
    colorlist = self.colortool.color_list
    [h, w, span] = self.editreal
    spanimg = np.full((h, span, 3), fill_value=255, dtype=np.uint8)
    totalimg = None
    for i, color in enumerate(colorlist):
        color = tuple(int(x) for x in color)
        # 创建并保存单个图片
        singleimg = np.full((h, w, 3), color, dtype=np.uint8)
        name = 'rgb_{}_{}_{}'.format(*color)
        if name not in files:
            cv2.imwrite(os.path.join(path, name + '.png'), singleimg)
        # 将单个图片拼接到大图像中
        if i == 0:
            totalimg = singleimg
        else:
            totalimg = cv2.hconcat([totalimg, spanimg, singleimg])
    # 将大图像保存到磁盘
    cv2.imwrite(os.path.join(path, "atla.png"), totalimg)
