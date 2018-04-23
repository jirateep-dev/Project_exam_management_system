from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse,  HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from .forms import *
import csv, codecs
import datetime
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from django.db import connection
from database_management import callsql
from database_management.models import *
from django.db.models import Q
from random import randint
from collections import Counter
from django.db.models import Max
from random import randint
import statistics
import logging

def this_year():
    return Project.objects.all().aggregate(Max('proj_years'))['proj_years__max']

def lastname_tch(tch_name):
    split_name = tch_name.split(' ')
    last_name = split_name[len(split_name)-1]
    return last_name

def manage_poster(request):
    sem = Settings.objects.get(id=1).forms
    re_post = request.POST.get('re_post',None)
    gen_post = request.POST.get('gen_post',None)

    # if re_post:
    
    # if gen_post:

    return render(request,"poster.html", {'proj_act':sem})