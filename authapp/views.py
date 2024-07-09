# authapp/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # request.session['user_level'] = user.userlevel.userlevel.level_nama
            return redirect('dashboard')  # Ubah 'home' sesuai dengan nama rute Anda
        else:
            return render(request, 'authapp/login.html', {'error': 'Invalid credentials'})
    else:
        return render(request, 'authapp/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')
