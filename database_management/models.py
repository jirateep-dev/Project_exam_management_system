#database_management / models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

class Major(models.Model):
    major_name = models.CharField(max_length=1024)
    objects = models.Manager()

    class Meta:
        verbose_name_plural = 'ตารางแขนง'

    def __str__(self):
        return self.major_name

class Room(models.Model):
    room_name = models.CharField(max_length=1024)
    objects = models.Manager()

    class Meta:
        verbose_name_plural = 'ตาราง ห้อง'

    def __str__(self):
        return self.room_name

class TimeExam(models.Model):
    time_exam = models.CharField(max_length=256)
    time_period = models.IntegerField(default=0)
    objects = models.Manager()

    class Meta:
        verbose_name_plural = 'ตารางเวลา'

class DateExam(models.Model):
    date_exam = models.CharField(max_length=256)
    time_period = models.IntegerField(default=0)
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE, null=True)
    objects = models.Manager()

    class Meta:
        verbose_name_plural = 'ตารางวันที่สอบ'
    
    def __str__(self):
        return self.date_exam

class ScheduleRoom(models.Model):
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE)
    date_id = models.ForeignKey(DateExam, on_delete=models.CASCADE, null=True)
    time_id = models.ForeignKey(TimeExam, on_delete=models.CASCADE, null=True)
    # proj_id = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    proj_id = models.IntegerField(default=0)
    teacher_group = models.IntegerField(default=0)
    objects = models.Manager()

    class Meta:
        verbose_name_plural = 'ตารางกำหนดการ'

class Project(models.Model):
    schedule_id = models.ForeignKey(ScheduleRoom, on_delete=models.SET_NULL, null=True)
    # schedule_id = models.OneToOneField(ScheduleRoom, on_delete=models.CASCADE, blank=True, null=True)
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
        
class ScoreProj(models.Model):
    proj_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    presentation_media = models.IntegerField(default=0)
    presentation = models.IntegerField(default=0)
    question = models.IntegerField(default=0)
    report = models.IntegerField(default=0)
    discover = models.IntegerField(default=0)
    analysis = models.IntegerField(default=0)
    quantity = models.IntegerField(default=0)
    levels = models.IntegerField(default=0)
    quality = models.IntegerField(default=0)
    objects = models.Manager()

    class Meta:
        verbose_name_plural = 'ตาราง คะแนนโปรเจค'

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

class Teacher(models.Model):
    login_user = models.ForeignKey(User, on_delete=models.CASCADE)
    teacher_name = models.CharField(max_length=1024)
    proj_group_exam = models.IntegerField(default=0)
    proj_group_poster = models.IntegerField(default=0)
    levels_teacher = models.IntegerField(default=1)
    score_projs = models.ManyToManyField(ScoreProj)
    score_posters = models.ManyToManyField(ScorePoster)
    score_advisor = models.ManyToManyField(ScoreAdvisor)
    major_teacher = models.ManyToManyField(Major)
    objects = models.Manager()

    class Meta:
        ordering = ['login_user']
        verbose_name_plural = 'ตาราง อาจารย์'

    def __str__(self):
        return self.teacher_name
