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

def upload_poster(request):
    sem = Settings.objects.get(id=1).forms
    return render(request,"upload_csv.html", {'proj_act':sem})
    
def export_poster(request):
    return HttpResponseRedirect(reverse("manage_poster"))

def prepare_render():
    result = []

    projs = Project.objects.filter(proj_years=this_year(), proj_semester=2)
    tch = Teacher.objects.all()

    for i in range(1, len(projs)+1):
        in_result = {}
        tch_lis = {}
        
        post_id = projs[i-1].sche_post_id

        for t in tch:
            if t.schepost_teacher.filter(id=post_id).exists():
                tch_lis[t.teacher_name] = t.levels_teacher
        
        sum_v = 0
        if tch_lis != {}:
            for key, value in tch_lis.items():
                sum_v += value

            in_result['id'] = i
            in_result['proj_name'] = projs[i-1].proj_name_th

            for i in range(1, len(tch_lis)+1):
                in_result['teacher'+str(i)] = list(tch_lis.keys())[i-1]
            in_result['avg'] = str("{:.3f}".format(sum_v / 3.0))
            result.append(in_result)

    return result

@admin_required(login_url="login/")
def generate_poster(request):
    date_selected = request.POST.get('date_selected',None)

    teachers = Teacher.objects.all()
    projs_sem2 = Project.objects.filter(proj_years=this_year(), proj_semester=2).filter(~Q(schedule_id=None))
    projs = Project.objects.filter(proj_years=this_year(), proj_semester=2, sche_post_id=None)
    sche = ScheduleRoom.objects.filter(semester=1)
    safe_zone = level_safezone()
    load_set = Settings.objects.get(id=1).load_post

    if len(projs) != 0:
        for new in projs:
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