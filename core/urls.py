# core / urls.py
from django.conf.urls import url
from . import views

urlpatterns = [
     url(r'^$', views.scoreproj, name='scoreproj'),
     url(r'^scoreproj/', views.scoreproj, name='scoreproj'),
     url(r'^scoreposter/', views.scoreposter, name='scoreposter'),
     url(r'^update_scoreproj/', views.update_scoreproj, name='update_scoreproj'),
     url(r'^settings/', views.settings, name='settings'),
]