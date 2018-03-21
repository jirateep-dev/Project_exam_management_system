from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse,  HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from database_management.models import *
from django.db.models import Max
from django.db.models import Avg
from django.db.models import F
from django.shortcuts import redirect
from django.utils.html import format_html
import logging
import numpy

log = logging.getLogger('django.db.backends')
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())

tch = Teacher.objects.filter(id__lte=32)
col_de = ['รายชื่ออาจารย์','การวัดผลคะแนนโปรเจค','การวัดผลคะแนนโปสเตอร์','ระดับคะแนนอาจารย์']

teachers = [[i.teacher_name, str(i.measure_sproj), str(i.measure_spost), str(i.levels_teacher)] for i in tch]

def avg(lis):
    """uses floating-point division."""
    return sum(lis) / float(len(lis))

def admin_required(login_url=None):
    return user_passes_test(lambda u: u.is_superuser, login_url=login_url)

@login_required(login_url="login/")
def facet(request):
    
    return render(request, 'facet.html', {'teachers':teachers, 'col_de':col_de})

@login_required(login_url="login/")
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
        for line in lines:
            str_line = "{}".format(line.strip())
            if 'Title = Analytic Scoring Project' in str_line:
                type_data = 1
            if 'Title = Analytic Scoring Poster' in str_line:
                type_data = 2
            if 'Teacher Measurement Report  (arranged by mN)' in str_line:
                chk = True
            if 'Teacher Measurement Report  (arranged by fN)' in str_line or '-----------------' in str_line:
                chk = False
            if chk:
                num += 1
            spt = str_line.split()
            if num > 6 and chk:
                print(line.strip())
                if type_data == 1:
                    Teacher.objects.filter(id=int(spt[22])).update(measure_sproj=float(spt[6]))
                if type_data == 2:
                    Teacher.objects.filter(id=int(spt[22])).update(measure_spost=float(spt[6]))
        
        for i in tch:
            mean_i = avg([i.measure_sproj, i.measure_spost])
            Teacher.objects.filter(id = i.id).update(levels_teacher=mean_i)
    except Exception:
        return render(request, 'facet.html', {'teachers':teachers, 'col_de':col_de})

    return render(request, 'facet.html', {'teachers':teachers, 'col_de':col_de})

@login_required(login_url="login/")
def export_script(request):
    # not present
    proj = Project.objects.filter(id__lte=218)
    teacher = Teacher.objects.filter(id__lte=32)
    with open('script_scoreproj.txt','w') as new_file:
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
        score_proj = ScoreProj.objects.filter(id__lte=469)

        for s in score_proj:
            teacher_relate = Teacher.objects.filter(score_projs__proj_id_id=s.proj_id_id).filter(score_projs__id=s.id)
            for t in teacher_relate:
                list_teacher.append(t.id)
        
        for i in score_proj:
            new_file.write(str(i.proj_id_id)+','+str(list_teacher[i.id-1])+','+'1-9'+','+str(i.presentation)+','+str(i.question)+','+\
            str(i.report)+','+str(i.presentation_media)+','+str(i.discover)+','+\
            str(i.analysis)+','+str(i.quantity)+','+str(i.levels)+','+str(i.quality)+'\r\n')

        new_file.close()

    

    with open('script_scorepost.txt','w') as new_file:
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
        score_post = ScorePoster.objects.filter(id__lte=469)

        for s in score_post:
            teacher_relate = Teacher.objects.filter(score_posters__proj_id_id=s.proj_id_id).filter(score_posters__id=s.id)
            for t in teacher_relate:
                list_teacher.append(t.id)
        
        for i in score_post:
            new_file.write(str(i.proj_id_id)+','+str(list_teacher[i.id-1])+','+'1-6'+','+str(i.time_spo)+','+str(i.character_spo)+','+\
            str(i.presentation_spo)+','+str(i.question_spo)+','+str(i.media_spo)+','+str(i.quality_spo)+'\r\n')

        new_file.close()


    return render(request, 'facet.html', {'teachers':teachers, 'col_de':col_de})