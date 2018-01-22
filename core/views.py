from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from database_management.models import Project
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
def update_scoreproj(request):
    if request.method == 'POST':
        proj_selected = request.POST.get("data_proj", None)
        lis_selected = []
        for i in range(len(list_column)-1):
            selected_option = request.POST.get("select_option"+str(i), None)
            lis_selected.append(int(selected_option))
        
    return render(request,"update_scoreproj.html")