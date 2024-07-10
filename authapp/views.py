# authapp/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from dashboard.models import Userlevel

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                
                # Check if the user is superuser
                if user.is_superuser:
                    # If superuser, set session to show all menus and submenus
                    request.session['is_superuser'] = True
                else:
                    # If not superuser, fetch the Userlevel object
                    try:
                        userlevel = Userlevel.objects.get(user_nama=user)
                        request.session['is_superuser'] = False
                        request.session['user_nama'] = user.username
                        request.session['subopd'] = userlevel.userlevelopd.sub_nama
                        request.session['level'] = userlevel.userlevel.level_nama
                        request.session['submenus'] = list(userlevel.userlevel.level_submenu.values_list('id', flat=True))
                    except Userlevel.DoesNotExist:
                        messages.error(request, 'Pengaturan level pengguna tidak ditemukan. Silakan hubungi administrator.')
                        return redirect('login')
                
                return redirect('dashboard')
            else:
                messages.error(request, 'Akun tidak aktif. Silakan hubungi administrator.')
        else:
            messages.error(request, 'Kombinasi username dan password salah.')
        
    return render(request, 'authapp/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')
