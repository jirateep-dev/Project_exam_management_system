# import numpy as np
# import pandas as pd
# from sklearn.cluster import KMeans
# from sklearn.decomposition import PCA
# import matplotlib.pyplot as plt
# import io
# from django.conf import settings
# from django.db import connection
# from django.core.files.images import ImageFile

# class CalKMean:
#         def __init__(self):
#                 data = pd.read_sql_query(settings.JOIN_MEAN_SCORE,connection)
#                 reduced_data = PCA(n_components=2).fit_transform(data)
#                 kmeans = KMeans(init='k-means++', n_clusters=4, n_init=10).fit(reduced_data)
#                 labels = kmeans.labels_
#                 center = kmeans.cluster_centers_
#                 z = kmeans_pca.predict(reduced_data)
        
#         def plot_kmean(self):
               
for i in range(len(labels)):
    labels[i] = 3 if labels[i] == 0 else 0 if labels[i] == 3 else labels[i]
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from django.conf import settings
from django.db import connection
from database_management import callsql

data_mean = pd.read_sql_query(callsql.JOIN_MEAN_SCORE,connection)
data_levels = pd.read_sql_query(callsql.LEVELS_TEACHER,connection)

kmeans = KMeans(init='k-means++', n_clusters=4, n_init=10, random_state=2).fit(data_mean)
labels = kmeans.labels_
center = kmeans.cluster_centers_
z = kmeans.predict(data_mean)
x = data_mean.loc[:, "RESULT_score_proj"]
y = data_mean.loc[:, "quality_proj"]

 
plot, plt_areas = plt.subplots(1, 2, sharex='col', sharey='row')

plt_areas[0].set_xlabel('AVG SCORE')
plt_areas[0].set_ylabel('Quality')
plt_areas[0].set_title('K Mean not PCA')
plt_areas[0].scatter(x,y, c=labels)
plt_areas[0].scatter(center[:, 1], center[:, 0],
            marker='x', s=169, linewidths=3,
            color='b', zorder=10)

reduced_data = PCA().fit_transform(data_mean)
kmeans_pca = KMeans(init='k-means++', n_clusters=4, n_init=10, random_state=2).fit(reduced_data)
zz = kmeans_pca.predict(reduced_data)
plt_areas[1].set_title('K-means (PCA-reduced data)')
plt_areas[1].set_xlabel('AVG SCORE')
plt_areas[1].set_ylabel('Quality')
plt_areas[1].scatter(x, y,c=zz)
plt_areas[1].scatter(center[:, 1], center[:, 0],
            marker='x', s=169, linewidths=3,
            color='b', zorder=10)
plot.show()


