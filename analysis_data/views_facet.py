from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse,  HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from database_management.models import *
from django.db.models import Max
from django.db.models import Avg, Sum
from django.db.models import F
from django.shortcuts import redirect
from django.utils.html import format_html
try:
    from BytesIO import BytesIO
except ImportError:
    from io import BytesIO
from zipfile import ZipFile
import logging
import numpy
import statistics
import chardet

log = logging.getLogger('django.db.backends')
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())

col_de = ['รายชื่ออาจารย์','การวัดผลคะแนนโปรเจค','การวัดผลคะแนนโปสเตอร์','ระดับคะแนนอาจารย์']

def detail_teacher():
    # test limite id32
    # tch = Teacher.objects.filter(id__lte=32)
    tch = Teacher.objects.all()
    teachers = [[i.teacher_name, str("{:.3f}".format(i.measure_sproj)), \
    str("{:.3f}".format(i.measure_spost)), str("{:.3f}".format(i.levels_teacher))] for i in tch]
    return teachers

def avg(lis):
    """uses floating-point division."""
    return sum(lis) / float(len(lis))

def level_safezone():
    levels = Teacher.objects.all().values_list('levels_teacher', flat=True).order_by('levels_teacher')
    tch = Teacher.objects.all().order_by('levels_teacher')
    cal_med = statistics.median(levels)
    sd_value = statistics.stdev(levels)
    plus_sd1 = Teacher.objects.filter(levels_teacher__lte=cal_med+sd_value).filter(levels_teacher__gte=cal_med)\
            .values_list('levels_teacher', flat=True).order_by('levels_teacher')
    minus_sd1 = Teacher.objects.filter(levels_teacher__lte=cal_med).filter(levels_teacher__gte=cal_med-sd_value)\
            .values_list('levels_teacher', flat=True).order_by('levels_teacher')
    
    min_safe = statistics.median(minus_sd1)
    max_safe = statistics.median(plus_sd1)

    return {'min':min_safe, 'max':max_safe, 'minus_sd1':minus_sd1[0], \
            'plus_sd1':plus_sd1[len(plus_sd1)-1], 'cal_med':cal_med, 'minus_normal':tch[0].levels_teacher, 'plus_normal':tch[len(tch)-1].levels_teacher}

def len_teacher(min_in, max_in):
    teachers = Teacher.objects.all().order_by('levels_teacher')
    lis = []

    for i in teachers:
        if i.levels_teacher <= max_in and i.levels_teacher >= min_in:
            lis.append(i)

    return len(lis)

def chart_facet():
    dic = level_safezone()
    tch = Teacher.objects.all().order_by('levels_teacher')
    count_teacher = {'normal':len(tch),\
                     'minus_sd1':len_teacher(dic.get('minus_sd1'), dic.get('cal_med')),\
                     'plus_sd1':len_teacher(dic.get('cal_med'), dic.get('plus_sd1')), \
                     'minus_sd05':len_teacher(dic.get('min'), dic.get('cal_med')),\
                     'plus_sd05':len_teacher(dic.get('cal_med'), dic.get('max')), \
                     'safe':len_teacher(dic.get('cal_med'), dic.get('max'))+len_teacher(dic.get('min'), dic.get('cal_med'))}
    result = {'count':count_teacher, 'levels':dic}
    return result

def facet(request):
    sem = Settings.objects.get(id=1).forms
    return render(request, 'facet.html', {'teachers':detail_teacher(), 'col_de':col_de,\
                 'proj_act':sem, 'chart_facet':chart_facet()})

def import_script(request):
    files = request.FILES["script_file"]

    if not files.name.endswith('.txt'):
        messages.error(request,'File is not txt type')
        return HttpResponseRedirect(reverse("facet"))
        #if file is too large, return
    if files.multiple_chunks():
        messages.error(request,"Uploaded file is too big (%.2f MB)." % (files.size/(1000*1000),))
        return HttpResponseRedirect(reverse("facet"))
    
    try:
        lines = files.readlines()
        chk = False
        num = 0
        type_data = 1
        count_end = 0
        for line in lines:
            str_line = "{}".format(line.strip())
            if 'Title = Analytic Scoring Project' in str_line:
                type_data = 1
            if 'Title = Analytic Scoring Poster' in str_line:
                type_data = 2
            if 'Teacher Measurement Report  (arranged by mN)' in str_line:
                chk = True
            if chk and '+------+' in str_line:
                count_end += 1
            if 'Teacher Measurement Report  (arranged by fN)' in str_line or count_end == 2:
                chk = False
                break
            if chk:
                num += 1
            spt = str_line.split()
            if num > 6 and chk:
                print(line.strip())
                if type_data == 1:
                    Teacher.objects.filter(id=int(spt[22])).update(measure_sproj="{:.3f}".format(float(spt[6])))
                if type_data == 2:
                    Teacher.objects.filter(id=int(spt[22])).update(measure_spost="{:.3f}".format(float(spt[6])))
        tch_all = Teacher.objects.all()

        lis_measure = [[],[]]
        for i in tch_all:
            if i.measure_sproj != 0:
                lis_measure[0].append(i.measure_sproj)
            if i.measure_spost != 0:
                lis_measure[1].append(i.measure_spost)
        
        new_tch_sproj = Teacher.objects.filter(measure_sproj=0)
        new_tch_spost = Teacher.objects.filter(measure_spost=0)
        if lis_measure[0] != []:
            avgm_sproj = statistics.median(lis_measure[0])
            new_tch_sproj.update(measure_sproj=avgm_sproj)

        if lis_measure[1] != []:
            avgm_spost = statistics.median(lis_measure[1])
            new_tch_spost.update(measure_spost=avgm_spost)

        tch_all = Teacher.objects.all()
        for i in tch_all:
            mean_i = avg([i.measure_sproj, i.measure_spost])
            Teacher.objects.filter(id = i.id).update(levels_teacher="{:.3f}".format(float(mean_i)))
    except Exception as e:
        messages.error(request,e)
        return HttpResponseRedirect(reverse("facet"))

    return HttpResponseRedirect(reverse("facet"))

def export_script(request):
    # not present
    # proj = Project.objects.filter(id__lte=218)
    # teacher = Teacher.objects.filter(id__lte=32)
    proj = Project.objects.all()
    teacher = Teacher.objects.all()
    with open('script_scoreproj.txt','w', encoding='utf-8-sig') as new_file:
        new_file.write( 'Title = Analytic Scoring Project\r\n' + \
                        'facet = 3\r\n' + \
                        'Pt-biserial = measure\r\n' + \
                        'Inter-rater = 2\r\n' + \
                        'Model = ?,?,?,Score\r\n' + \
                        'Rating scale = Score,R10\r\n' + \
                        '1 = lowest\r\n' + \
                        '5 = middle\r\n' + \
                        '10 = highest\r\n' + \
                        '*\r\n' +\
                        'Labels =\r\n' +\
                        '1,Project\r\n')
        for i in proj:
            new_file.write(str(i.id)+'='+i.proj_name_th+'\r\n')
        new_file.write('*\r\n' +\
                        '2,Teacher\r\n')
        for i in teacher:
            new_file.write(str(i.id)+'='+i.teacher_name+'\r\n')
        new_file.write('*\r\n' +\
                        '3,Traits\r\n')
        num = 1
        for f in ScoreProj._meta.get_fields():
            if f.name not in ['teacher', 'id', 'proj_id']:
                new_file.write(str(num)+'='+f.name+'\r\n')
                num += 1
        new_file.write('*\r\n' +\
                        'Data=\r\n')

        list_teacher = []

        # query only not fake score ///////////////////////////////////////////////////////////////
        # score_proj = ScoreProj.objects.filter(id__lte=469)
        score_proj = ScoreProj.objects.all()

        for s in score_proj:
            teacher_relate = Teacher.objects.filter(score_projs__proj_id_id=s.proj_id_id).filter(score_projs__id=s.id)
            for t in teacher_relate:
                list_teacher.append(t.id)
        
        run = 0
        for i in score_proj:
            new_file.write(str(i.proj_id_id)+','+str(list_teacher[run])+','+'1-9'+','+str(i.presentation)+','+str(i.question)+','+\
            str(i.report)+','+str(i.presentation_media)+','+str(i.discover)+','+\
            str(i.analysis)+','+str(i.quantity)+','+str(i.levels)+','+str(i.quality)+'\r\n')
            run += 1

        new_file.close()

    with open('script_scorepost.txt','w', encoding='utf-8-sig') as new_file:
        new_file.write( 'Title = Analytic Scoring Poster\r\n' + \
                        'facet = 3\r\n' + \
                        'Pt-biserial = measure\r\n' + \
                        'Inter-rater = 2\r\n' + \
                        'Model = ?,?,?,Score\r\n' + \
                        'Rating scale = Score,R10\r\n' + \
                        '1 = lowest\r\n' + \
                        '5 = middle\r\n' + \
                        '10 = highest\r\n' + \
                        '*\r\n' +\
                        'Labels =\r\n' +\
                        '1,Project\r\n')
        for i in proj:
            new_file.write(str(i.id)+'='+i.proj_name_th+'\r\n')
        new_file.write('*\r\n' +\
                        '2,Teacher\r\n')
        for i in teacher:
            new_file.write(str(i.id)+'='+i.teacher_name+'\r\n')
        new_file.write('*\r\n' +\
                        '3,Traits\r\n')
        num = 1
        for f in ScorePoster._meta.get_fields():
            if f.name not in ['teacher', 'id', 'proj_id']:
                new_file.write(str(num)+'='+f.name+'\r\n')
                num += 1
        new_file.write('*\r\n' +\
                        'Data=\r\n')

        list_teacher = []
        # query only not fake score ///////////////////////////////////////////////////////////////
        # score_post = ScorePoster.objects.filter(id__lte=469)
        score_post = ScorePoster.objects.all()

        for s in score_post:
            teacher_relate = Teacher.objects.filter(score_posters__proj_id_id=s.proj_id_id).filter(score_posters__id=s.id)
            for t in teacher_relate:
                list_teacher.append(t.id)
        
        run = 0
        for i in score_post:
            new_file.write(str(i.proj_id_id)+','+str(list_teacher[run])+','+'1-6'+','+str(i.time_spo)+','+str(i.character_spo)+','+\
            str(i.presentation_spo)+','+str(i.question_spo)+','+str(i.media_spo)+','+str(i.quality_spo)+'\r\n')
            run += 1

        new_file.close()
    
    in_memory = BytesIO()

    with ZipFile(in_memory, "a") as zip:

        with open('script_scoreproj.txt', 'rb') as file:
            raw = file.read(32) # at most 32 bytes are returned
            encoding = chardet.detect(raw)['encoding']
        

        with open('script_scoreproj.txt', newline='', encoding=encoding) as script_scoreproj:
            zip.writestr("script_scoreproj.txt", script_scoreproj.read())
        with open('script_scorepost.txt', newline='', encoding=encoding) as script_scorepost:
            zip.writestr("script_scorepost.txt", script_scorepost.read())
        
        # fix for Linux zip files read in Windows
        for file in zip.filelist:
            file.create_system = 0
            
        zip.close()

        response = HttpResponse(content_type="application/x-zip-compressed")
        response["Content-Disposition"] = "attachment; filename=script.zip"
        
        in_memory.seek(0)
        response.write(in_memory.read())
        
        return response

    return HttpResponseRedirect(reverse("facet"))

def reset_teacher(request):
    Teacher.objects.update(measure_sproj=0, measure_spost=0, levels_teacher=0)
    return HttpResponseRedirect(reverse("facet"))