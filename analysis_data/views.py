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

this_year = Project.objects.all().aggregate(Max('proj_years'))['proj_years__max']

def export_csv(request):

    tchs = Teacher.objects.all()
    sc = ScheduleRoom.objects.all()
    lis_ex = [["date_id", "room_id", "time_id", "project_id", "teacher_group", "teacher_id"]]

    for objs in sc:
        lis_tch = []
        for tch in tchs:
            rel_tch = tch.schedule_teacher.all()
            for i in rel_tch:
                if objs.id == i.id:
                    lis_tch.append(tch.id)
        lis_sub = []
        lis_sub.append(str(objs.date_id_id))
        lis_sub.append(str(objs.room_id_id))
        lis_sub.append(str(objs.time_id_id))
        lis_sub.append(str(objs.proj_id))
        lis_sub.append(str(objs.teacher_group))
        lis_sub.append(str(lis_tch[0])+"/"+str(lis_tch[1])+"/"+str(lis_tch[2])+"/"+str(lis_tch[3]))
        lis_ex.append(lis_sub)

    with open('schedule_room.csv','w', newline='') as new_file:
        csv_writer = csv.writer(new_file, delimiter=',')
        for line in lis_ex:
            csv_writer.writerow(line)
    # render(request,"manage.html")
    return HttpResponseRedirect(reverse("manage"))

def upload_csv(request):
    # if not GET, then proceed
    try:
        csv_file = request.FILES["csv_file"]
        if not csv_file.name.endswith('.csv'):
            messages.error(request,'File is not CSV type')
            return HttpResponseRedirect(reverse("manage"))
        #if file is too large, return
        if csv_file.multiple_chunks():
            messages.error(request,"Uploaded file is too big (%.2f MB)." % (csv_file.size/(1000*1000),))
            return HttpResponseRedirect(reverse("manage"))
 
        file_data = csv_file.read().decode("utf-8")    
 
        lines = file_data.splitlines()
        #loop over the lines and save them in db. If error , store as string and then display
        for line in lines:                        
            fields = line.split(",")

            data_dict = {}
            data_dict["date_id"] = fields[0]
            data_dict["room_id"] = fields[1]
            data_dict["time_id"] = fields[2]
            data_dict["proj_id"] = fields[3]
            data_dict["teacher_group"] = fields[4]
            
            lis_id_teacher = fields[5].split("/")

            if not DateExam.objects.filter(id=fields[0]).exists() and fields[1] != "room_id":
                dict_date = {}
                dict_date["id"] = fields[0]
                dict_date["date_exam"] = fields[0][:2]+"/"+fields[0][2:4]+"/"+fields[0][4:8]
                dict_date["time_period"] = fields[0][8]
                dict_date["room_id"] = fields[0][9]
                try:
                    form_date = DateExamForm(dict_date)
                    if form_date.is_valid():
                        form_date.save()
                    else:
                        logging.getLogger("error_logger").error(form_date.errors.as_json())
                except Exception as e:
                    logging.getLogger("error_logger").error(form_date.errors.as_json())                    
                    pass
            try:
                form = ScheduleRoomForm(data_dict)
                if form.is_valid():
                    sche = form.save()
                    form.save()
                    for id_t in lis_id_teacher:
                        teacher = Teacher.objects.get(id=id_t)
                        teacher.schedule_teacher.add(sche)
                        teacher.save()
                    Project.objects.filter(id=fields[3]).update(schedule_id_id=sche.id)
                else:
                    logging.getLogger("error_logger").error(form.errors.as_json())                                                
            except Exception as e:
                logging.getLogger("error_logger").error(form.errors.as_json())                    
                pass
 
    except Exception as e:
        logging.getLogger("error_logger").error("Unable to upload file. "+repr(e))
        messages.error(request,"Unable to upload file. "+repr(e))
        return HttpResponseRedirect(reverse("manage"))
 
    return render(request,"upload_csv.html")

# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////      old code here    ////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////////////////////////////////

def manageTeacher(major_id, date_input, period_input):
    list_teachers = []
    return list_teachers

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

def count_proj(major):
    # form_setting = Settings.objects.get(id=1).forms
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
    result.append(dic)

    return result

def manage_room(request):
    room_selected = request.POST.get('room_selected',None)
    major_selected = request.POST.get('major_selected',None)
    period_selected = request.POST.get('period_selected',None)
    date_selected = request.POST.get('date_selected',None)

    date_time = datetime.datetime.strptime(date_selected, "%d/%m/%Y")
    list_proj_id, keep_proj_id = [], []
    real_teacher = []
    create_schedule = False
    fail_teacher = False
    list_teachers = manageTeacher(major_selected, date_selected, period_selected)

    # check date in database and insert
    dataframe_date = pd.DataFrame(list(DateExam.objects.values('date_exam')))
    dataframe_period = pd.DataFrame(list(DateExam.objects.values('time_period')))
    dataframe_room = pd.DataFrame(list(DateExam.objects.values('room_id_id')))

    id_dateexam = str((date_selected+period_selected+room_selected).replace('/',''))

    if not DateExam.objects.filter(id=id_dateexam).exists() and not (list_teachers == [] or len(list_teachers) < 4):
        create_schedule = True
        date_insert = DateExam(id=id_dateexam, date_exam=date_selected, time_period=period_selected, room_id_id=room_selected)
        date_insert.save()

    # /////////////////////////////////////

    # check proj of teacher
    mobj_name = Major.objects.values('major_name')
    if create_schedule:
        proj_tch_advisor = pd.DataFrame(list(Project.objects.values('id').filter(proj_years=this_year, \
                        proj_advisor__in=[list_teachers[0], list_teachers[1], list_teachers[2]], \
                        schedule_id_id=None, proj_major=mobj_name.get(id=major_selected)['major_name'])))
        for i in range(3):
            proj_of_teacher = pd.DataFrame(list(Project.objects.values('id').filter(proj_years=this_year, \
                        proj_advisor=list_teachers[i], schedule_id_id=None, proj_major=mobj_name.get(id=major_selected)['major_name'])))
            if not proj_of_teacher.empty:
                rand_index = randint(0,len(proj_of_teacher)-1)
                if proj_of_teacher.iloc[rand_index]['id'] not in list_proj_id and len(list_proj_id) < 5:
                    list_proj_id.append(proj_of_teacher.iloc[rand_index]['id'])
        for i in range(len(proj_tch_advisor)):
            if not proj_tch_advisor.empty:
                if proj_tch_advisor.iloc[i]['id'] not in list_proj_id and len(list_proj_id) < 5:
                    list_proj_id.append(proj_tch_advisor.iloc[i]['id'])
    if list_proj_id == []:
        DateExam.objects.filter(id=id_dateexam).delete()

    NoneType = type(None)
    max_count = ScheduleRoom.objects.all().aggregate(Max('teacher_group'))['teacher_group__max']
    if type(max_count) == NoneType:
        max_count = 0

    if create_schedule:
        for i in range(len(list_proj_id)):
            time_id_condition = 1 if(int(period_selected) == 0) else 6
            if not ScheduleRoom.objects.filter(date_id_id=id_dateexam, time_id_id=i+time_id_condition, room_id_id=int(room_selected)).exists():
                schedule = ScheduleRoom(teacher_group=max_count+1, room_id_id=int(room_selected), \
                            date_id_id=id_dateexam, proj_id=list_proj_id[i], time_id_id=i+time_id_condition)
                schedule.save()
                for name in list_teachers:
                    teacher_r = Teacher.objects.get(teacher_name=name)
                    teacher_r.schedule_teacher.add(schedule)
                    teacher_r.save()
                    teacher_r = Teacher.objects.filter(teacher_name=name).update(proj_group_exam=max_count+1)
                Project.objects.filter(id=list_proj_id[i]).update(schedule_id_id=schedule.id)

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
        advisor_result = proj_objs.proj_advisor
        time_result = TimeExam.objects.values('time_exam').get(id=schedule_all.iloc[i]['time_id_id'])['time_exam']
        major_result = Major.objects.values('major_name').get(major_name=proj_objs.proj_major)['major_name']

        result_manage.append({'teacher_group': schedule_all.iloc[i]['teacher_group'], 'room_name': room_result ,\
                    'date_exam': date_result, 'proj_name_th': proj_result, 'major_name':major_result, \
                    'time_exam': time_result, 'proj_advisor':advisor_result})

    return render(request,"result_room.html",{'list_result_teacher': teacher_groups, 'ScheduleRoom': result_manage})

def admin_required(login_url=None):
    return user_passes_test(lambda u: u.is_superuser, login_url=login_url)

@login_required
@admin_required(login_url="login/")
def manage(request):
    try:
        reset_selected = int(request.POST.get('reset_gen',None))
        if reset_selected:
            Project.objects.filter(proj_years=this_year).update(schedule_id_id=None)
            DateExam.objects.all().delete()
            Teacher.objects.all().order_by('proj_group_exam').update(proj_group_exam=0)
            Teacher.save()
        pre = prepare_render()
        return render(request,"manage.html",{'rooms': Room.objects.all(), 'majors':Major.objects.all(), 'proj_count': pre[0],
                    'room_period':pre[1]})
    except Exception as error:
        pre = prepare_render()
        return render(request,"manage.html",{'rooms': Room.objects.all(), 'majors':Major.objects.all(), 'proj_count': pre[0],
                    'room_period':pre[1]})