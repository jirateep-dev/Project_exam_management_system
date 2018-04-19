from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from database_management.models import *
from django.http import HttpResponse,  HttpResponseRedirect
from django.urls import reverse
from django.db.models import Max
from django.db.models import Avg
from django.db.models import F
from django.shortcuts import redirect
from django.utils.html import format_html
from django.contrib import messages
from .forms import *
try:
    from BytesIO import BytesIO
except ImportError:
    from io import BytesIO
from zipfile import ZipFile
import csv, codecs
import logging

LIST_COL = ['สื่อการนำเสนอ','การนำเสนอ','การตอบคำถาม','รายงาน','การค้นคว้า','การวิเคราะห์และออกแบบ','ปริมาณงาน','ความยากง่าย','คุณภาพของงาน']
LIST_COL_AD = ['การพัฒนาโครงงานตามวัตถุประสงค์','การปฏิบัติได้ตรงตามแผนที่วางไว้','การเลือกทฤษฏีและเครื่องมือ','การเข้าพบอาจารย์ที่ปรึกษา',\
            'การปรับปรุงแก้ไขรายงาน','คุณภาพของรายงาน','คุณภาพของโครงงาน']

def this_year():
    return Project.objects.all().aggregate(Max('proj_years'))['proj_years__max']

def export_forms(request):
    sem = Settings.objects.get(id=1).forms
    schedule = ScheduleRoom.objects.all()
    teachers = Teacher.objects.all()
    lis_result1 = [['คะแนนสอบโปรเจคภาคเรียนที่ '+str(sem)+' ปีการศึกษา '+str(this_year())], []]
    lis_result2 = [['คะแนนอาจารย์ที่ปรึกษาภาคเรียนที่ '+str(sem)+' ปีการศึกษา '+str(this_year())], []]
    lis_line2 = ['************','************','************','************','************','************','************',\
                '************','************','************','************']

    for tch in teachers:
        rel_tch = tch.schedule_teacher.all()
        split_name = tch.teacher_name.split(' ')
        last_name = split_name[len(split_name)-1]
        lis_sub1 = []
        lis_sub2 = []
        
        for sc in rel_tch:
            proj = Project.objects.get(id=sc.proj_id_id)
            advisor = proj.proj_advisor
            split_ad = advisor.split(' ')
            last_name2 = split_ad[len(split_ad)-1]
            if proj.proj_semester == sem and last_name != last_name2:
                lis_sub1.append([proj.proj_name_th, proj.proj_name_en])
            if proj.proj_semester == sem and last_name == last_name2:
                lis_sub2.append([proj.proj_name_th, proj.proj_name_en])
        if lis_sub1 != []:
            lis_sub1 = [['กรรมการคุมสอบ', tch.teacher_name],[], ['รายชื่อโครงงานภาษาไทย', 'รายชื่อโครงงานภาษาอังกฤษ']+LIST_COL]+lis_sub1
            lis_sub1.append(lis_line2)
            lis_sub1.append(lis_line2)
        if lis_sub2 != []:
            lis_sub2 = [['อาจารย์ที่ปรึกษา', tch.teacher_name],[], ['รายชื่อโครงงานภาษาไทย', 'รายชื่อโครงงานภาษาอังกฤษ']+LIST_COL_AD]+lis_sub2
            lis_sub2.append(lis_line2)
            lis_sub2.append(lis_line2)
        
        for i in lis_sub1:
            lis_result1.append(i)
        for i in lis_sub2:
            lis_result2.append(i)

    with open('form_score_proj.csv','w', newline='', encoding='utf-8-sig') as new_file:
        csv_writer = csv.writer(new_file, delimiter=',')
        csv_writer.writerows(lis_result1)
    new_file.closed

    with open('form_score_advisor.csv','w', newline='', encoding='utf-8-sig') as new_file:
        csv_writer = csv.writer(new_file, delimiter=',')
        csv_writer.writerows(lis_result2)
    new_file.closed

    in_memory = BytesIO()
    with ZipFile(in_memory, "a") as zip:

        with open('form_score_proj.csv', 'rb') as form_sproj:
            zip.writestr("form_score_proj.csv", form_sproj.read())
        with open('form_score_advisor.csv', 'rb') as form_sads:
            zip.writestr("form_score_advisor.csv", form_sads.read())
        
        # fix for Linux zip files read in Windows
        for file in zip.filelist:
            file.create_system = 0    
            
        zip.close()

        response = HttpResponse(content_type="application/x-zip-compressed")
        response["Content-Disposition"] = "attachment; filename=score.zip"
        
        in_memory.seek(0)    
        response.write(in_memory.read())
        
        return response

    return HttpResponseRedirect(reverse('result_sem1'))

def import_score(request):
    files = request.FILES["score_file"]

    if not files.name.endswith('.csv'):
        messages.error(request,'File is not csv type')
        return HttpResponseRedirect(reverse("result_sem1"))
        #if file is too large, return
    if files.multiple_chunks():
        messages.error(request,"Uploaded file is too big (%.2f MB)." % (files.size/(1000*1000),))
        return HttpResponseRedirect(reverse("result_sem1"))
    
    try:
        file_data = files.read().decode('UTF-8')
 
        lines = file_data.splitlines()
        #loop over the lines and save them in db. If error , store as string and then display
        for line in lines:                        
            fields = line.split(",")
            # str_line = "{}".format(line.strip())
            
    except Exception as e:
        messages.error(request,e)
        return HttpResponseRedirect(reverse("result_sem1"))

    return HttpResponseRedirect(reverse('result_sem1'))

def reset_score(request):

    return HttpResponseRedirect(reverse('result_sem1'))