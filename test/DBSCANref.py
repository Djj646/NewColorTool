from sklearn.cluster import DBSCAN
from sklearn.datasets import make_blobs
import matplotlib.pyplot as plt

# 生成随机数据
X, y = make_blobs(n_samples=1000, centers=6, random_state=42)
# 调用DBSCAN算法
dbscan = DBSCAN(eps=0.5, min_samples=6)
clusters = dbscan.fit_predict(X)
# 可视化聚类结果
plt.scatter(X[:, 0], X[:, 1], c=clusters, cmap="viridis")
plt.show()