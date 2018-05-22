from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login
from django.template import RequestContext
from ldap3 import Server, Connection, ALL
from django.shortcuts import render
from django.contrib.auth.models import User
from database_management.models import *
from django.db.models import Max
from django_python3_ldap.auth import LDAPBackend

def this_year():
    return Project.objects.all().aggregate(Max('proj_years'))['proj_years__max']

def data_user(user_model):
    projid_teacher = []
    

    try:
        if user_model.is_authenticated:
            user_id = user_model.id
            teacher_sp = Teacher.objects.get(login_user_id=user_id)
            projs = teacher_sp.schedule_teacher.all()
            for i in projs:
                projid_teacher.append(i.proj_id_id)
        queryset = []
        info_setting = Settings.objects.get(id=1)
        form_setting = info_setting.forms
        for i in range(len(projid_teacher)):
            if Project.objects.filter(proj_years=this_year(), proj_semester=form_setting, id=projid_teacher[i]).exists():
                queryset.append(Project.objects.get(id=projid_teacher[i]))
    except Exception:
        return False
    
    return queryset

def err_message(user):
    if user is not None:
        if user.is_active:   
            return [1, "User is valid, active and authenticated"]
        else:
            return [0, "The password is valid, but the account has been disabled!"]
    return [0, "The username and password were incorrect."]

def choice_return(request, err, user_model):
    form_setting = Settings.objects.get(id=1).forms
    state = err[1]
    data = data_user(user_model)
    if err[0] == 1 and data != False:
        login(request, user_model)
        return render(request,"scoreproj.html",{'Projectset':data_user(user_model), 'proj_act':form_setting})
    else:
        return render(request, 'login.html', {'err_ms':state})

def login_user(request):
    state = ""
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        info_setting = Settings.objects.get(id=1)
        form_setting = info_setting.forms
        try:       
            user = User.objects.get(username=username)
            s = Server('ldap://161.246.38.141', get_info=ALL, use_ssl=True) 
            c = Connection(s, user=username+"@it.kmitl.ac.th", password=password)
            user.backend = "django_python3_ldap.auth.LDAPBackend"
            user.save()
            try:
                if not c.bind():
                    user_model = authenticate(username=username, password=password)
                    err = err_message(user_model)
                    return choice_return(request, err, user_model)
            except Exception:
                user_model = authenticate(username=username, password=password)
                err = err_message(user_model)
                return choice_return(request, err, user_model)
            if user is not None and c.bind():
                if user.is_active:
                    login(request, user)
                    return render(request,"scoreproj.html",{'Projectset':data_user(user), 'proj_act':form_setting})
                else:
                    state = "The password is valid, but the account has been disabled!"
                    return render(request, 'login.html', {'err_ms':state})
            else:
                state = "The username and password were incorrect."
                return render(request, 'login.html', {'err_ms':state})
        except Exception:
            user_model = authenticate(username=username, password=password)
            err = err_message(user_model)
            return choice_return(request, err, user_model)
    return render(request, 'login.html', {'err_ms':state})