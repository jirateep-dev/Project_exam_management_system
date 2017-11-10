from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from django.db import connection
from database_management import callsql, models


def calkmean():
    data = pd.read_sql_query(callsql.JOIN_MEAN_SCORE,connection)
    reduced_data = PCA().fit_transform(data)
    kmeans = KMeans(init='k-means++', n_clusters=4, n_init=10, random_state=2).fit(reduced_data)
    result_kmean = kmeans.predict(reduced_data)
    for i in range(len(result_kmean)):
        result_kmean[i] = 1 if result_kmean[i] == 0 else 0 if result_kmean[i] == 1 else result_kmean[i]
    # result type array([x,x,x,x,...]) link to Teacher_id of join_data_score_proj
    return result_kmean

def clusteringTeacher():
    data = pd.read_sql_query(callsql.LEVELS_TEACHER,connection)
    data_kmeans = calkmean()
    for i in range(len(data)):
        data.set_value(i,'levels_teacher',data_kmeans[i])
        models.Teacher.objects.filter(id = data.loc[i]['id']).update(levels_teacher = data.loc[i]['levels_teacher'])
    return

@login_required(login_url="login/")
def home(request):
    return render(request,"kmean.html")