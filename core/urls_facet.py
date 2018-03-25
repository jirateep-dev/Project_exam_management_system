# analysis_data / urls.py
from django.conf.urls import url
from . import views_facet

urlpatterns = [
    url(r'^$', views_facet.facet, name='facet'),
    url(r'^export_script/', views_facet.export_script, name='export_script'),
    url(r'^import_script/', views_facet.import_script, name='import_script'),
    url(r'^reset_teacher/', views_facet.reset_teacher, name='reset_teacher'),
]