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

log = logging.getLogger('django.db.backends')
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())
LIST_COL = ['สื่อการนำเสนอ','การนำเสนอ','การตอบคำถาม','รายงาน','การค้นคว้า','การวิเคราะห์และออกแบบ','ปริมาณงาน','ความยากง่าย','คุณภาพของงาน']
LIST_COL_AD = ['การพัฒนาโครงงานตามวัตถุประสงค์','การปฏิบัติได้ตรงตามแผนที่วางไว้','การเลือกทฤษฏีและเครื่องมือ','การเข้าพบอาจารย์ที่ปรึกษา',\
            'การปรับปรุงแก้ไขรายงาน','คุณภาพของรายงาน','คุณภาพของโครงงาน']
LIST_COL_PO = ['การตรงต่อเวลา','บุคลิกภาพและการแต่งกาย','ความชัดเจนในการอธิบาย','ความชัดเจนในการตอบคำถาม','ความชัดเจนของสื่อ','คุณภาพของโครงงาน']
LIST_COL_RE = ['รหัสนักศึกษา','ชื่อ-นามสกุล','ชื่อโปรเจค','คะแนนโปรเจค (60%)','คะแนนอาจารย์ที่ปรึกษา (40%)', 'ผลรวมคะแนน', 'รายละอียด']
LIST_COL_RE2 = ['รหัสนักศึกษา','ชื่อ-นามสกุล','ชื่อโปรเจค','คะแนนโปรเจค (40%)','คะแนนโปสเตอร์ (20%)','คะแนนอาจารย์ที่ปรึกษา (40%)', 'ผลรวมคะแนน', 'รายละอียด']
LIST_COL_DE = [['รายชื่ออาจารย์']+LIST_COL, ['รายชื่ออาจารย์']+LIST_COL_PO , ['อาจารย์ที่ปรึกษา']+LIST_COL_AD]
LIST_COL_PROJ = ['ปีการศึกษา', 'เทอม', 'ชื่อโปรเจค(TH)', 'ชื่อโปรเจค(EN)', 'แขนง', 'ที่ปรึกษา', 'ที่ปรึกษา(ร่วม)', 'รายละเอียด']

def this_year():
    return Project.objects.all().aggregate(Max('proj_years'))['proj_years__max']

def lastname_tch(tch_name):
    split_name = tch_name.split(' ')
    last_name = split_name[len(split_name)-1]
    return last_name

def admin_required(login_url=None):
    return user_passes_test(lambda u: u.is_superuser, login_url=login_url)

@login_required
def upload_projs(request):
    
    return render(request, "upload_projs.html")

@login_required
@admin_required(login_url="login/")
def settings(request):
    if request.method == 'POST':
        on_off = request.POST.get("on_off_sys", None)
        proj_num = request.POST.get("proj_num", None)
        load = request.POST.get("load_tch", None)
        load_post = request.POST.get("load_tch_post", None)
        if on_off == 'on':
            num_on_off = 1
        if on_off != 'on':
            num_on_off = 0
        if proj_num == 'on':
            proj_int = 1
        if proj_num != 'on':
            proj_int = 2

        Settings.objects.filter(id=1).update(load=load,load_post=load_post, activate=num_on_off, forms=proj_int)
        User.objects.filter(is_staff=0).update(is_active=num_on_off)
    info_setting = Settings.objects.get(id=1)
    return render(request,"settings.html", {'activated':info_setting.activate, 'proj_act':info_setting.forms, \
     'load_proj':info_setting.load, 'load_post':info_setting.load_post})

def manage_student(std_dic, p_semester, proj):
    if Student.objects.filter(id=std_dic['pk']).exists():
        if p_semester == '1':
            Student.objects.filter(id=std_dic['pk']).update(proj1_id_id=proj.id, \
            student_id=std_dic['std_id'], student_name=std_dic['name'])
            if Student.objects.get(id=std_dic['pk']).proj1_id_id == Student.objects.get(id=std_dic['pk']).proj2_id_id:
                Student.objects.filter(id=std_dic['pk']).update(proj2_id_id=None)
        else:
            Student.objects.filter(id=std_dic['pk']).update(proj2_id_id=proj.id, \
            student_id=std_dic['std_id'], student_name=std_dic['name'])
            if Student.objects.get(id=std_dic['pk']).proj1_id_id == Student.objects.get(id=std_dic['pk']).proj2_id_id:
                Student.objects.filter(id=std_dic['pk']).update(proj1_id_id=None)
    else:
        if p_semester == '1':
            new_std = Student(proj1_id_id=proj.id, proj2_id_id='', student_id=std_dic['std_id'], student_name=std_dic['name'])
            new_std.save()
        else:
            new_std = Student(proj1_id_id='', proj2_id_id=proj.id, student_id=std_dic['std_id'], student_name=std_dic['name'])
            new_std.save()


def del_projs(del_semester):
    projs = Project.objects.filter(proj_years=this_year(), proj_semester=del_semester)
    for proj in projs:
        Student.objects.filter(proj1_id_id=proj.id).update(proj1_id_id=None)
        Student.objects.filter(proj2_id_id=proj.id).update(proj2_id_id=None)
    
    Student.objects.filter(proj1_id_id=None).filter(proj2_id_id=None).delete()
    Project.objects.filter(proj_years=this_year(), proj_semester=del_semester).delete()

    return True

def import_student(data_std, semester, proj_form):
    std_id = data_std.get('student_id')
    std_name = data_std.get('student_name')
    if Student.objects.filter(student_id=std_id).exists():
        if semester == '1':
            Student.objects.filter(student_id=std_id).update(proj1_id_id=proj_form.id)
        else:
            Student.objects.filter(student_id=std_id).update(proj2_id_id=proj_form.id)
    else:
        if semester == '1':
            std = Student(proj1_id_id=proj_form.id, proj2_id_id=None, student_id=std_id, student_name=std_name)
            std.save()
        else:
            std = Student(proj1_id_id=None, proj2_id_id=proj_form.id, student_id=std_id, student_name=std_name)
            std.save()

def import_projs(request, csv_file, add_semester):
    # if not GET, then proceed
    try:
        if Project.objects.filter(proj_years=this_year(), proj_semester=add_semester).exists():
            Project.objects.filter(proj_years=this_year(), proj_semester=add_semester).delete()
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request,'File is not CSV type')
            return HttpResponseRedirect(reverse("manage_proj"))
        #if file is too large, return
        if csv_file.multiple_chunks():
            messages.error(request,"Uploaded file is too big (%.2f MB)." % (csv_file.size/(1000*1000),))
            return HttpResponseRedirect(reverse("manage_proj"))
        
        file_data = csv_file.read().decode('UTF-8')
 
        lines = file_data.splitlines()
        #loop over the lines and save them in db. If error , store as string and then display
        start = False
        for line in lines:                        
            fields = line.split(",")
            data_dict = {}
            data_std1, data_std2 = {}, {}
            print(fields)
            if fields[0].isdigit():
                start = True
            if start:
                data_dict["proj_years"] = this_year()
                data_dict["proj_semester"] = add_semester
                data_dict["proj_name_th"] = fields[1]
                data_dict["proj_name_en"] = fields[2]
                data_dict["proj_major"] = fields[9]
                data_dict["proj_advisor"] = fields[7]
                if '-' in fields[8] and len(fields[8]) <= 3:
                    fields[8] = ''
                data_dict["proj_co_advisor"] = fields[8]

                data_std1["student_id"] = fields[3]
                data_std1["student_name"] = fields[4]

                if '-' in fields[5] and len(fields[5]) <= 3:
                    fields[5] = ''
                    fields[6] = ''
                data_std2["student_id"] = fields[5]
                data_std2["student_name"] = fields[6]
                try:
                    form = ProjectForm(data_dict)
                    if form.is_valid():
                        proj = form.save()
                        form.save()
                        import_student(data_std1, add_semester, proj)
                        import_student(data_std2, add_semester, proj)
                except Exception as e:
                    logging.getLogger("error_logger").error(form.errors.as_json())
                    pass
 
    except Exception as e:
        logging.getLogger("error_logger").error("Unable to upload file. "+repr(e))
        messages.error(request,"Unable to upload file. "+repr(e))
        return False
 
    return True

@login_required(login_url="login/")
def manage_proj(request):
    teacher = Teacher.objects.all()
    majors = Major.objects.all()
    info_setting = Settings.objects.get(id=1)
    projs = Project.objects.filter(proj_years=this_year())
    col_proj = 7
    list_projs = []
    for i in projs:
        list_projs.append([i.proj_years, i.proj_semester, i.proj_name_th, i.proj_name_en, i.proj_major, i.proj_advisor, i.proj_co_advisor])
    if request.method == 'POST':
        mproj = request.POST.get("mproj", None)
        if mproj == "mproj_add":
            return render(request, "mproj_add.html", {'teachers':teacher, 'majors':majors, 'proj_act':info_setting.forms})
        if mproj == "mproj_edit":
            col_proj = 8
            list_projs = []
            for i in projs:
                list_projs.append([i.proj_years, i.proj_semester, i.proj_name_th, i.proj_name_en, i.proj_major, i.proj_advisor, i.proj_co_advisor, \
                format_html("<button name="'"project_edit"'" type="'"submit"'" class="'"btn btn-warning"'" \
                form="'"manage_proj"'" value=""'"+str(i.proj_semester)+i.proj_name_th+"'""><h4 style="'"font-size: 1.7em;"'">แก้ไข</h4></button>")])
            
            return render(request, "manage_proj.html", {"col_result":LIST_COL_PROJ[:col_proj], "list_proj":list_projs, 'proj_act':info_setting.forms})
            # return render(request, "mproj_edit.html", {'proj':projs})
        if mproj == "mproj_del":
            col_proj = 8
            list_projs = []
            for i in projs:
                list_projs.append([i.proj_years, i.proj_semester, i.proj_name_th, i.proj_name_en, i.proj_major, i.proj_advisor, i.proj_co_advisor, \
                format_html("<button type="'"button"'"  class="'"open-Dialog btn btn-danger"'" data-toggle="'"modal"'" data-target="'"#del_modal"'"\
                data-id=""'"+str(i.proj_semester)+i.proj_name_th+"'""><h4 style="'"font-size: 1.7em;"'">ลบ</h4></button>")])
            return render(request, "manage_proj.html", {"col_result":LIST_COL_PROJ[:col_proj], "list_proj":list_projs, 'proj_act':info_setting.forms})

        pj_pk = request.POST.get('proj_pk', None)
        np_th = request.POST.get("proj_name_th", None)
        np_en = request.POST.get("proj_name_en", None)
        p_year = request.POST.get("proj_year", None)
        p_semester = request.POST.get("semester", None)
        p_major = request.POST.get("major", None)
        n_t = request.POST.get("t_name", None)
        n_cot = request.POST.get("cot_name", None)

        std1_pk = request.POST.get("std1_pk", None)
        std1_id = request.POST.get("std1_id", None)
        pre_std1 = request.POST.get("std1_pre_name", None)
        std1_fname = request.POST.get("std1_fname", None)
        std1_lname = request.POST.get("std1_lname", None)

        std2_pk = request.POST.get("std2_pk", None)
        std2_id = request.POST.get("std2_id", None)
        pre_std2 = request.POST.get("std2_pre_name", None)
        std2_fname = request.POST.get("std2_fname", None)
        std2_lname = request.POST.get("std2_lname", None)

        proj_d = request.POST.get("project_del", None)
        proj_e = request.POST.get("project_edit", None)

        del_semester = request.POST.get("del_semester", None)
        add_semester = request.POST.get("add_semester", None)

        try:
            csv_file = request.FILES["csv_file"]
        except Exception:
            pass

        if not type(del_semester) is type(None):
            if del_projs(del_semester):
               return HttpResponseRedirect(reverse('manage_proj'))


        if not type(add_semester) is type(None) and not type(csv_file) is type(None):
           if import_projs(request, csv_file, add_semester):
               return HttpResponseRedirect(reverse('upload_projs'))

        chk = True
        lis_chk = [np_th, np_en, p_year, p_semester, p_major, n_t, std1_id, pre_std1, std1_fname, std1_lname]

        for i in lis_chk:
            if type(i) is type(None):
                chk = False
                break

        if chk:
            if type(n_cot) is type(None):
                n_cot = ''
            if type(std2_id) is type(None) or type(pre_std2) is type(None) or type(std2_fname) is type(None):
                pre_std2 = ''
                std2_fname = ''
                std2_lname = ''
                std2_id = ''
            if type(std2_lname) is type(None):
                std2_lname = ''

            if Project.objects.filter(id=pj_pk).exists():
                Project.objects.filter(id=pj_pk).update(proj_years=p_year, proj_semester=p_semester,\
                 proj_name_th=np_th, proj_name_en=np_en, proj_major=p_major, proj_advisor=n_t, proj_co_advisor=n_cot)

                get_proj = Project.objects.get(id=pj_pk)
                std1_nstr = pre_std1+std1_fname+' '+std1_lname
                std2_nstr = pre_std2+std2_fname+' '+std2_lname
                std_dic = {'std1':{'pk':std1_pk, 'std_id':std1_id, 'name':std1_nstr}, \
                'std2':{'pk':std2_pk, 'std_id':std2_id, 'name':std2_nstr}}
                if std1_pk != '':
                    manage_student(std_dic['std1'], p_semester, get_proj)
                if std2_pk != '':
                    manage_student(std_dic['std2'], p_semester, get_proj)
            
            else:
                new_proj = Project(proj_years=p_year, proj_semester=p_semester, proj_name_th=np_th, proj_name_en=np_en,\
                                proj_major=p_major, proj_advisor=n_t, proj_co_advisor=n_cot)
                new_proj.save()

                std1_nstr = pre_std1+std1_fname+' '+std1_lname
                std2_nstr = pre_std2+std2_fname+' '+std2_lname
                std_dic = {'std1':{'pk':std1_pk, 'std_id':std1_id, 'name':std1_nstr}, \
                'std2':{'pk':std2_pk, 'std_id':std2_id, 'name':std2_nstr}}
                if std1_pk != '':
                    manage_student(std_dic['std1'], p_semester, new_proj)
                if std2_pk != '':
                    manage_student(std_dic['std2'], p_semester, new_proj)

            return HttpResponseRedirect(reverse("manage_proj"))
        
        if type(proj_d) is not type(None):
            proj_del = Project.objects.filter(proj_semester=proj_d[0], proj_name_th=proj_d[1:])

            if proj_d[0] == '1':
                Student.objects.filter(proj1_id_id=proj_del[0].id).update(proj1_id_id=None)
            else:
                Student.objects.filter(proj2_id_id=proj_del[0].id).update(proj2_id_id=None)
            Student.objects.filter(proj1_id_id=None).filter(proj2_id_id=None).delete()
            proj_del.delete()
            return HttpResponseRedirect(reverse("manage_proj"))
        
        if type(proj_e) is not type(None):
            pedit_selected = Project.objects.get(proj_semester=proj_e[0], proj_name_th=proj_e[1:])
            if int(proj_e[0]) == 1:
                stds = Student.objects.filter(proj1_id_id=pedit_selected.id)
            else:
                stds = Student.objects.filter(proj2_id_id=pedit_selected.id)
            
            stds1 = stds[0]
            students = {}
            name_s1 = stds1.student_name.split(" ")

            if name_s1[0][:6] == 'นางสาว':
                pre1 = 'นางสาว'
                fname1 = name_s1[0][6:]
            else:
                pre1 = name_s1[0][:3]
                fname1 = name_s1[0][3:]
            lname1 = name_s1[1]
            students['std1'] = {'id':stds1.id, 'std_id':stds1.student_id, 'pre':pre1, 'fname':fname1, 'lname':lname1}

            if len(stds) == 2:
                stds2 = stds[1]
                name_s2 = stds2.student_name.split(" ")

                if name_s2[0][:6] == 'นางสาว':
                    pre2 = 'นางสาว'
                    fname2 = name_s2[0][6:]
                else:
                    pre2 = name_s2[0][:3]
                    fname2 = name_s2[0][3:]
                lname2 = name_s2[1]
                students['std2'] = {'id':stds2.id, 'std_id':stds2.student_id, 'pre':pre2, 'fname':fname2, 'lname':lname2}
            
            return render(request, "mproj_edit2.html", {'proj':pedit_selected, 'teachers':teacher, 'majors':majors, \
            'students':students, 'proj_act':info_setting.forms})
    

    return render(request, "manage_proj.html", {"col_result":LIST_COL_PROJ[:col_proj], "list_proj":list_projs, \
                'proj_act':info_setting.forms})

@login_required(login_url="login/")
def scoreproj(request):
    info_setting = Settings.objects.get(id=1)
    projid_teacher = []
    if request.user.is_authenticated:
        user_id = request.user.id
        teacher_sp = Teacher.objects.get(login_user_id=user_id)
        projs = teacher_sp.schedule_teacher.all()
        for i in range(len(projs)):
            projid_teacher.append(projs[i].proj_id_id)

    queryset = []
    form_setting = info_setting.forms
    for i in range(len(projid_teacher)):
        if Project.objects.filter(proj_years=this_year(), proj_semester=form_setting, id=projid_teacher[i]).exists():
            queryset.append(Project.objects.get(id=projid_teacher[i]))
    lis_select = []

    if request.method == 'POST' and request.user.is_authenticated:
        user_id = request.user.id
        teacher_sp = Teacher.objects.get(login_user_id=user_id)
        proj_selected = request.POST.get("data_proj", None)
        if type(proj_selected) is not type(None):
            proj = Project.objects.get(proj_years=this_year(), proj_name_th=proj_selected, proj_semester=form_setting)

            lname_tch = lastname_tch(teacher_sp.teacher_name)
            lname_adv = lastname_tch(proj.proj_advisor)
            if lname_tch == lname_adv:
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
    project = Project.objects.filter(proj_years=this_year(), proj_semester=info_setting.forms)
    lis_stu = []
    max_sc = 220

    for num in range(len(project)):
        if info_setting.forms == 1:
            stu = Student.objects.filter(proj1_id_id=project[num].id)
            max_sc = 150
        else:
            stu = Student.objects.filter(proj2_id_id=project[num].id)

        # calculate score project (percentage)
        if info_setting.forms == 1:
            test = ScoreProj.objects.annotate(result_scoreproj = ((F('presentation')+F('presentation_media')+F('question'))/3.0+\
                F('report')+(F('discover')+F('analysis'))*1.5+(F('quantity')+F('levels'))/2.0)).filter(proj_id_id=project[num].id)
        else:
            test = ScoreProj.objects.annotate(result_scoreproj = ((F('presentation')+F('presentation_media')+F('question'))*0.667+\
                F('report')*2+(F('discover')+F('analysis'))*1.5+F('quantity')+F('levels')+F('quality'))*0.4).filter(proj_id_id=project[num].id)
        avg_scorep = 0
        for i in test:
            avg_scorep += i.result_scoreproj
        if len(test) != 0:
            avg_scorep = avg_scorep / len(test)

        # calculate score advisor (percentage)
        test = ScoreAdvisor.objects.annotate(result_score_advicsor = (F('propose')+F('planning')+F('tool')+\
            F('advice')+F('improve')+F('quality_report')+F('quality_project'))*0.5714).filter(proj_id_id=project[num].id)
        avg_scoread = 0
        for i in test:
            avg_scoread += i.result_score_advicsor
        if len(test) != 0:
            avg_scoread = avg_scoread / len(test)

        # calculate score poster (percentage)
        test = ScorePoster.objects.annotate(result_scorepost = ((F('time_spo')+F('character_spo')+F('presentation_spo')+\
            F('question_spo')+F('media_spo')+F('quality_spo'))*0.33)).filter(proj_id_id=project[num].id)
        avg_scorepo = 0
        for i in test:
            avg_scorepo += i.result_scorepost
        if len(test) != 0:
            avg_scorepo = avg_scorepo / len(test)

        for i in stu:
            if info_setting.forms == 1:
                lis_stu.append([i.student_id, i.student_name, project[num].proj_name_th, "%.2f" %avg_scorep, "%.2f" %avg_scoread, \
                "%.2f" %(avg_scorep+avg_scoread), format_html("<button name="'"detail"'" type="'"submit"'" class="'"btn btn-success"'" \
                form="'"detail_score"'" value='"+project[num].proj_name_th+"'><h4 style="'"font-size: 1.7em;"'">ดูรายละเอียด</h4></button>")])
            else:
                lis_stu.append([i.student_id, i.student_name, project[num].proj_name_th, "%.2f" %avg_scorep, "%.2f" %avg_scorepo, "%.2f" %avg_scoread, \
                "%.2f" %(avg_scorep+avg_scorepo+avg_scoread), format_html("<button name="'"detail"'" type="'"submit"'" class="'"btn btn-success"'" \
                form="'"detail_score"'" value='"+project[num].proj_name_th+"'><h4 style="'"font-size: 1.7em;"'">ดูรายละเอียด</h4></button>")])

    if info_setting.forms == 2:
        return render(request,"result_score.html", {'proj_act':info_setting.forms, 'this_year':this_year(), \
            'col_result':LIST_COL_RE2, 'list_student':lis_stu})
    return render(request,"result_score.html", {'proj_act':info_setting.forms, 'this_year':this_year(), \
            'col_result':LIST_COL_RE, 'list_student':lis_stu})

@login_required(login_url="login/")
def detail_score(request):
    try:
        if request.method == 'POST':
            proj_name = request.POST.get("detail", None)
            sem = Settings.objects.get(id=1).forms
            proj = Project.objects.get(proj_name_th=proj_name, proj_semester=sem)
            teacher = Teacher.objects.all()
            result_sproj = []
            result_spost = []
            result_sadvisor = []
            for i in teacher:
                if i.score_projs.filter(proj_id_id=proj.id).exists():
                    t_name = i.teacher_name
                    sc_de =  i.score_projs.get(proj_id_id=proj.id)
                    result_sproj.append([t_name, sc_de.presentation_media, sc_de.presentation, sc_de.question, sc_de.report,\
                                sc_de.discover, sc_de.analysis, sc_de.quantity, sc_de.levels, sc_de.quality])
                if i.score_advisor.filter(proj_id_id=proj.id).exists():
                    sc_ad = i.score_advisor.get(proj_id_id=proj.id)
                    t_ad_name = i.teacher_name
                    result_sadvisor.append([t_ad_name, sc_ad.propose, sc_ad.planning, sc_ad.tool, sc_ad.advice, sc_ad.improve,\
                    sc_ad.quality_report, sc_ad.quality_project])
                if i.score_posters.filter(proj_id_id=proj.id).exists():
                    sc_post = i.score_posters.get(proj_id_id=proj.id)
                    t_ad_name = i.teacher_name
                    result_spost.append([t_ad_name, sc_post.time_spo, sc_post.character_spo, sc_post.presentation_spo,\
                    sc_post.question_spo, sc_post.media_spo, sc_post.quality_spo])
    except Exception as e:
        return render(request, "detail_score.html", {'this_year':this_year(), 'proj_name':proj_name, 'col_de':LIST_COL_DE[0],\
         'result':[["Error :", "please generate schedule_poster and then generate form_score again"]],\
          'result1':[["Error :", "please generate schedule_poster and then generate form_score again"]],\
          'result2':[["Error :", "please generate schedule_poster and then generate form_score again"]],\
          'col_de1':LIST_COL_DE[1],'col_de2':LIST_COL_DE[2], 'proj_act':sem})
    
    return render(request, "detail_score.html", {'this_year':this_year(), 'proj_name':proj_name, 'col_de':LIST_COL_DE[0],\
         'result':result_sproj, 'result1':result_spost, 'col_de1':LIST_COL_DE[1],'col_de2':LIST_COL_DE[2], 'result2':result_sadvisor, 'proj_act':sem})

@login_required(login_url="login/")
def update_scoreproj(request):
    info_setting = Settings.objects.get(id=1)
    message = ''
    if request.method == 'POST' and request.user.is_authenticated:
        # get data from html
        user_id = request.user.id
        teacher_sp = Teacher.objects.get(login_user_id=user_id)
        proj_selected = request.POST.get("data_proj", None)
        proj = Project.objects.get(proj_name_th=proj_selected, proj_semester=info_setting.forms)
        form_setting = Settings.objects.get(id=1).forms
        lis_selected = []
        len_lis = 0

        if form_setting == 1:
            len_lis = len(LIST_COL)-1
        if form_setting == 2:
            len_lis = len(LIST_COL)
        if lastname_tch(teacher_sp.teacher_name) == lastname_tch(proj.proj_advisor):
            len_lis = len(LIST_COL_AD)

        for i in range(len_lis):
            selected_option = request.POST.get("select_option"+str(i), None)
            lis_selected.append(int(selected_option))

        
        if not teacher_sp.score_projs.filter(proj_id_id=proj.id).exists() and lastname_tch(teacher_sp.teacher_name) != lastname_tch(proj.proj_advisor):
            if info_setting.forms == 1:
                score_proj = ScoreProj(proj_id_id=proj.id, presentation=lis_selected[0], question=lis_selected[1], report=lis_selected[2],\
                                presentation_media=lis_selected[3], discover=lis_selected[4], analysis=lis_selected[5], \
                                quantity=lis_selected[6], levels=lis_selected[7])
            else:
                score_proj = ScoreProj(proj_id_id=proj.id, presentation=lis_selected[0], question=lis_selected[1], report=lis_selected[2],\
                                presentation_media=lis_selected[3], discover=lis_selected[4], analysis=lis_selected[5], \
                                quantity=lis_selected[6], levels=lis_selected[7], quality=lis_selected[8])
            
            score_proj.save()
            teacher_sp.score_projs.add(score_proj)
            teacher_sp.save()
        else:
            message = 'ท่านได้ส่งคะแนนเป็นที่เรียบร้อยแล้ว คะแนนจะไม่ถูกอัพเดทหรือแก้ไขได้'
            if lastname_tch(teacher_sp.teacher_name) == lastname_tch(proj.proj_advisor):
                message = ''
        if not teacher_sp.score_advisor.filter(proj_id_id=proj.id).exists() and lastname_tch(teacher_sp.teacher_name) == lastname_tch(proj.proj_advisor):
            score_ad = ScoreAdvisor(proj_id_id=proj.id, propose=lis_selected[0], planning=lis_selected[1], tool=lis_selected[2],\
                            advice=lis_selected[3], improve=lis_selected[4], quality_report=lis_selected[5], \
                            quality_project=lis_selected[6])
            score_ad.save()
            teacher_sp.score_advisor.add(score_ad)
            teacher_sp.save()
        else:
            message = 'ท่านได้ส่งคะแนนเป็นที่เรียบร้อยแล้ว คะแนนจะไม่ถูกอัพเดทหรือแก้ไขได้'
            

    return render(request,"update_scoreproj.html", {'message':message, 'proj_act':info_setting.forms})