# analysis_data / urls.py
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.manage, name='manage'),
    url(r'^manage_room/$', views.manage_room, name='manage_room'),
    url(r'^table_room/$', views.table_room, name='table_room'),
    url(r'^upload_csv/$', views.upload_csv, name='upload_csv'),
    url(r'^export_csv/$', views.export_csv, name='export_csv'),
]