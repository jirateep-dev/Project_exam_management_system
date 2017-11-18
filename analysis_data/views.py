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
from collections import Counter
from django.db.models import Max

this_year = Project.objects.all().aggregate(Max('proj_years'))['proj_years__max']

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
            proj_years = (date_time.year+543)).distinct()
    dataframe = pd.DataFrame(list(advisor))

    to_name = Teacher.objects.values('teacher_name')
    to_levels = Teacher.objects.values('levels_teacher')

    dic_apv = {}
    for i in range(len(advisor)):
        dic_apv[advisor[i]['proj_advisor']] = 0
    
    while True:
        list_teachers, list_levels = [], []
        while (len(list_teachers) != 3):
            teacher = dataframe.iloc[randint(0,len(list(advisor))-1)]['proj_advisor']
            app_tch = approve_teacher(teacher, date_input, period_input)
            if(teacher not in list_teachers) and app_tch:
                list_teachers.append(teacher)
            if app_tch == False and teacher in dic_apv:
                dic_apv[teacher] = 1
            count_dict_apv = Counter(dic_apv.values())
            if count_dict_apv[0] == 3:
                count_chk = 0
                list_teachers = []
                for key, values in dic_apv.items():
                    app_last_group = approve_teacher(key, date_input, period_input)
                    if values == 0 and app_last_group:\
                        count_chk +=1
                if count_chk == 3:
                    list_teachers.append(key)
                else:
                    list_teachers = []
                break
        
        if list_teachers == []:
            break
        for i in range(len(list_teachers)):
            list_levels.append(pd.DataFrame(list(to_levels.filter(teacher_name=list_teachers[i]))).iloc[0]['levels_teacher'])
        if sum(list_levels) > 3 and count_dict_apv[0] == 3:
            list_levels = []
            break
        if sum(list_levels) <= 3 and sum(list_levels) != 0:
            rand_teacher = randint(1,31)
            levels_rand = pd.DataFrame(list(to_levels.filter(id=rand_teacher))).iloc[0]['levels_teacher']
            teacher_get = pd.DataFrame(list(to_name.filter(id=rand_teacher))).iloc[0]['teacher_name']
            app_tch_last = approve_teacher(teacher_get, date_input, period_input)
            if levels_rand == 2 and teacher_get not in list_teachers and app_tch_last :
                list_levels.append(levels_rand)
                list_teachers.append(teacher_get)
                break
        
            
    return list_teachers

def count_proj(major):
    return len(Project.objects.filter(proj_years=this_year, schedule_id_id=None, proj_major=major))

def prepare_render():
    result = []
    dic = {}
    room = Room.objects.values('room_name')
    date = DateExam.objects.values('date_exam').distinct()
    date_all = DateExam.objects.all()
    pc_result = [{'bi':count_proj('Business Intelligence'), 'ds':count_proj('Data Science'), 'es':count_proj('Embedded Systems'), \
                'mu':count_proj('Multimedia'), 'nw':count_proj('Network and Communication'), 'se':count_proj('Software Development')}]
    date_result = [date[i]['date_exam'] for i in range(len(date))]
    
    for i in date_result:
        period_zero = [0 for i in range(len(room))]
        period_one = [0 for i in range(len(room))]
        tp_date = DateExam.objects.values('time_period').filter(date_exam=i)
        rm_date = DateExam.objects.values('room_id_id').filter(date_exam=i)
        dic_keep = {}

        for j in range(len(tp_date)):
            dic_keep[j] = (rm_date[j]['room_id_id']-1, tp_date[j]['time_period'])

        for j in range(len(dic_keep)):
            if dic_keep[j][1] == 0:
                period_zero[dic_keep[j][0]] = 1 
            else:
                period_one[dic_keep[j][0]] = 1
        dic[i] = (period_zero, period_one)
    result.append(pc_result)
    # result.append(date_result)
    result.append(dic)

    return result

def manage_room(request):
    room_selected = request.POST.get('room_selected',None)
    major_selected = request.POST.get('major_selected',None)
    period_selected = request.POST.get('period_selected',None)
    date_selected = request.POST.get('date_selected',None)

    date_time = datetime.datetime.strptime(date_selected, "%d/%m/%Y")
    list_proj_id = []
    real_teacher = []
    create_schedule = False
    fail_teacher = False
    list_teachers = manageTeacher(major_selected, date_selected, period_selected)

    # check date in database and insert
    dataframe_date = pd.DataFrame(list(DateExam.objects.values('date_exam')))
    dataframe_period = pd.DataFrame(list(DateExam.objects.values('time_period')))
    dataframe_room = pd.DataFrame(list(DateExam.objects.values('room_id_id')))

    id_dateexam = int((date_selected+period_selected+room_selected).replace('/',''))

    if not DateExam.objects.filter(id=id_dateexam).exists():
        create_schedule = True
        date_insert = DateExam(id=id_dateexam, date_exam=date_selected, time_period=period_selected, room_id_id=room_selected)
        date_insert.save()

    # /////////////////////////////////////
    if list_teachers == []:
        fail_teacher = True
    # check proj of teacher
    mobj_name = Major.objects.values('major_name')

    if not fail_teacher:
        for i in range(3):
            proj_of_teacher = pd.DataFrame(list(Project.objects.values('id').filter(proj_years=date_time.year+543, \
                            proj_advisor=list_teachers[i], schedule_id_id=None, \
                            proj_major=mobj_name.get(id=major_selected)['major_name'])))
            if not proj_of_teacher.empty:
                rand_index = randint(0,len(proj_of_teacher)-1)
                if proj_of_teacher.iloc[rand_index]['id'] not in list_proj_id:
                    list_proj_id.append(proj_of_teacher.iloc[rand_index]['id'])
        
        proj_major_selected = pd.DataFrame(list(Project.objects.values('id').filter(proj_years=date_time.year+543, schedule_id_id=None,\
                proj_major=mobj_name.get(id=major_selected)['major_name'])))

    count_loop = 1
    if create_schedule and not fail_teacher and list_proj_id != []:
        while True:
            check_status = 0
            for i in list_teachers:
                if Teacher.objects.filter(teacher_name=i, proj_group_exam__lte=count_loop).exists():
                    check_status += 1
            if not Teacher.objects.filter(proj_group_exam=count_loop).exists() and check_status == len(list_teachers):
                for i in range(len(list_teachers)):
                    Teacher.objects.filter(teacher_name=list_teachers[i]).update(proj_group_exam=count_loop)
                break
            count_loop += 1
    
    if not fail_teacher:
        for i in range(len(proj_major_selected)):
            if proj_major_selected.iloc[i]['id'] not in list_proj_id and len(list_proj_id) < 5:
                list_proj_id.append(proj_major_selected.iloc[i]['id'])
    


    if create_schedule and not fail_teacher :
        for i in range(len(list_proj_id)):
            time_id_condition = 1 if(int(period_selected) == 0) else 6
            if not ScheduleRoom.objects.filter(date_id_id=id_dateexam, time_id_id=i+time_id_condition, room_id_id=int(room_selected)).exists():
                schedule = ScheduleRoom(teacher_group=count_loop, room_id_id=int(room_selected), \
                            date_id_id=id_dateexam, proj_id=list_proj_id[i], time_id_id=i+time_id_condition)
                schedule.save()
                for name in list_teachers:
                    teacher_r = Teacher.objects.get(teacher_name=name)
                    teacher_r.schedule_teacher.add(schedule)
                    teacher_r.save()
                Project.objects.filter(id=list_proj_id[i]).update(schedule_id_id=schedule.id)
    else:
        DateExam.objects.filter(id=id_dateexam).delete()
    pre = prepare_render()
    return render(request,"manage.html",{'rooms': Room.objects.all(), 'majors':Major.objects.all(), 'proj_count': pre[0],
                    'room_period':pre[1]})

def table_room(request):
    teacher_groups = []
    result_manage = []
    # query teacher_group

    sched_r = ScheduleRoom.objects.all()
    list_group = list(sched_r.values('teacher_group').distinct())
    count_teacher, count_len = 0, 0
    for i in list_group:
        dtset_id_sch = sched_r.values('id').filter(teacher_group=i['teacher_group'])
        for j in range(4):
            id_sch = dtset_id_sch[0]['id']
            tch_obj = list(sched_r.get(id=id_sch).teacher_set.all())[j]
            teacher_groups.append({'proj_group_exam': i['teacher_group'], \
                                'teacher_name': tch_obj.teacher_name, \
                                'levels_teacher': tch_obj.levels_teacher})
    

    # //////////////////////////////////////

    # query data to html
    schedule_all = pd.read_sql_query(str(ScheduleRoom.objects.all().query), connection)
    for i in range(len(schedule_all)):
        proj_objs = Project.objects.get(schedule_id_id=schedule_all.iloc[i]['id'])
        room_result = Room.objects.values('room_name').get(id=schedule_all.iloc[i]['room_id_id'])['room_name']
        date_result = DateExam.objects.values('date_exam').get(id=schedule_all.iloc[i]['date_id_id'])['date_exam']
        proj_result = proj_objs.proj_name_th
        time_result = TimeExam.objects.values('time_exam').get(id=schedule_all.iloc[i]['time_id_id'])['time_exam']
        major_result = Major.objects.values('major_name').get(major_name=proj_objs.proj_major)['major_name']
 
        result_manage.append({'teacher_group': schedule_all.iloc[i]['teacher_group'], 'room_name': room_result ,\
                    'date_exam': date_result, 'proj_name_th': proj_result, 'major_name':major_result, 'time_exam': time_result})
    
    return render(request,"result_room.html",{'list_result_teacher': teacher_groups, 'ScheduleRoom': result_manage})

def admin_required(login_url=None):
    return user_passes_test(lambda u: u.is_superuser, login_url=login_url)

@login_required
@admin_required(login_url="login/")
def manage(request):
    pre = prepare_render()
    try:
        reset_selected = int(request.POST.get('reset_gen',None))
        if reset_selected:
            Project.objects.filter(proj_years=this_year).update(schedule_id_id=None)
            DateExam.objects.all().delete()
            Teacher.objects.all().order_by('proj_group_exam').update(proj_group_exam=0)
            Teacher.save()
        return render(request,"manage.html",{'rooms': Room.objects.all(), 'majors':Major.objects.all(), 'proj_count': pre[0],
                    'room_period':pre[1]})
    except Exception as error:
        print(error)
        return render(request,"manage.html",{'rooms': Room.objects.all(), 'majors':Major.objects.all(), 'proj_count': pre[0],
                    'room_period':pre[1]})