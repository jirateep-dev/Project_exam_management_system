# analysis_data / urls.py
from django.conf.urls import url
from . import views, view_poster, views_facet

urlpatterns = [
    url(r'^$', views.manage, name='manage'),
    url(r'^generate_poster/$', view_poster.generate_poster, name='generate_poster'),
    url(r'^manage_poster/$', view_poster.manage_poster, name='manage_poster'),
    url(r'^upload_poster/$', view_poster.upload_poster, name='upload_poster'),
    url(r'^export_poster/$', view_poster.export_poster, name='export_poster'),
    url(r'^manage_room/$', views.manage_room, name='manage_room'),
    url(r'^table_room/$', views.table_room, name='table_room'),
    url(r'^upload_csv/$', views.upload_csv, name='upload_csv'),
    url(r'^export_csv/$', views.export_csv, name='export_csv'),
    url(r'^facet/$', views_facet.facet, name='facet'),
    url(r'^export_script/$', views_facet.export_script, name='export_script'),
    url(r'^import_script/$', views_facet.import_script, name='import_script'),
    url(r'^reset_teacher/$', views_facet.reset_teacher, name='reset_teacher'),
]