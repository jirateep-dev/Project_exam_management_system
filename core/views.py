from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from database_management.models import Project
import logging

log = logging.getLogger('django.db.backends')
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())

@login_required(login_url="login/")
def home(request):
    return render(request,"home.html")

@login_required(login_url="login/")
def scoreproj(request):
    queryset = Project.objects.all()
    list_column = ['สื่อการนำเสนอ','การนำเสนอ','การตอบคำถาม','รายงาน','การค้นคว้า','การวิเคราะห์และออกแบบ','ปริมาณงาน','ความยากง่าย','คุณภาพของงาน']
    return render(request,"scoreproj.html",{'Projectset':queryset, 'column_name':list_column,'range':range(11)})

@login_required(login_url="login/")
def scoreposter(request):
    return render(request,"scoreposter.html")