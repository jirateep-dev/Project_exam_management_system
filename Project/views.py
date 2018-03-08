from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login
from django.template import RequestContext
from ldap3 import Server, Connection, ALL
from django.shortcuts import render
from django.contrib.auth.models import User

def login_user(request):
    state = ""
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        # user = authenticate(username=username, password=password)
        user = User.objects.get(username=username)

        s = Server('ldap://161.246.38.141', get_info=ALL, use_ssl=True) 
        c = Connection(s, user=username+"@it.kmitl.ac.th", password=password)
        
        if user is not None and c.bind():
        # if c.bind():
            login(request, user)
            state = "Valid account"
            return render(request, 'scoreproj.html')
        else:
            state = "Inactive account"
    return render(request, 'login.html')