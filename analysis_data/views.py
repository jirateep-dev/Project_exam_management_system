from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
import datetime
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from django.db import connection
from database_management import callsql, models
from random import randint

def change_positionlevels(number1, number2, kmean):
    for i in range(len(kmean)):
        kmean[i] = number1 if kmean[i] == number2 else number2 if kmean[i] == number1 else kmean[i]
    return kmean

def calkmean():
    data = pd.read_sql_query(callsql.JOIN_MEAN_SCORE,connection)
    reduced_data = PCA().fit_transform(data)
    kmeans = KMeans(init='k-means++', n_clusters=3, n_init=10, random_state=2).fit(reduced_data)
    result_kmean = kmeans.predict(reduced_data)
    result_kmean = change_positionlevels(1,2,result_kmean)
    result_kmean = change_positionlevels(1,0,result_kmean)
    # result type array([x,x,x,x,...]) link to Teacher_id of join_data_score_proj
    return result_kmean


# manageTeacher('1', '13/11/2017')
# def manageTeacher(major_id, date_input):
#     # clustering teacher and set levels to schema Teacher
#     data = pd.read_sql_query(callsql.LEVELS_TEACHER,connection)
#     data_kmeans = calkmean()
#     for i in range(len(data)):
#         data.set_value(i,'levels_teacher',data_kmeans[i])
#         models.Teacher.objects.filter(id = data.loc[i]['id']).update(levels_teacher = data.loc[i]['levels_teacher'])

#     # //////////////////////////////////////////////////////////////////
#     # calculate levels of group exam proj
#     # //////////////////////////////////////////////////////////////////
def manageTeacher(major_id, date_input):
    date_time = datetime.datetime.strptime(date_input, "%d/%m/%Y")
    get_major_name = models.Major.objects.get(id = int(major_id))
    advisor = models.Project.objects.values('proj_advisor').filter(proj_major = get_major_name.major_name,\
            proj_years = (date_time.year+543)).distinct()
    dataframe = pd.DataFrame(list(advisor))
    while True:
        list_teachers, list_levels = [], []
        while (len(list_teachers) != 3):
            teacher = dataframe.iloc[randint(0,4)]['proj_advisor']
            if(teacher not in list_teachers):
                list_teachers.append(teacher)
        for i in range(len(list_teachers)):
            list_levels.append(pd.DataFrame(list(models.Teacher.objects.values('levels_teacher').filter(teacher_name=list_teachers[i]))).iloc[0]['levels_teacher'])
        if sum(list_levels) > 2 and sum(list_levels) < 5:
            rand_teacher = randint(0,31)
            list_levels.append(pd.DataFrame(list(models.Teacher.objects.values('levels_teacher').filter(id=rand_teacher))).iloc[0]['levels_teacher'])
            list_teachers.append(pd.DataFrame(list(models.Teacher.objects.values('teacher_name').filter(id=rand_teacher))).iloc[0]['teacher_name'])
            break
    return list_levels+list_teachers


def manage_room(request):
    room_selected = request.POST.get('room_selected',None)
    major_selected = request.POST.get('major_selected',None)
    period_selected = request.POST.get('period_selected',None)
    date_selected = request.POST.get('date_selected',None)
    if 'room_selected' in request.POST and 'major_selected' in request.POST and 'period_selected' in request.POST:
        message_1 = 'Room : %r' % room_selected
        message_2 = 'Major : %r' % major_selected
        message_3 = 'Period : %r' % period_selected
        message_4 = 'Date : %r' % date_selected
        boo = True
    else:
        message = 'You submitted an empty form.'
        boo = False


    return HttpResponse(message_1+"<br>"+message_2+"<br>"+message_3+"<br>"+message_4) if boo == True else HttpResponse(message)

def admin_required(login_url=None):
    return user_passes_test(lambda u: u.is_superuser, login_url=login_url)

@login_required
@admin_required(login_url="login/")
def manage(request):
    return render(request,"manage.html",{'rooms': models.Room.objects.all(), 'majors':models.Major.objects.all()})