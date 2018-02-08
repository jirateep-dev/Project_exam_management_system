# core / urls.py
from django.conf.urls import url
from . import views

urlpatterns = [
     url(r'^$', views.scoreproj, name='scoreproj'),
     url(r'^scoreproj/', views.scoreproj, name='scoreproj'),
     url(r'^scoreposter/', views.scoreposter, name='scoreposter'),
     url(r'^update_scoreproj/', views.update_scoreproj, name='update_scoreproj'),
     url(r'^settings/', views.settings, name='settings'),
     url(r'^result_sem1/', views.result_sem1, name='result_sem1'),
     url(r'^detail_score/', views.detail_score, name='detail_score'),
     url(r'^manage_proj/', views.manage_proj, name='manage_proj'),
]