from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from database_management.models import *
from django.db.models import Max
from django.db.models import Avg
from django.shortcuts import redirect
import logging

log = logging.getLogger('django.db.backends')
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())
THIS_YEARS = Project.objects.all().aggregate(Max('proj_years'))['proj_years__max']
LIST_COL = ['สื่อการนำเสนอ','การนำเสนอ','การตอบคำถาม','รายงาน','การค้นคว้า','การวิเคราะห์และออกแบบ','ปริมาณงาน','ความยากง่าย','คุณภาพของงาน']
LIST_COL_AD = ['การพัฒนาโครงงานตามวัตถุประสงค์','การปฏิบัติได้ตรงตามแผนที่วางไว้','การเลือกทฤษฏีและเครื่องมือ','การเข้าพบอาจารย์ที่ปรึกษา',\
            'การปรับปรุงแก้ไขรายงาน','คุณภาพของรายงาน','คุณภาพของโครงงาน']
LIST_COL_PO = ['การตรงต่อเวลา','บุคลิกภาพและการแต่งกาย','ความชัดเจนในการอธิบาย','ความชัดเจนในการตอบคำถาม','ความชัดเจนของสื่อ','คุณภาพของโครงงาน']
LIST_COL_RE = ['รหัสนักศึกษา','ชื่อ-นามสกุล','ชื่อโปรเจค','คะแนนโปรเจค (60%)','คะแนนอาจารย์ที่ปรึกษา (40%)']

def admin_required(login_url=None):
    return user_passes_test(lambda u: u.is_superuser, login_url=login_url)

@login_required
@admin_required(login_url="login/")
def settings(request):
    if request.method == 'POST':
        on_off = request.POST.get("on_off_sys", None)
        proj_num = request.POST.get("proj_num", None)
        
        if on_off == 'on':
            num_on_off = 1
        if on_off != 'on':
            num_on_off = 0
        if proj_num == 'on':
            proj_int = 1
        if proj_num != 'on':
            proj_int = 2

        Settings.objects.filter(id=1).update(activate=num_on_off, forms=proj_int)
        User.objects.filter(is_staff=0).update(is_active=num_on_off)
    info_setting = Settings.objects.get(id=1)
    return render(request,"settings.html", {'activated':info_setting.activate, 'proj_act':info_setting.forms})


@login_required(login_url="login/")
def scoreproj(request):
    info_setting = Settings.objects.get(id=1)
    projid_teacher = []
    if request.user.is_authenticated():
        user_id = request.user.id
        teacher_sp = Teacher.objects.get(login_user_id=user_id)
        projs = teacher_sp.schedule_teacher.all()
        for i in range(len(projs)):
            projid_teacher.append(projs[i].proj_id)

    queryset = []
    form_setting = Settings.objects.get(id=1).forms
    for i in range(len(projid_teacher)):
        if Project.objects.filter(proj_years=THIS_YEARS, proj_semester=form_setting, id=projid_teacher[i]).exists():
            queryset.append(Project.objects.get(id=projid_teacher[i]))
    lis_select = []

    if request.method == 'POST' and request.user.is_authenticated():
        user_id = request.user.id
        teacher_sp = Teacher.objects.get(login_user_id=user_id)
        proj_selected = request.POST.get("data_proj", None)
        if type(proj_selected) is not None:
            proj = Project.objects.get(proj_name_th=proj_selected)

            if teacher_sp.teacher_name == proj.proj_advisor:
                for i in range(len(LIST_COL_AD)):
                    lis_select.append('select_option'+str(i))
                return render(request, "scoreadvisor.html", {'Projectset':proj, 'column_name':LIST_COL_AD,\
            'range':range(1,11), 'len_col':lis_select, 'proj_act':info_setting.forms})

            if form_setting == 1:
                for i in range(len(LIST_COL)-1):
                    lis_select.append('select_option'+str(i))
                return render(request, "add_scoreproj1.html", {'Projectset':proj, 'column_name':LIST_COL[:len(LIST_COL)-1],\
            'range':range(1,11), 'len_col':lis_select, 'proj_act':info_setting.forms})

            if form_setting == 2:
                for i in range(len(LIST_COL)):
                    lis_select.append('select_option'+str(i))
                return render(request, "add_scoreproj1.html", {'Projectset':proj, 'column_name':LIST_COL,\
            'range':range(1,11), 'len_col':lis_select, 'proj_act':info_setting.forms})
        else:
            return render(request,"scoreproj.html",{'Projectset':queryset, 'proj_act':info_setting.forms})
    else:
        return render(request,"scoreproj.html",{'Projectset':queryset, 'proj_act':info_setting.forms})


@login_required(login_url="login/")
def scoreposter(request):
    info_setting = Settings.objects.get(id=1)
    return render(request,"scoreposter.html", {'proj_act':info_setting.forms})

@login_required(login_url="login/")
def result_sem1(request):
    info_setting = Settings.objects.get(id=1)
    project = Project.objects.filter(proj_years=THIS_YEARS)
    lis_stu = []

    for obj in project:
        stu = Student.objects.filter(proj_id_id=obj.id)
        for i in stu:
            lis_stu.append([i.student_id, i.student_name, obj.proj_name_th])


    return render(request,"result_score.html", {'proj_act':info_setting.forms, 'this_year':THIS_YEARS, \
            'col_result':LIST_COL_RE, 'list_student':lis_stu})

@login_required(login_url="login/")
def update_scoreproj(request):
    info_setting = Settings.objects.get(id=1)
    message = ''
    if request.method == 'POST' and request.user.is_authenticated():
        # get data from html
        user_id = request.user.id
        teacher_sp = Teacher.objects.get(login_user_id=user_id)
        proj_selected = request.POST.get("data_proj", None)
        proj = Project.objects.get(proj_name_th=proj_selected)
        form_setting = Settings.objects.get(id=1).forms
        lis_selected = []
        len_lis = 0

        if form_setting == 1:
            len_lis = len(LIST_COL)-1
        if form_setting == 2:
            len_lis = len(LIST_COL)
        if teacher_sp.teacher_name == proj.proj_advisor:
            len_lis = len(LIST_COL_AD)

        for i in range(len_lis):
            selected_option = request.POST.get("select_option"+str(i), None)
            lis_selected.append(int(selected_option))

        
        if not teacher_sp.score_projs.filter(proj_id_id=proj.id).exists() and teacher_sp.teacher_name != proj.proj_advisor:
            score_proj = ScoreProj(proj_id_id=proj.id, presentation=lis_selected[0], question=lis_selected[1], report=lis_selected[2],\
                            presentation_media=lis_selected[3], discover=lis_selected[4], analysis=lis_selected[5], \
                            quantity=lis_selected[6], levels=lis_selected[7])
            score_proj.save()
            teacher_sp.score_projs.add(score_proj)
            teacher_sp.save()
        else:
            message = 'ท่านได้ส่งคะแนนเป็นที่เรียบร้อยแล้ว คะแนนจะไม่ถูกอัพเดทหรือแก้ไขได้'
            if teacher_sp.teacher_name == proj.proj_advisor:
                message = ''
        if not teacher_sp.score_advisor.filter(proj_id_id=proj.id).exists() and teacher_sp.teacher_name == proj.proj_advisor:
            score_ad = ScoreAdvisor(proj_id_id=proj.id, propose=lis_selected[0], planning=lis_selected[1], tool=lis_selected[2],\
                            advice=lis_selected[3], improve=lis_selected[4], quality_report=lis_selected[5], \
                            quality_project=lis_selected[6])
            score_ad.save()
            teacher_sp.score_advisor.add(score_ad)
            teacher_sp.save()
        else:
            message = 'ท่านได้ส่งคะแนนเป็นที่เรียบร้อยแล้ว คะแนนจะไม่ถูกอัพเดทหรือแก้ไขได้'
            

    return render(request,"update_scoreproj.html", {'message':message, 'proj_act':info_setting.forms})