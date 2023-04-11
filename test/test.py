import cv2
import numpy as np
from sklearn.mixture import GaussianMixture as GMM
from sklearn.cluster import DBSCAN
from sklearn.cluster import KMeans

img = cv2.imdecode(np.fromfile("./test/test.jpg", dtype=np.uint8), -1)
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

ch1 = img_rgb[:, :, 0].flatten()
ch2 = img_rgb[:, :, 1].flatten()
ch3 = img_rgb[:, :, 2].flatten()

rawlist = np.vstack((ch1, ch2, ch3))
rawlist = rawlist.astype(np.double)

def find_in_list(lst, k):
    index_lst = []
    for i in range(len(lst)):
        if lst[i] == k:
            index_lst.append(i)
    return index_lst

def kmeans(rawlist, color_num):
    '''kmeans算法核心

    Args:
        rawlist (ndarray): 待聚类的三维数组列表
        color_num (int): 颜色数量

    Returns:
        ndarray: 聚类后得到的颜色列表，未排序
    '''
    kmeans = KMeans(n_clusters=color_num, max_iter=10, verbose=1, algorithm='auto')
    kmeans.fit(rawlist.T)
    
    rawcolorlist = kmeans.cluster_centers_
    
    return np.round(rawcolorlist)

def gaussi(rawlist, color_num):
    gmm = GMM(n_components=color_num, max_iter=1000)
    clusters = gmm.fit_predict(rawlist.T)
    labels_list = list(clusters)

    chs_sum = np.zeros((color_num, 3))
    
    # TODO: 将labels归类平均
    for i in range(color_num):
        indexes = find_in_list(labels_list, i)
        for j in range(len(indexes)):
            chs_sum[i] += rawlist[:, indexes[j]]
        if i == 0:
            rawcolorlist = chs_sum[i]/len(indexes)
            continue
        rawcolorlist = np.vstack((rawcolorlist, chs_sum[i]/len(indexes)))
        
    return rawcolorlist

def dbscan(rawlist, color_num):
    dbscan = DBSCAN(eps=0.5, min_samples=max(min(color_num, 2), 8))
    clusters = dbscan.fit_predict(rawlist.T)
    
    labels_list = list(clusters)
    # print("noise: ", len(find_in_list(labels_list, -1)))

    chs_sum = np.zeros((color_num, 3))
    
    # 将labels归类平均, 不包括-1噪声类
    for i in range(color_num):
        indexes = find_in_list(labels_list, i)
        for j in range(len(indexes)):
            chs_sum[i] += rawlist[:, indexes[j]]
        if i == 0:
            rawcolorlist = chs_sum[i]/len(indexes)
            continue
        rawcolorlist = np.vstack((rawcolorlist, chs_sum[i]/len(indexes)))
        
    return rawcolorlist

rawcolorlist = kmeans(rawlist, 4)
print(rawlist.shape)
print(rawcolorlist)
print(rawcolorlist.shape)
print(rawcolorlist[0])

rawcolorlist = np.array(rawcolorlist)
if len(rawcolorlist.shape)==2:
    w, ch = rawcolorlist.shape
    print("进入reshape")
    rawcolorlist = rawcolorlist.reshape(-1, w, ch).astype(np.float32)

print(rawcolorlist.shape)
# 先全部转HSV
queuecolorlist = cv2.cvtColor(rawcolorlist, cv2.COLOR_RGB2HSV)
print(queuecolorlist)

# dbscan运行结果
# (3, 5184000)
# [[ 27.  92. 150.]
#  [ 27.  93. 151.]
#  [ 22.  96. 143.]
#  [ 16.  94. 133.]]
# (4, 3)
# [ 27.  92. 150.]