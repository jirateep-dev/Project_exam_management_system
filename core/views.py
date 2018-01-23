from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from database_management.models import Project, ScoreProj, Teacher
from django.db.models import Max
import logging

log = logging.getLogger('django.db.backends')
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())
this_year = Project.objects.all().aggregate(Max('proj_years'))['proj_years__max']
list_column = ['สื่อการนำเสนอ','การนำเสนอ','การตอบคำถาม','รายงาน','การค้นคว้า','การวิเคราะห์และออกแบบ','ปริมาณงาน','ความยากง่าย','คุณภาพของงาน']

@login_required(login_url="login/")
def home(request):
    return render(request,"home.html")

@login_required(login_url="login/")
def scoreproj(request):
    queryset = Project.objects.filter(proj_years=this_year)
    lis_select = []
    for i in range(len(list_column)-1):
        lis_select.append('select_option'+str(i))
    return render(request,"scoreproj.html",{'Projectset':queryset, 'column_name':list_column[:len(list_column)-1],'range':range(1,11), 'len_col':lis_select})

@login_required(login_url="login/")
def scoreposter(request):
    return render(request,"scoreposter.html")

@login_required(login_url="login/")
def calculate_score(request):
    return 1

@login_required(login_url="login/")
def update_scoreproj(request):
    if request.method == 'POST':
        # get data from html
        proj_selected = request.POST.get("data_proj", None)
        lis_selected = []
        for i in range(len(list_column)-1):
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
                id_sc = teacher_sp.score_projs.filter(proj_id_id=proj.id)[0].id
                ScoreProj.objects.filter(id=id_sc).update(presentation=lis_selected[0], question=lis_selected[1], report=lis_selected[2],\
                            presentation_media=lis_selected[3], discover=lis_selected[4], analysis=lis_selected[5], \
                            quantity=lis_selected[6], levels=lis_selected[7])

    return render(request,"update_scoreproj.html")