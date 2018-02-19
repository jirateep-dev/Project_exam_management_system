from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse,  HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from .forms import *
import csv
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
from collections import Counter
from django.db.models import Max
import logging

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

def approve_teacher(tch_name, date_selected, period_selected):
    approve_tch = False

    if not Teacher.objects.get(teacher_name=tch_name).schedule_teacher.all().exists():
        approve_tch = True
    else:
        tid_sch = Teacher.objects.get(teacher_name=tch_name).schedule_teacher.all()
        sche_r = ScheduleRoom.objects.all()
        chk_schedule = 0;
        for obj in tid_sch:
            date_id_check = sche_r.values('date_id_id').get(id=obj.id)['date_id_id']
            date_exam_chk = DateExam.objects.values('date_exam').get(id=date_id_check)['date_exam']
            time_period_chk = DateExam.objects.values('time_period').get(id=date_id_check)['time_period']
            if not (date_exam_chk == date_selected and time_period_chk == int(period_selected)):
                chk_schedule += 1
            if chk_schedule == len(tid_sch):
                approve_tch = True

    return approve_tch

def manageTeacher(major_id, date_input, period_input):
    # clustering teacher and set levels to schema Teacher
    data = pd.read_sql_query(callsql.LEVELS_TEACHER,connection)
    data_kmeans = calkmean()
    for i in range(len(data)):
        data.set_value(i,'levels_teacher',data_kmeans[i])
        Teacher.objects.filter(id = data.loc[i]['id']).update(levels_teacher = data.loc[i]['levels_teacher'])

    # //////////////////////////////////////////////////////////////////
    # calculate levels of group exam proj
    date_time = datetime.datetime.strptime(date_input, "%d/%m/%Y")
    get_major_name = Major.objects.get(id = int(major_id))
    advisor = Project.objects.values('proj_advisor').filter(proj_major = get_major_name.major_name,\
            proj_years = (this_year), schedule_id_id=None).distinct()
    dataframe = pd.DataFrame(list(advisor))

    advisor_m = Project.objects.values('proj_advisor').filter(proj_major = get_major_name.major_name,\
            proj_years = (this_year)).distinct()

    kind_teacher = Teacher.objects.filter(levels_teacher=2)
    normal_teacher = Teacher.objects.filter(levels_teacher=1)

    to_name = Teacher.objects.values('teacher_name')
    to_levels = Teacher.objects.values('levels_teacher')

    dic_apv = {}
    for i in range(len(advisor)):
        dic_apv[advisor[i]['proj_advisor']] = 0

    dic_kind = {}
    for i in range(len(kind_teacher)):
        dic_kind[kind_teacher.values('teacher_name')[i]['teacher_name']] = 0
    
    if len(advisor) > 2:
        while True:
            list_teachers, list_levels = [], []
            while True:
                teacher = dataframe.iloc[randint(0,len(list(advisor))-1)]['proj_advisor']
                app_tch = approve_teacher(teacher, date_input, period_input)
                if(teacher not in list_teachers) and app_tch:
                    list_teachers.append(teacher)
                if app_tch == False and teacher in dic_apv:
                    dic_apv[teacher] = 1
                if app_tch == False and teacher in dic_kind:
                    dic_kind[teacher] = 1
                count_dict_apv = Counter(dic_apv.values())
                count_dict_kind = Counter(dic_kind.values())
                if count_dict_kind[0] == 0:
                    list_teachers = []
                    break
                if count_dict_apv[0] == 3:
                    list_teachers = []
                    for key, values in dic_apv.items():
                        app_last_group = approve_teacher(key, date_input, period_input)
                        if values == 0 and app_last_group:
                            list_teachers.append(key)
                    if len(list_teachers) == 3:
                        break
                    else:
                        list_teachers = []
                    break
                if count_dict_apv[0] < 3:
                    list_teachers = []
                    for key, values in dic_apv.items():
                        app_group = approve_teacher(key, date_input, period_input)
                        if values == 0 and app_group:
                            list_teachers.append(key)
                    for i in range(len(normal_teacher)):
                        teacher = pd.DataFrame(list(to_name.filter(levels_teacher=1))).iloc[i]['teacher_name']
                        app_t = approve_teacher(teacher, date_input, period_input)
                        if app_t and len(list_teachers) < 3 and teacher not in list_teachers:
                            list_teachers.append(teacher)
                if len(list_teachers) == 3:
                    break
            if list_teachers == []:
                break
            for i in range(len(list_teachers)):
                list_levels.append(pd.DataFrame(list(to_levels.filter(teacher_name=list_teachers[i]))).iloc[0]['levels_teacher'])
            
            if (sum(list_levels) == 0 and count_dict_apv[0] == 3):
                list_teachers = []
                break
            if (sum(list_levels) > 3):
                for i in range(len(normal_teacher)):
                    teacher_get = normal_teacher.values('teacher_name')[i]['teacher_name']
                    app_t = approve_teacher(teacher_get, date_input, period_input)
                    if app_t and teacher_get not in list_teachers:
                        list_teachers.append(teacher_get)
                        break
                if len(list_teachers) == 4:
                    break
            if sum(list_levels) <= 3 and sum(list_levels) != 0:
                rand_teacher = randint(0,len(kind_teacher)-1)
                teacher_get = kind_teacher.values('teacher_name')[rand_teacher]['teacher_name']
                levels_rand = kind_teacher.values('levels_teacher')[0]['levels_teacher']
                app_tch_last = approve_teacher(teacher_get, date_input, period_input)
                if app_tch_last == False and teacher_get in dic_kind:
                    dic_kind[teacher_get] = 1
                count_dict_kind = Counter(dic_kind.values())
                if count_dict_kind[0] == 0 or (count_dict_kind[0] == 1 and teacher_get in list_teachers):
                    list_teachers = []
                    break
                if teacher_get not in list_teachers and app_tch_last :
                    list_levels.append(levels_rand)
                    list_teachers.append(teacher_get)
                    break
    else:
        list_teachers = []
        for i in range(len(advisor)):
            teacher = advisor[i]['proj_advisor']
            app_t = approve_teacher(teacher, date_input, period_input)
            if app_t:
                list_teachers.append(teacher)
        for i in range(len(normal_teacher)):
            teacher_get = normal_teacher.values('teacher_name')[i]['teacher_name']
            app_t = approve_teacher(teacher_get, date_input, period_input)
            if app_t and teacher_get not in list_teachers:
                list_teachers.append(teacher_get)
            if len(list_teachers) == 4:
                break

    return list_teachers