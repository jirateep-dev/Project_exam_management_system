# core / urls.py
from django.conf.urls import url
from . import views

urlpatterns = [
     url(r'^$', views.home, name='home'),
     url(r'^scoreproj/', views.scoreproj, name='scoreproj'),
     url(r'^scoreposter/', views.scoreposter, name='scoreposter'),
]