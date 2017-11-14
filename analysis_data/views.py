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
# def manageTeacher(major_id, date_input):
#     # clustering teacher and set levels to schema Teacher
#     data = pd.read_sql_query(callsql.LEVELS_TEACHER,connection)
#     data_kmeans = calkmean()
#     for i in range(len(data)):
#         data.set_value(i,'levels_teacher',data_kmeans[i])
#         Teacher.objects.filter(id = data.loc[i]['id']).update(levels_teacher = data.loc[i]['levels_teacher'])

#     # //////////////////////////////////////////////////////////////////
#     # calculate levels of group exam proj
#     # //////////////////////////////////////////////////////////////////
def manageTeacher(major_id, date_input):
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
    list_proj_id, result_manage, teacher_groups = [], [], []
    dict_date = {}
    create_schedule = False
    list_teachers = manageTeacher(major_selected, date_selected)

    # check date in database and insert
    dataframe_date = pd.DataFrame(list(DateExam.objects.values('date_exam')))
    dataframe_period = pd.DataFrame(list(DateExam.objects.values('time_period')))
    dataframe_room = pd.DataFrame(list(DateExam.objects.values('room_id_id')))
    for i in range(len(dataframe_date)):
        dict_date[dataframe_date.iloc[i]['date_exam']] = (dataframe_period.iloc[i]['time_period'], dataframe_room.iloc[i]['room_id_id'])
    print('wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww')
    print(dict_date)
    if not ((date_selected in dict_date) and (int(period_selected) == dict_date[dataframe_date.iloc[i]['date_exam']][0])\
        and (room_selected == dict_date[dataframe_date.iloc[i]['date_exam']][1])):
        create_schedule = True
        print('wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww')
        print(date_selected+" "+period_selected)
        date_insert = DateExam(date_exam=date_selected, time_period=period_selected, room_id_id=room_selected)
        date_insert.save()
    # /////////////////////////////////////

    # update teacher_group_exam
    count_loop = 1
    if create_schedule:
        while True:
            check_status = 0
            for i in list_teachers:
                if Teacher.objects.filter(teacher_name=i, proj_group_exam__lte=count_loop).exists():
                    check_status += 1
            if not Teacher.objects.filter(proj_group_exam=count_loop).exists() and check_status == len(list_teachers):
                for i in range(len(list_teachers)):
                    Teacher.objects.filter(teacher_name=list_teachers[i]).update(proj_group_exam=count_loop)
                break
            else:
                list_teachers = manageTeacher(major_selected, date_selected)
            count_loop += 1

    # count_loop = 1
    # while True:
    #     check_status = 0
    #     for i in list_teachers:
    #         if not Teacher.objects.filter(teacher_name=i, proj_group_exam=count_loop).exists():
    #             check_status += 1
    #     if not Teacher.objects.filter(proj_group_exam=count_loop).exists() and check_status == len(list_teachers):
    #         for i in range(len(list_teachers)):
    #             # Teacher.objects.filter(teacher_name=list_teachers[i]).update(proj_group_exam=count_loop)
    #             print(list_teachers[i])
    #         break
    #     else:
    #         print('eieieieieeieiieieieieieieiie')
    #         list_teachers = manageTeacher('1', '14/11/2017')
    #     count_loop += 1
    print(list_teachers)
    # /////////////////////////////////////

    # check proj of teacher
    for i in range(3):
        proj_of_teacher = pd.DataFrame(list(Project.objects.values('id').filter(proj_years=date_time.year+543, proj_advisor=list_teachers[i])))
        for j in range(len(proj_of_teacher)):
            if proj_of_teacher.iloc[j]['id'] not in list_proj_id:
                list_proj_id.append(proj_of_teacher.iloc[j]['id'])
    print(list_proj_id)
    # /////////////////////////////////////

    # create data of table schedule
    

    proj_in_schedule = ScheduleRoom.objects.values('proj_id_id')
    list_temp = list_proj_id
    if proj_in_schedule.exists():
        for i in list_temp:
            for j in range(len(proj_in_schedule)):
                if i == pd.DataFrame(list(proj_in_schedule)).iloc[j]['proj_id_id'] and i in list_proj_id:
                    list_proj_id.remove(i)
    loop_schedule = 5 if len(list_proj_id) > 4 else len(list_proj_id)
    if create_schedule:
        print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
        print(list_proj_id)
        for i in range(loop_schedule):
            time_id_condition = 1 if(int(period_selected) == 0) else 6
            if not ScheduleRoom.objects.filter(time_id_id=i+time_id_condition, room_id_id=int(room_selected)).exists():
                schedule = ScheduleRoom(teacher_group=count_loop, room_id_id=int(room_selected), \
                            date_id_id=DateExam.objects.values('id').filter(date_exam=date_selected)[0]['id'], \
                            proj_id_id=list_proj_id[i], time_id_id=i+time_id_condition)
                schedule.save()
    # //////////////////////////////////////

    # query teacher_group
    for i in range(len(Teacher.objects.filter(~Q(proj_group_exam=0)))):
        teacher_groups.append({'proj_group_exam':pd.DataFrame(list(Teacher.objects.values('proj_group_exam').filter(~Q(proj_group_exam=0)))).iloc[i]['proj_group_exam'], \
                            'teacher_name': pd.DataFrame(list(Teacher.objects.values('teacher_name').filter(~Q(proj_group_exam=0)))).iloc[i]['teacher_name']})
    # //////////////////////////////////////
    print('/////////////+++++++++++++++++++++++++++++++++++++++++////////////////////')
    print(teacher_groups)
    # query data to html
    schedule_all = pd.read_sql_query(str(ScheduleRoom.objects.all().query), connection)
    print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    print(schedule_all)
    for i in range(len(schedule_all)):
        room_result = pd.DataFrame(list(Room.objects.values('room_name').filter(id=schedule_all.iloc[i]['room_id_id']))).iloc[0]['room_name']
        date_result = pd.DataFrame(list(DateExam.objects.values('date_exam').filter(id=schedule_all.iloc[i]['date_id_id']))).iloc[0]['date_exam']
        proj_result = pd.DataFrame(list(Project.objects.values('proj_name_th').filter(id=schedule_all.iloc[i]['proj_id_id']))).iloc[0]['proj_name_th']
        time_result = pd.DataFrame(list(TimeExam.objects.values('time_exam').filter(id=schedule_all.iloc[i]['time_id_id']))).iloc[0]['time_exam']

        result_manage.append({'teacher_group': schedule_all.iloc[i]['teacher_group'], 'room_name': room_result ,'date_exam': date_result, 'proj_name_th': proj_result, 'time_exam': time_result})
    
    print(result_manage)
    return render(request,"result_room.html",{'list_result_teacher': teacher_groups, \
                    'ScheduleRoom': result_manage})

def admin_required(login_url=None):
    return user_passes_test(lambda u: u.is_superuser, login_url=login_url)

@login_required
@admin_required(login_url="login/")
def manage(request):
    return render(request,"manage.html",{'rooms': Room.objects.all(), 'majors':Major.objects.all()})