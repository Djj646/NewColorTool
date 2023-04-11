#产生实验数据
import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs
X, y_true = make_blobs(n_samples=1000, centers=4, n_features=3,
                       cluster_std=0.7, random_state=0, )


from sklearn.mixture import GaussianMixture as GMM
from sklearn.cluster import DBSCAN
# gmm = GMM(n_components=4)
gmm = DBSCAN(eps=0.8, min_samples=4)
clusters = gmm.fit_predict(X)

fig, ax= plt.subplots()
ax = plt.axes(projection='3d')
ax.scatter3D(X[:,0], X[:,1], X[:,2], c = clusters)
plt.show()

# 降维可视化
from sklearn.manifold import TSNE
ts = TSNE(n_components = 2, init='pca')
y = ts.fit_transform(X)
print(y.shape)
fig, ax = plt.subplots()
ax.scatter(y[:,0], y[:, 1], c = clusters)
plt.show()
