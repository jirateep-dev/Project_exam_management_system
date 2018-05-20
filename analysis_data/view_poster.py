from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse,  HttpResponseRedirect
from django.shortcuts import redirect
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
from random import randint
import random
import statistics
import logging

def admin_required(login_url=None):
    return user_passes_test(lambda u: u.is_superuser, login_url=login_url)

def this_year():
    return Project.objects.all().aggregate(Max('proj_years'))['proj_years__max']

def lastname_tch(tch_name):
    split_name = tch_name.split(' ')
    last_name = split_name[len(split_name)-1]
    return last_name

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

def prepare_render():
    result = []

    projs = Project.objects.filter(proj_years=this_year(), proj_semester=2)
    proj_2 = Project.objects.all()
    sch_post = SchedulePoster.objects.all()
    lis_sch = []
    tch = Teacher.objects.all()

    for proj in sch_post:
        for p in projs:
            if p.id == proj.proj_id_id:
                lis_sch.append(proj.proj_id_id)

    for i in range(1, len(lis_sch)+1):
        in_result = {}
        tch_lis = {}
        
        post_id = proj_2.get(id=lis_sch[i-1]).sche_post_id

        for t in tch:
            if t.schepost_teacher.filter(id=post_id).exists():
                tch_lis[t.teacher_name] = t.levels_teacher
        
        sum_v = 0
        if tch_lis != {}:
            for key, value in tch_lis.items():
                sum_v += value

            in_result['id'] = i
            in_result['proj_name'] = proj_2.get(id=lis_sch[i-1]).proj_name_th

            for i in range(1, len(tch_lis)+1):
                in_result['teacher'+str(i)] = list(tch_lis.keys())[i-1]
            in_result['avg'] = str("{:.3f}".format(sum_v / 3.0))
            result.append(in_result)

    return result

def upload_poster(request):
    # if not GET, then proceed
    try:
        sem = Settings.objects.get(id=1).forms
        csv_file = request.FILES["csv_file"]
        proj2 = Project.objects.filter(proj_years=this_year(), proj_semester=sem)
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
        count_line = 0
        date = ''
        tch_name = ''
        for line in lines:
            fields = line.split(",")
            if "การสอบโปสเตอร์ ณ วันที่" in fields[0] and count_line == 0:
                sp = fields[0].split()
                date = sp[-1]
                for obj in proj2:
                    SchedulePoster.objects.filter(proj_id_id=obj.id).delete()
                proj2.update(sche_post_id=None)
            if count_line >= 2:
                proj = Project.objects.filter(proj_years=this_year(), proj_semester=sem, proj_name_th=fields[1])
                schedule_post = SchedulePoster(date_post=date, proj_id_id=proj[0].id)
                schedule_post.save()
                proj.update(sche_post_id=schedule_post.id)
                for i in range(2, 5):
                    if Teacher.objects.filter(teacher_name=fields[i]).exists():
                        tch_name = fields[i]
                    tch = Teacher.objects.get(teacher_name=tch_name)
                    if not tch.schepost_teacher.filter(proj_id_id=proj[0].id).exists() and \
                        not tch.schepost_teacher.filter(proj_id_id=proj[0].id).exists() and \
                        not tch.schepost_teacher.filter(proj_id_id=proj[0].id).exists():
                        tch.schepost_teacher.add(schedule_post)
                        tch.save()
                
            count_line += 1
            
    except Exception as e:
        logging.getLogger("error_logger").error("Unable to upload file. "+repr(e))
        messages.error(request,"Unable to upload file. "+repr(e))
        return HttpResponseRedirect(reverse("manage_poster"))
 
    return render(request,"upload_csv.html", {'proj_act':sem})
    
def export_poster(request):
    pre = prepare_render()
    sem = Settings.objects.get(id=1).forms
    date = SchedulePoster.objects.all().values_list('date_post', flat=True).distinct()
    teachers = Teacher.objects.all()
    projs = Project.objects.filter(proj_years=this_year(), proj_semester=sem)
    date_post = ''
    if len(date) != 0:
        date_post = date[len(date)-1]

    lis_ex = [["การสอบโปสเตอร์ ณ วันที่ "+date_post], ["ลำดับ", "รายชื่อโปรเจค", "อาจารย์คนที่ 1", "อาจารย์คนที่ 2", "อาจารย์คนที่ 3"]]
    lis_line = ['----------','----------','----------','----------','----------']

    for obj in pre:
        lis_ex.append([obj['id'], obj['proj_name'],obj['teacher1'],obj['teacher2'],obj['teacher3']])
    
    for i in range(4):
        lis_ex.append(lis_line)
    lis_ex.append(["ลำดับ", "รายชื่ออาจารย์"])

    for i in teachers:
        lis_ex.append([i.id, i.teacher_name])

    for i in range(4):
        lis_ex.append(lis_line)
    lis_ex.append(["ลำดับ", "รายชื่อโปรเจค"])

    for i in range(1, len(projs)+1):
        lis_ex.append([i, projs[i-1].proj_name_th])
    
    with open('schedule_poster.csv','w', newline='', encoding='utf-8-sig') as new_file:
        csv_writer = csv.writer(new_file, delimiter=',')
        csv_writer.writerows(lis_ex)
    new_file.closed

    with open('schedule_poster.csv', 'rb') as schedule_poster:
        response = HttpResponse(schedule_poster.read())
        response['content_type'] = 'application/schedule_poster'
        response['Content-Disposition'] = 'attachment;filename=schedule_poster.csv'
        return response

    return HttpResponseRedirect(reverse("manage_poster"))

@admin_required(login_url="login/")
def generate_poster(request):
    date_selected = request.POST.get('date_selected',None)

    teachers = Teacher.objects.all()
    projs_sem2 = Project.objects.filter(proj_years=this_year(), proj_semester=2).filter(~Q(schedule_id=None))
    projs = Project.objects.filter(proj_years=this_year(), proj_semester=2, sche_post_id=None)
    lis_inx = [i for i in range(len(projs))]
    sche = ScheduleRoom.objects.filter(semester=1)
    safe_zone = level_safezone()
    load_set = Settings.objects.get(id=1).load_post

    if len(projs) != 0:
        for index in range(len(projs)):
            new = projs[lis_inx.pop(random.randrange(len(lis_inx)))]
            old_tch = []
            for old in projs_sem2:
                if new.proj_name_th == old.proj_name_th:
                    for t in teachers:
                        if t.schedule_teacher.filter(proj_id_id=old.id).exists():
                            old_tch.append(t.teacher_name)
            while True:
                new_tch = []
                while len(new_tch) != 3:
                    tch_ran = Teacher.objects.order_by('?').first()
                    load = len(Teacher.objects.get(teacher_name=tch_ran.teacher_name).schepost_teacher.all())
                    if tch_ran.teacher_name not in new_tch and tch_ran.teacher_name not in old_tch and load <= load_set and tch_ran.teacher_name != ' ':
                        new_tch.append(tch_ran.teacher_name)
                sum_lev = 0
                for name in new_tch:
                    last_name = lastname_tch(name)
                    sum_lev += Teacher.objects.get(teacher_name__contains=last_name).levels_teacher
                if (sum_lev/3.0) <= safe_zone['max'] and (sum_lev/3.0) >= safe_zone['min']:
                    break
            if len(new_tch) == 3:
                schedule = SchedulePoster(date_post=date_selected, proj_id_id=new.id)
                schedule.save()
                Project.objects.filter(id=new.id).update(sche_post_id=schedule.id)
                for name in new_tch:
                    last_name = lastname_tch(name)
                    teacher_r = Teacher.objects.get(teacher_name__contains=last_name)
                    teacher_r.schepost_teacher.add(schedule)
                    teacher_r.save()
    return redirect('manage_poster')

@admin_required(login_url="login/")
def manage_poster(request):
    re_post = request.POST.get('re_post',None)
    proj2 = Project.objects.filter(proj_years=this_year(), proj_semester=2)
    proj2_null = Project.objects.filter(proj_years=this_year(), proj_semester=2, schedule_id=None)
    if re_post:
        for i in proj2:
            if SchedulePoster.objects.filter(proj_id_id=i.id).exists():
                SchedulePoster.objects.filter(proj_id_id=i.id).delete()
                Project.objects.filter(id=i.id).update(sche_post_id=None)

    sem = Settings.objects.get(id=1).forms
    date = SchedulePoster.objects.all().values_list('date_post', flat=True).distinct()
    date_post = ''
    result={}
    if len(date) != 0:
        date_post = date[len(date)-1]
        result = prepare_render()
    
    safe_zone = level_safezone()
    return render(request,"poster.html", {'proj_act':sem, 'date':date_post, 'result':result, 'safezone':safe_zone, 'proj2_null':proj2_null})