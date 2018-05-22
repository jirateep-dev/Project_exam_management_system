from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse,  HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from .forms import *
import csv, codecs
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
from random import randint, shuffle
import statistics
import logging

def this_year():
    return Project.objects.all().aggregate(Max('proj_years'))['proj_years__max']

def lastname_tch(tch_name):
    split_name = tch_name.split(' ')
    last_name = split_name[len(split_name)-1]
    return last_name

def export_csv(request):
    setting = Settings.objects.get(id=1)
    sc = ScheduleRoom.objects.filter(semester=setting.forms)
    proj = Project.objects.filter(proj_years=this_year(), proj_semester=setting.forms)
    teachers = Teacher.objects.all()
    room = Room.objects.all()
    time = TimeExam.objects.all()
    date = DateExam.objects.all()

    lis_ex = [["date", "room", "time", "proj_name_th", "proj_name_en", "proj_major", "proj_advisor", "proj_co_advisor", \
    "teacher_group", "teacher1", "teacher2", "teacher3", "teacher4"]]
    
    lis_line = ['----------','----------','----------','----------','----------','----------',\
    '----------','----------','----------','----------','----------','----------','----------']

    checkloop = 1
    for objs in sc:
        lis_tch = []
        for tch in teachers:
            rel_tch = tch.schedule_teacher.all()
            for i in rel_tch:
                if objs.id == i.id:
                    lis_tch.append(tch.teacher_name)
        lis_sub = []
        lis_sub.extend([str(date.get(id=objs.date_id_id).date_exam), str(room.get(id=objs.room_id_id).room_name), str(time.get(id=objs.time_id_id).time_exam), \
        str(proj.get(id=objs.proj_id_id).proj_name_th), str(proj.get(id=objs.proj_id_id).proj_name_en), \
        str(proj.get(id=objs.proj_id_id).proj_major), str(proj.get(id=objs.proj_id_id).proj_advisor), \
        str(proj.get(id=objs.proj_id_id).proj_co_advisor), str(objs.teacher_group), str(lis_tch[0]), str(lis_tch[1]), str(lis_tch[2]), str(lis_tch[3])])
        
        if checkloop != objs.teacher_group:
            checkloop = objs.teacher_group
            lis_ex.append(lis_line)

        lis_ex.append(lis_sub)

    proj_null = proj.filter(schedule_id=None)

    for i in range(4):
        lis_ex.append(lis_line)
    lis_ex.append(['ลำดับ', 'ชื่อโปรเจคภาษาไทย', 'ชื่อโปรเจคภาษาอังกฤษ', 'แขนง', 'อาจารย์ที่ปรึกษา', 'อาจารย์ที่ปรึกษา(ร่วม)'])
    for idx,item in enumerate(proj_null):
        lis_ex.append([idx, item.proj_name_th, item.proj_name_en, item.proj_major, item.proj_advisor, item.proj_co_advisor])
    
    for i in range(4):
        lis_ex.append(lis_line)
    lis_ex.append(["ลำดับ", "รายชื่ออาจารย์"])

    for i in teachers:
        lis_ex.append([i.id, i.teacher_name])

    
    with open('schedule_room_sem'+str(setting.forms)+'.csv','w', newline='', encoding='utf-8-sig') as new_file:
        csv_writer = csv.writer(new_file, delimiter=',')
        csv_writer.writerows(lis_ex)
    new_file.closed

    with open('schedule_room_sem'+str(setting.forms)+'.csv', 'rb') as schedule_room:
        response = HttpResponse(schedule_room.read())
        response['content_type'] = 'application/schedule_room'
        response['Content-Disposition'] = 'attachment;filename='+'schedule_room_sem'+str(setting.forms)+'.csv'
        return response

    return HttpResponseRedirect(reverse("manage"))

def upload_csv(request):
    # if not GET, then proceed
    try:
        sem = Settings.objects.get(id=1).forms
        csv_file = request.FILES["csv_file"]
        Project.objects.filter(proj_years=this_year(), proj_semester=sem).update(schedule_id=None)
        DateExam.objects.all().filter(id__endswith=str(sem)).delete()
        room = Room.objects.all()
        time = TimeExam.objects.all()
        proj = Project.objects.all()
        teachers = Teacher.objects.all()
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request,'File is not CSV type')
            return HttpResponseRedirect(reverse("manage"))
        #if file is too large, return
        if csv_file.multiple_chunks():
            messages.error(request,"Uploaded file is too big (%.2f MB)." % (csv_file.size/(1000*1000),))
            return HttpResponseRedirect(reverse("manage"))
        
        file_data = csv_file.read().decode('UTF-8')
 
        lines = file_data.splitlines()
        #loop over the lines and save them in db. If error , store as string and then display
        for line in lines:                        
            fields = line.split(",")
            
            data_dict = {}
            dict_date = {}
            if room.filter(room_name=fields[1]).exists() and time.filter(time_exam=fields[2]).exists() and \
                proj.filter(proj_name_th=fields[3], proj_years=this_year(), proj_semester=str(sem)).exists() and\
                teachers.filter(teacher_name=fields[9]).exists() and teachers.filter(teacher_name=fields[10]).exists() and \
                teachers.filter(teacher_name=fields[11]).exists() and teachers.filter(teacher_name=fields[12]).exists():

                data_dict["date_id"] = fields[0].replace('/', '')+str(time.get(time_exam=fields[2]).time_period)+str(room.get(room_name=fields[1]).id)+str(sem)
                data_dict["room_id"] = str(room.get(room_name=fields[1]).id)
                data_dict["time_id"] = str(time.get(time_exam=fields[2]).id)
                data_dict["proj_id"] = str(proj.get(proj_name_th=fields[3], proj_semester=str(sem)).id)
                data_dict["teacher_group"] = fields[8]
                data_dict["semester"] = sem
                
                lis_id_teacher = [teachers.get(teacher_name=fields[9]).id, teachers.get(teacher_name=fields[10]).id, \
                teachers.get(teacher_name=fields[11]).id, teachers.get(teacher_name=fields[12]).id]

            if not DateExam.objects.filter(id=fields[0]).exists() and fields[1] != "room_id" and fields[1] != "----------" and \
                room.filter(room_name=fields[1]).exists() and time.filter(time_exam=fields[2]).exists():
                
                dict_date["id"] = fields[0].replace('/', '')+str(time.get(time_exam=fields[2]).time_period)+str(room.get(room_name=fields[1]).id)+str(sem)
                dict_date["date_exam"] = fields[0]
                dict_date["time_period"] = str(time.get(time_exam=fields[2]).time_period)
                dict_date["room_id"] = str(room.get(room_name=fields[1]).id)
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
                    proj.filter(proj_name_th=fields[3], proj_semester=str(sem)).update(schedule_id=sche.id)
                else:
                    logging.getLogger("error_logger").error(form.errors.as_json())                                                
            except Exception as e:
                logging.getLogger("error_logger").error(form.errors.as_json())                    
                pass
 
    except Exception as e:
        logging.getLogger("error_logger").error("Unable to upload file. "+repr(e))
        messages.error(request,"Unable to upload file. "+repr(e))
        return HttpResponseRedirect(reverse("manage"))
 
    return render(request,"upload_csv.html", {'proj_act':sem})


def approve_teacher(tch_name, date_selected, period_selected):
    load = Settings.objects.get(id=1).load
    sem = Settings.objects.get(id=1).forms
    approve_tch = False

    last_name = lastname_tch(tch_name)

    if not Teacher.objects.get(teacher_name__contains=last_name).schedule_teacher.filter(semester=sem).exists():
        approve_tch = True
    else:
        tid_sch = Teacher.objects.get(teacher_name__contains=last_name).schedule_teacher.filter(semester=sem)
        if len(tid_sch) <= load:
            sche_r = ScheduleRoom.objects.filter(semester=sem)
            chk_schedule = 0;
            for obj in tid_sch:
                date_id_check = sche_r.values('date_id_id').get(id=obj.id)['date_id_id']
                date_exam_chk = DateExam.objects.values('date_exam').get(id=date_id_check)['date_exam']
                time_period_chk = DateExam.objects.values('time_period').get(id=date_id_check)['time_period']
                if not (date_exam_chk == date_selected and time_period_chk == int(period_selected)):
                    chk_schedule += 1
                if chk_schedule == len(tid_sch):
                    approve_tch = True
        else:
            approve_tch = False

    return approve_tch

def level_safezone():
    levels = Teacher.objects.all().values_list('levels_teacher', flat=True).order_by('levels_teacher')
    cal_med = statistics.median(levels)
    sd_value = statistics.stdev(levels)
    plus_sd1 = Teacher.objects.filter(levels_teacher__lte=cal_med+sd_value).filter(levels_teacher__gte=cal_med)\
            .values_list('levels_teacher', flat=True).order_by('levels_teacher')
    minus_sd1 = Teacher.objects.filter(levels_teacher__lte=cal_med).filter(levels_teacher__gte=cal_med-sd_value)\
            .values_list('levels_teacher', flat=True).order_by('levels_teacher')
    
    min_safe = statistics.median(minus_sd1)
    max_safe = statistics.median(plus_sd1)

    return {'min':min_safe, 'max':max_safe}

def manageTeacher(major_id, date_input, period_input):
    list_teachers = []
    temp_tch = []
    setting = Settings.objects.get(id=1)
    major = Major.objects.get(id=major_id)
    teachers_all = Teacher.objects.all()

    proj_null = Project.objects.filter(proj_years=this_year(), proj_semester=setting.forms, \
                    proj_major=major.major_name, schedule_id=None)

    for i in proj_null:
        if approve_teacher(i.proj_advisor, date_input, period_input) and i.proj_advisor not in list_teachers:
            list_teachers.append(i.proj_advisor)
        if i.proj_co_advisor != '' and (approve_teacher(i.proj_co_advisor, date_input, period_input) and i.proj_co_advisor not in list_teachers and \
            not approve_teacher(i.proj_advisor, date_input, period_input)):
            list_teachers.append(i.proj_co_advisor)
        if len(list_teachers) == 3:
            break

    safe_zone = level_safezone()

    templis = list(list_teachers)
    chk_tch = []

    for i in teachers_all:
        boo = True
        for j in templis:
            last_name = lastname_tch(i.teacher_name)
            last_name_t = lastname_tch(j)
            if last_name == last_name_t:
                boo = False
        if approve_teacher(i.teacher_name, date_input, period_input) and boo and i.teacher_name not in chk_tch:
            chk_tch.append(i.teacher_name)
    
    count_end = 0

    if templis != []:
        while True:
            while len(list_teachers) != 4:
                tch_ran = Teacher.objects.order_by('?').first()
                check_lastname = True
                for i in range(len(list_teachers)):
                    last_name = lastname_tch(list_teachers[i])
                    last_name_t = lastname_tch(tch_ran.teacher_name)
                    if last_name == last_name_t:
                        check_lastname = False
                if approve_teacher(tch_ran.teacher_name, date_input, period_input) and check_lastname:
                    count_end += 1
                    list_teachers.append(tch_ran.teacher_name)
            if len(list_teachers) == 4:
                sum_lev = 0
                for name in list_teachers:
                    last_name = lastname_tch(name)
                    sum_lev += Teacher.objects.get(teacher_name__contains=last_name).levels_teacher
                avg_s = (sum_lev/4.0)
                if avg_s <= safe_zone['max'] and avg_s >= safe_zone['min']:
                    break
                else:
                    list_teachers = list(templis)
            if count_end == len(chk_tch):
                break
    shuffle(list_teachers)
    return [templis, list_teachers]

def count_proj(major):
    form_setting = Settings.objects.get(id=1).forms
    return len(Project.objects.filter(proj_years=this_year(), proj_semester=form_setting, schedule_id=None, proj_major=major))

def prepare_render():
    result = []
    dic = {}
    sem =Settings.objects.get(id=1).forms
    room = Room.objects.values('room_name')
    date = DateExam.objects.values('date_exam').filter(id__endswith=str(sem)).distinct()
    date_all = DateExam.objects.all()
    pc_result = [{'bi':count_proj('Business Intelligence'), 'ds':count_proj('Data Science'), 'es':count_proj('Embedded Systems'), \
                'mu':count_proj('Multimedia'), 'nw':count_proj('Network and Communication'), 'se':count_proj('Software Development')}]
    date_result = [date[i]['date_exam'] for i in range(len(date))]

    for i in date_result:
        dic_keep = {}
        period_zero = ['Available' for i in range(len(room))]
        period_one = ['Available' for i in range(len(room))]
        tp_date = DateExam.objects.values('time_period').filter(date_exam=i)
        rm_date = DateExam.objects.values('room_id_id').filter(date_exam=i)
        id_date = DateExam.objects.values('id').filter(date_exam=i)

        for j in range(len(tp_date)):
            dic_keep[j] = (rm_date[j]['room_id_id']-1, tp_date[j]['time_period'])

        for j in range(len(dic_keep)):
            try:
                proj_id = ScheduleRoom.objects.filter(date_id_id=id_date[j]['id'], semester=sem)
                lis_major = [Project.objects.get(id=i.proj_id_id).proj_major for i in proj_id]
                lis = []
                test_error = Project.objects.filter(id=proj_id[0].proj_id_id)
                for obj in proj_id:
                    type_proj = Project.objects.get(id=obj.proj_id_id)
                    if type_proj.proj_major+' : '+str(lis_major.count(type_proj.proj_major)) not in lis:
                        lis.append(type_proj.proj_major+' : '+str(lis_major.count(type_proj.proj_major)))
                    if dic_keep[j][1] == 0:
                        period_zero[dic_keep[j][0]] = lis
                    else:
                        period_one[dic_keep[j][0]] = lis
            except Exception as error:
                if dic_keep[j][1] == 0:
                    period_zero[dic_keep[j][0]] = 'Error'
                else:
                    period_one[dic_keep[j][0]] = 'Error'
        dic[i] = (period_zero, period_one)

    proj_null = Project.objects.filter(proj_years=this_year(), proj_semester=sem, schedule_id=None)

    result.append(pc_result)
    result.append(dic)
    result.append(proj_null)

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
    result_tch = manageTeacher(major_selected, date_selected, period_selected)
    list_teachers = result_tch[1]
    sem = Settings.objects.get(id=1).forms

    # check date in database and insert
    dataframe_date = pd.DataFrame(list(DateExam.objects.values('date_exam')))
    dataframe_period = pd.DataFrame(list(DateExam.objects.values('time_period')))
    dataframe_room = pd.DataFrame(list(DateExam.objects.values('room_id_id')))

    id_dateexam = str((date_selected+period_selected+room_selected+str(sem)).replace('/',''))

    if not DateExam.objects.filter(id=id_dateexam).exists() and not (list_teachers == [] or len(list_teachers) < 4):
        create_schedule = True
        date_insert = DateExam(id=id_dateexam, date_exam=date_selected, time_period=period_selected, room_id_id=room_selected)
        date_insert.save()

    # /////////////////////////////////////

    # check proj of teacher
    major = Major.objects.get(id=major_selected)

    if create_schedule:
        ad_teacher = result_tch[0]
        proj_ad = Project.objects.filter(proj_years=this_year(), proj_semester=sem,\
                 proj_advisor__in=ad_teacher,schedule_id=None, proj_major=major.major_name)
        proj_co_ad = Project.objects.filter(proj_years=this_year(), proj_semester=sem,\
                 proj_co_advisor__in=ad_teacher,schedule_id=None, proj_major=major.major_name)
        proj_result = []
        for i in proj_ad:
            if i not in proj_result:
                proj_result.append(i)
        for i in proj_co_ad:
            if i not in proj_result:
                proj_result.append(i)
        
        if len(proj_result) < 5 and proj_result != []:
            for pro in proj_result:
                list_proj_id.append(pro.id)
        else:
            s = set()
            while len(s) != 5:
                rand_index = randint(0,len(proj_result)-1)
                s.add(proj_result[rand_index])
            for obj in s:
                list_proj_id.append(obj.id)

    if list_proj_id == [] and not (list_teachers == [] or len(list_teachers) < 4):
        date = DateExam.objects.get(id=id_dateexam)
        sche = ScheduleRoom.objects.filter(date_id_id=date.id)
        for i in sche:
            Project.objects.filter(id=i.proj_id_id).update(schedule_id=None)
        DateExam.objects.filter(id=id_dateexam).delete()

    NoneType = type(None)

    proj_id = Project.objects.values_list('id', flat=True).filter(proj_years=this_year(), proj_semester=sem)
    max_count = ScheduleRoom.objects.filter(proj_id_id__in=proj_id).aggregate(Max('teacher_group'))['teacher_group__max']
    if type(max_count) == NoneType:
        max_count = 0

    if create_schedule:
        for i in range(len(list_proj_id)):
            time_id_condition = 1 if(int(period_selected) == 0) else 6
            if not ScheduleRoom.objects.filter(date_id_id=id_dateexam, time_id_id=i+time_id_condition, room_id_id=int(room_selected)).exists():
                schedule = ScheduleRoom(teacher_group=max_count+1, room_id_id=int(room_selected), \
                            date_id_id=id_dateexam, proj_id_id=list_proj_id[i], time_id_id=i+time_id_condition)
                schedule.save()
                Project.objects.filter(id=list_proj_id[i]).update(schedule_id=schedule.id)
                for name in list_teachers:
                    last_name = lastname_tch(name)
                    teacher_r = Teacher.objects.get(teacher_name__contains=last_name)
                    teacher_r.schedule_teacher.add(schedule)
                    teacher_r.save()
                    # teacher_r = Teacher.objects.filter(teacher_name__contains=last_name).update(proj_group_exam=max_count+1)
    pre = prepare_render()
    return render(request,"manage.html",{'rooms': Room.objects.all(), 'majors':Major.objects.all(), 'proj_count': pre[0],
                    'room_period':pre[1], 'proj_act':sem})

def table_room(request):
    teacher_groups = []
    result_manage = []
    # query teacher_group

    sem = Settings.objects.get(id=1).forms
    sched_r = ScheduleRoom.objects.filter(semester=str(sem))
    list_group = list(sched_r.values('teacher_group').filter(semester=str(sem)).distinct())
    for i in list_group:
        dtset_id_sch = sched_r.values('id').filter(teacher_group=i['teacher_group'])
        count_teacher = 0
        sum_lv = 0
        for j in range(4):
            id_sch = dtset_id_sch[0]['id']
            tch_obj = list(sched_r.get(id=id_sch).teacher_set.all())[j]
            sum_lv += tch_obj.levels_teacher
            count_teacher+=1
            avg = sum_lv/4.0
            teacher_groups.append({'proj_group_exam': i['teacher_group'], \
                                'teacher_name': tch_obj.teacher_name, \
                                'levels_teacher': str("{:.3f}".format(tch_obj.levels_teacher)), \
                                'count_group':j+1, \
                                'avg':float("{:.3f}".format(avg))})
            if count_proj == 3:
                sum_lv, avg = 0, 0

    # //////////////////////////////////////

    # query data to html
    schedule_all = ScheduleRoom.objects.filter(semester=str(sem))
    for i in schedule_all:
        proj_objs = Project.objects.get(schedule_id=i.id)
        room_result = Room.objects.values('room_name').get(id=i.room_id_id)['room_name']
        date_result = DateExam.objects.values('date_exam').get(id=i.date_id_id)['date_exam']
        proj_result = proj_objs.proj_name_th
        advisor_result = proj_objs.proj_advisor
        time_result = TimeExam.objects.values('time_exam').get(id=i.time_id_id)['time_exam']
        major_result = Major.objects.values('major_name').get(major_name=proj_objs.proj_major)['major_name']

        result_manage.append({'teacher_group': i.teacher_group, 'room_name': room_result ,\
                    'date_exam': date_result, 'proj_name_th': proj_result, 'major_name':major_result, \
                    'time_exam': time_result, 'proj_advisor':advisor_result})

    return render(request,"result_room.html",{'result_teacher': teacher_groups, 'ScheduleRoom': result_manage,\
             'safezone':level_safezone(), 'proj_act':sem, 'proj_years':this_year()})

def admin_required(login_url=None):
    return user_passes_test(lambda u: u.is_superuser, login_url=login_url)

@login_required
@admin_required(login_url="login/")
def manage(request):
    sem = Settings.objects.get(id=1).forms
    str_link = "manage.html"
        
    # if sem == 2:
    #     str_link = "manage_sem2.html"
    try:
        reset_selected = int(request.POST.get('reset_gen',None))
        table_projs = request.POST.get('table_projs',None)
        if reset_selected:
            Project.objects.filter(proj_years=this_year(), proj_semester=sem).update(schedule_id=None)
            DateExam.objects.all().filter(id__endswith=str(sem)).delete()
            projs = Project.objects.filter(proj_years=this_year(), proj_semester=sem)
            proj2 = Project.objects.filter(proj_years=this_year(), proj_semester=2)
            for proj in projs:
                ScoreProj.objects.filter(proj_id_id=proj.id).delete()
                ScoreAdvisor.objects.filter(proj_id_id=proj.id).delete()
                if sem == 2:
                    ScorePoster.objects.filter(proj_id_id=proj.id).delete()
                    for i in proj2:
                        if SchedulePoster.objects.filter(proj_id_id=i.id).exists():
                            SchedulePoster.objects.filter(proj_id_id=i.id).delete()
                            Project.objects.filter(id=i.id).update(sche_post_id=None)
        pre = prepare_render()
        return render(request,str_link,{'rooms': Room.objects.all(), 'majors':Major.objects.all(), 'proj_count': pre[0],
                    'room_period':pre[1], 'proj_null':pre[2], 'proj_act':sem, 'proj_years':this_year(), 'table_projs':table_projs})
    except Exception as error:
        table_projs = request.POST.get('table_projs',None)
        pre = prepare_render()
        return render(request,str_link,{'rooms': Room.objects.all(), 'majors':Major.objects.all(), 'proj_count': pre[0],
                    'room_period':pre[1], 'proj_null':pre[2], 'proj_act':sem, 'proj_years':this_year(), 'table_projs':table_projs})
