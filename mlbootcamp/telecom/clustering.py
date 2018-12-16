import pandas as pd
from sklearn.cluster import KMeans

kpi_chnn = pd.read_pickle('kpi_chnn_kmean.pk')

seed = 83
pd.np.random.seed(seed)
kmeans = KMeans(n_clusters=10, random_state=83)
kmeans.fit(kpi_chnn)

cell_clusters = pd.DataFrame(kmeans.labels_)
cell_clusters.index = kpi_chnn.index
cell_clusters.columns = ['CELL_CLST']

cell_clusters.to_pickle('kpi_chnn_clst.pk')