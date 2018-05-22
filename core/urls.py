# core / urls.py
from django.conf.urls import url, include
from . import views, manage_score
from database_management.models import *

urlpatterns = [
    url(r'^$', views.scoreproj, name='scoreproj'),
    url(r'^scoreproj/', views.scoreproj, name='scoreproj'),
    url(r'^scoreposter/', views.scoreposter, name='scoreposter'),
    url(r'^update_scoreproj/', views.update_scoreproj, name='update_scoreproj'),
    url(r'^settings/', views.settings, name='settings'),
    url(r'^result_sem1/', views.result_sem1, name='result_sem1'),
    url(r'^detail_score/', views.detail_score, name='detail_score'),
    url(r'^manage_proj/', views.manage_proj, name='manage_proj'),
    url(r'^export_forms/', manage_score.export_forms, name='export_forms'),
    url(r'^import_score/', manage_score.import_score, name='import_score'),
    url(r'^reset_score/', manage_score.reset_score, name='reset_score'),
    url(r'^upload_projs/', views.upload_projs, name='upload_projs'),
]