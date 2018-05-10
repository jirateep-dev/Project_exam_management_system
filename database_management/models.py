#database_management / models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_prometheus.models import ExportModelOperationsMixin

import datetime

# class Major(ExportModelOperationsMixin('major'),models.Model):
class Major(models.Model):
    major_name = models.CharField(max_length=1024)
    objects = models.Manager()

    class Meta:
        verbose_name_plural = 'ตารางแขนง'

    def __str__(self):
        return self.major_name

# class Room(ExportModelOperationsMixin('room'),models.Model):
class Room(models.Model):
    room_name = models.CharField(max_length=1024)
    objects = models.Manager()

    class Meta:
        verbose_name_plural = 'ตาราง ห้อง'

    def __str__(self):
        return self.room_name

# class TimeExam(ExportModelOperationsMixin('timeexam'),models.Model):
class TimeExam(models.Model):
    time_exam = models.CharField(max_length=256)
    time_period = models.IntegerField(default=0)
    objects = models.Manager()

    class Meta:
        verbose_name_plural = 'ตารางเวลา'

# class DateExam(ExportModelOperationsMixin('dateexam'),models.Model):
class DateExam(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    date_exam = models.CharField(max_length=256)
    time_period = models.IntegerField(default=0)
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE, null=True)
    objects = models.Manager()

    class Meta:
        verbose_name_plural = 'ตารางวันที่สอบ'
    
    def __str__(self):
        return self.date_exam

# class Project(ExportModelOperationsMixin('project'),models.Model):
class Project(models.Model):
    schedule_id = models.IntegerField(blank=True, null=True)
    sche_post_id = models.IntegerField(blank=True, null=True)
    proj_years = models.IntegerField(default=0)
    proj_semester = models.IntegerField(default=1)
    proj_name_th = models.CharField(max_length=1024)
    proj_name_en = models.CharField(max_length=1024)
    proj_major = models.CharField(max_length=1024)
    proj_advisor = models.CharField(max_length=1024)
    proj_co_advisor = models.CharField(max_length=1024)
    objects = models.Manager()

    class Meta:
        verbose_name_plural = 'ตาราง โปรเจค'

    def __str__(self):
        return self.proj_name_th

# class ScheduleRoom(ExportModelOperationsMixin('scheduleroom'),models.Model):
class ScheduleRoom(models.Model):
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE)
    date_id = models.ForeignKey(DateExam, on_delete=models.CASCADE, null=True)
    time_id = models.ForeignKey(TimeExam, on_delete=models.CASCADE, null=True)
    proj_id = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    teacher_group = models.IntegerField(default=0)
    semester = models.IntegerField(default=1)
    objects = models.Manager()

    class Meta:
        verbose_name_plural = 'ตารางกำหนดการโปรเจค'

# class SchedulePoster(ExportModelOperationsMixin('scheduleposter'),models.Model):
class SchedulePoster(models.Model):
    date_post = models.CharField(max_length=256)
    proj_id = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    objects = models.Manager()

    class Meta:
        verbose_name_plural = 'ตารางกำหนดการโปสเตอร์'

# class ScoreProj(ExportModelOperationsMixin('scoreproj'),models.Model):
class ScoreProj(models.Model):
    proj_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    presentation = models.IntegerField(default=0)
    question = models.IntegerField(default=0)
    report = models.IntegerField(default=0)
    presentation_media = models.IntegerField(default=0)
    discover = models.IntegerField(default=0)
    analysis = models.IntegerField(default=0)
    quantity = models.IntegerField(default=0)
    levels = models.IntegerField(default=0)
    quality = models.IntegerField(default=0)
    objects = models.Manager()

    class Meta:
        verbose_name_plural = 'ตาราง คะแนนโปรเจค'

# class ScorePoster(ExportModelOperationsMixin('scoreposter'),models.Model):
class ScorePoster(models.Model):
    proj_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    time_spo = models.IntegerField(default=0)
    character_spo = models.IntegerField(default=0)
    presentation_spo = models.IntegerField(default=0)
    question_spo = models.IntegerField(default=0)
    media_spo = models.IntegerField(default=0)
    quality_spo = models.IntegerField(default=0)
    objects = models.Manager()

    class Meta:
        verbose_name_plural = 'ตาราง คะแนนโพสเตอร์'

# class ScoreAdvisor(ExportModelOperationsMixin('scoreadvisor'),models.Model):
class ScoreAdvisor(models.Model):
    proj_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    propose = models.IntegerField(default=0)
    planning = models.IntegerField(default=0)
    tool = models.IntegerField(default=0)
    advice = models.IntegerField(default=0)
    improve = models.IntegerField(default=0)
    quality_report =  models.IntegerField(default=0)
    quality_project = models.IntegerField(default=0)
    objects = models.Manager()

    class Meta:
        verbose_name_plural = 'ตาราง คะแนนที่ปรึกษา'

# class Teacher(ExportModelOperationsMixin('teacher'),models.Model):
class Teacher(models.Model):
    login_user = models.ForeignKey(User, on_delete=models.CASCADE, unique=True)
    teacher_name = models.CharField(max_length=1024)
    measure_sproj = models.FloatField(default=0)
    measure_spost = models.FloatField(default=0)
    levels_teacher = models.FloatField(default=0)
    score_projs = models.ManyToManyField(ScoreProj)
    score_posters = models.ManyToManyField(ScorePoster)
    score_advisor = models.ManyToManyField(ScoreAdvisor)
    major_teacher = models.ManyToManyField(Major)
    schedule_teacher = models.ManyToManyField(ScheduleRoom)
    schepost_teacher = models.ManyToManyField(SchedulePoster)
    objects = models.Manager()

    class Meta:
        ordering = ['login_user']
        verbose_name_plural = 'ตาราง อาจารย์'

    def __str__(self):
        return self.teacher_name

# class Student(ExportModelOperationsMixin('student'),models.Model):
class Student(models.Model):
    proj1_id = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, related_name='+')
    proj2_id = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, related_name='+')
    student_id = models.CharField(max_length=1024)
    student_name = models.CharField(max_length=1024, default='')
    objects = models.Manager()

    class Meta:
        verbose_name_plural = 'ตาราง นักศึกษา'

    def __str__(self):
        return self.student_id

# class Settings(ExportModelOperationsMixin('setting'),models.Model):
class Settings(models.Model):
    load = models.IntegerField(default=8)
    load_post = models.IntegerField(default=6)
    activate = models.IntegerField(default=1)
    forms = models.IntegerField(default=1)
    objects = models.Manager()
    
    class Meta:
        verbose_name_plural = 'ตาราง คะแนนที่ปรึกษา'

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        teacher = Teacher.objects.create(login_user=instance)
        teacher.save()
    else:
        Teacher.objects.filter(login_user=instance).update(teacher_name=instance.first_name+' '+instance.last_name)