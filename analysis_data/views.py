from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
import datetime
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from django.db import connection
from database_management import callsql
from database_management.models import *
from django.db.models import Q
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
def manageTeacher(major_id, date_input):
    # clustering teacher and set levels to schema Teacher
    data = pd.read_sql_query(callsql.LEVELS_TEACHER,connection)
    data_kmeans = calkmean()
    for i in range(len(data)):
        data.set_value(i,'levels_teacher',data_kmeans[i])
        Teacher.objects.filter(id = data.loc[i]['id']).update(levels_teacher = data.loc[i]['levels_teacher'])

    # //////////////////////////////////////////////////////////////////
    # calculate levels of group exam proj
    # //////////////////////////////////////////////////////////////////
    date_time = datetime.datetime.strptime(date_input, "%d/%m/%Y")
    get_major_name = Major.objects.get(id = int(major_id))
    advisor = Project.objects.values('proj_advisor').filter(proj_major = get_major_name.major_name,\
            proj_years = (date_time.year+543)).distinct()
    dataframe = pd.DataFrame(list(advisor))
    while True:
        list_teachers, list_levels = [], []
        while (len(list_teachers) != 3):
            teacher = dataframe.iloc[randint(0,len(list(advisor))-1)]['proj_advisor']
            if(teacher not in list_teachers):
                list_teachers.append(teacher)
        for i in range(len(list_teachers)):
            list_levels.append(pd.DataFrame(list(Teacher.objects.values('levels_teacher').filter(teacher_name=list_teachers[i]))).iloc[0]['levels_teacher'])
        if sum(list_levels) > 2 and sum(list_levels) < 5:
            rand_teacher = randint(1,31)
            list_levels.append(pd.DataFrame(list(Teacher.objects.values('levels_teacher').filter(id=rand_teacher))).iloc[0]['levels_teacher'])
            list_teachers.append(pd.DataFrame(list(Teacher.objects.values('teacher_name').filter(id=rand_teacher))).iloc[0]['teacher_name'])
            break
        if sum(list_levels) <= 2 and list_levels.count(1) >= 1:
            rand_teacher = randint(1,31)
            levels_rand = pd.DataFrame(list(Teacher.objects.values('levels_teacher').filter(id=rand_teacher))).iloc[0]['levels_teacher']
            if levels_rand == 2:
                list_levels.append(levels_rand)
                list_teachers.append(pd.DataFrame(list(Teacher.objects.values('teacher_name').filter(id=rand_teacher))).iloc[0]['teacher_name'])
                break
    
    return list_teachers


def manage_room(request):
    room_selected = request.POST.get('room_selected',None)
    major_selected = request.POST.get('major_selected',None)
    period_selected = request.POST.get('period_selected',None)
    date_selected = request.POST.get('date_selected',None)

    date_time = datetime.datetime.strptime(date_selected, "%d/%m/%Y")
    list_proj_id, list_proj_name = [], []
    list_teachers = manageTeacher(major_selected, date_selected)

    list_date = []
    
    dataframe_date = pd.DataFrame(list(DateExam.objects.values('date_exam')))
    for i in range(len(dataframe_date)):
        list_date.append(dataframe_date[i]['date_exam'])
    
    if date_selected not in list_date:
        date_insert = DateExam(date_exam=date_selected)
        date_insert.save()

    for i in range(3):
        proj_of_teacher = pd.DataFrame(list(Project.objects.values('id').filter(proj_years=date_time.year+543, proj_advisor=list_teachers[i])))
        for j in range(len(proj_of_teacher)):
            if proj_of_teacher.iloc[j]['id'] not in list_proj_id:
                list_proj_id.append(proj_of_teacher.iloc[j]['id'])
    
    count_loop = 1
    while True:
        if not Teacher.objects.filter(proj_group_exam=count_loop).exists():
            for i in range(list_teachers):
                teacher_group.filter(teacher_name=list_teachers[i]).update(proj_group_exam=count_loop)
            break
        count_loop += 1
    
    for i in range(5):
        list_proj_name.append(pd.DataFrame(list(Project.objects.values('proj_name_th').filter(id=list_proj_id[i]))).iloc[0]['proj_name_th'])
        if(period_selected == 0):
            schedule = ScheduleRoom(teacher_group=count_loop, room_id_id=int(room_selected), \
                        date_id_id=DateExam.objects.values('id').filter(date_exam=date_selected)[0]['id'], \
                        proj_id_id=list_proj_id[i], time_id_id=i+1)
            schedule.save()
        if(period_selected == 0):
            schedule = ScheduleRoom(teacher_group=count_loop, room_id_id=int(room_selected), \
                        date_id_id=DateExam.objects.values('id').filter(date_exam=date_selected)[0]['id'], \
                        proj_id_id=list_proj_id[i], time_id_id=i+6)
            schedule.save()

    print(list_proj_name)
    if 'room_selected' in request.POST and 'major_selected' in request.POST and 'period_selected' in request.POST:
        message_1 = 'Room : %r' % room_selected
        message_2 = 'Major : %r' % major_selected
        message_3 = 'Period : %r' % period_selected
        message_4 = 'Date : %r' % date_selected
        boo = True
    else:
        message = 'You submitted an empty form.'
        boo = False
    # return HttpResponse(message_1+"<br>"+message_2+"<br>"+message_3+"<br>"+message_4) if boo == True else HttpResponse(message)
    return render(request,"result_room.html",{'list_result': manageTeacher(major_selected, date_selected), \
                    'time_exam': TimeExam.objects.all(), 'list_proj_name': list_proj_name})

def admin_required(login_url=None):
    return user_passes_test(lambda u: u.is_superuser, login_url=login_url)

@login_required
@admin_required(login_url="login/")
def manage(request):
    return render(request,"manage.html",{'rooms': Room.objects.all(), 'majors':Major.objects.all()})