from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from database_management.models import *
from django.shortcuts import redirect
from django.db.models import Max
import logging

log = logging.getLogger('django.db.backends')
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())
THIS_YEARS = Project.objects.all().aggregate(Max('proj_years'))['proj_years__max']
LIST_COL = ['สื่อการนำเสนอ','การนำเสนอ','การตอบคำถาม','รายงาน','การค้นคว้า','การวิเคราะห์และออกแบบ','ปริมาณงาน','ความยากง่าย','คุณภาพของงาน']


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
    for i in range(len(LIST_COL)-1):
        lis_select.append('select_option'+str(i))

    if request.method == 'POST':
        proj_selected = request.POST.get("data_proj", None)
        if type(proj_selected) is not None:
            proj = Project.objects.get(proj_name_th=proj_selected)
            if form_setting == 1:
                return render(request, "add_scoreproj1.html", {'Projectset':proj, 'column_name':LIST_COL[:len(LIST_COL)-1],\
            'range':range(1,11), 'len_col':lis_select, 'proj_act':info_setting.forms})
            if form_setting == 2:
                return render(request, "add_scoreproj2.html", {'Projectset':proj, 'column_name':LIST_COL[:len(LIST_COL)],\
            'range':range(1,11), 'len_col':lis_select, 'proj_act':info_setting.forms})
        else:
            return render(request,"scoreproj.html",{'Projectset':queryset, 'proj_act':info_setting.forms})
    else:
        return render(request,"scoreproj.html",{'Projectset':queryset, 'proj_act':info_setting.forms})


@login_required(login_url="login/")
def scoreposter(request):
    info_setting = Settings.objects.get(id=1)
    return render(request,"scoreposter.html")

@login_required(login_url="login/")
def calculate_score(request):
    return 1

@login_required(login_url="login/")
def update_scoreproj(request):
    info_setting = Settings.objects.get(id=1)
    message = ''
    if request.method == 'POST':
        # get data from html
        proj_selected = request.POST.get("data_proj", None)
        lis_selected = []
        for i in range(len(LIST_COL)-1):
            selected_option = request.POST.get("select_option"+str(i), None)
            lis_selected.append(int(selected_option))
        user_id = None
        if request.user.is_authenticated():
            user_id = request.user.id
            teacher_sp = Teacher.objects.get(login_user_id=user_id)
            proj = Project.objects.get(proj_name_th=proj_selected)
            if not teacher_sp.score_projs.filter(proj_id_id=proj.id).exists():
                score_proj = ScoreProj(proj_id_id=proj.id, presentation=lis_selected[0], question=lis_selected[1], report=lis_selected[2],\
                                presentation_media=lis_selected[3], discover=lis_selected[4], analysis=lis_selected[5], \
                                quantity=lis_selected[6], levels=lis_selected[7])
                score_proj.save()
                teacher_sp.score_projs.add(score_proj)
                teacher_sp.save()
            else:
                message = 'ก่อนหน้านี้ท่านได้ส่งคะแนนเป็นที่เรียบร้อยแล้ว คะแนนจะไม่ถูกอัพเดทหรือแก้ไขได้'
            #     id_sc = teacher_sp.score_projs.filter(proj_id_id=proj.id)[0].id
            #     ScoreProj.objects.filter(id=id_sc).update(presentation=lis_selected[0], question=lis_selected[1], report=lis_selected[2],\
            #                 presentation_media=lis_selected[3], discover=lis_selected[4], analysis=lis_selected[5], \
            #                 quantity=lis_selected[6], levels=lis_selected[7])

    return render(request,"update_scoreproj.html", {'message':message, 'proj_act':info_setting.forms})