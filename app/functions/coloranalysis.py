from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture as GMM
from sklearn.cluster import DBSCAN
import numpy as np

#--------------------------
# 分析函数返回颜色列表：(n, 3)
#--------------------------

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
    kmeans = KMeans(n_clusters=color_num, max_iter=1000, verbose=1, algorithm='auto')
    kmeans.fit(rawlist.T)
    
    rawcolorlist = kmeans.cluster_centers_
    
    return np.round(rawcolorlist)

def dbscan(rawlist, color_num):
    dbscan = DBSCAN(eps=0.5, min_samples=color_num)
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
        
    return np.round(rawcolorlist)
    

def gaussi(rawlist, color_num):
    gmm = GMM(n_components=color_num, max_iter=1000)
    clusters = gmm.fit_predict(rawlist.T)
    labels_list = list(clusters)

    chs_sum = np.zeros((color_num, 3))
    
    # 将labels归类平均
    for i in range(color_num):
        indexes = find_in_list(labels_list, i)
        for j in range(len(indexes)):
            chs_sum[i] += rawlist[:, indexes[j]]
        if i == 0:
            rawcolorlist = chs_sum[i]/len(indexes)
            continue
        rawcolorlist = np.vstack((rawcolorlist, chs_sum[i]/len(indexes)))
        
    return np.round(rawcolorlist)