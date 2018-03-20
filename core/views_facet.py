from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from database_management.models import *
from django.db.models import Max
from django.db.models import Avg
from django.db.models import F
from django.shortcuts import redirect
from django.utils.html import format_html
import logging

log = logging.getLogger('django.db.backends')
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())

def admin_required(login_url=None):
    return user_passes_test(lambda u: u.is_superuser, login_url=login_url)

@login_required(login_url="login/")
def facet(request):
    return render(request,"facet.html")

@login_required(login_url="login/")
def export_script_scoreproj(request):
    # not present
    proj = Project.objects.filter(id__lte=218)
    teacher = Teacher.objects.filter(id__lte=32)
    with open('script_scoreproj.txt','w', newline='', encoding='utf-8-sig') as new_file:
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


    return render(request,"facet.html")