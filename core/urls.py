# core / urls.py
from django.conf.urls import url, include
from . import views, views_facet

urlpatterns = [
    url(r'^$', views.scoreproj, name='scoreproj'),
    url(r'^scoreproj/', views.scoreproj, name='scoreproj'),
    url(r'^scoreposter/', views.scoreposter, name='scoreposter'),
    url(r'^update_scoreproj/', views.update_scoreproj, name='update_scoreproj'),
    url(r'^settings/', views.settings, name='settings'),
    url(r'^result_sem1/', views.result_sem1, name='result_sem1'),
    url(r'^detail_score/', views.detail_score, name='detail_score'),
    url(r'^manage_proj/', views.manage_proj, name='manage_proj'),
    url(r'^facet/', views_facet.facet, name='facet'),
    url(r'^export_script/', views_facet.export_script, name='export_script'),
    url(r'^import_script/', views_facet.import_script, name='import_script'),
    url(r'^reset_teacher/', views_facet.reset_teacher, name='reset_teacher'),
    url(r'^upload_projs/', views.upload_projs, name='upload_projs'),
]