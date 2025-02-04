# authapp/views.py
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.contrib import messages
from dashboard.models import Userlevel, Levelsub
from jadwal.models import Jadwal

def login_view(request):
    year = datetime.now().year
    years = list(range(year - 1, year + 1 ))
    
    # try:
    #     tblrencana=RencDankeljadwal.objects.latest('rencdankel_jadwal')
    #     jadwal = tblrencana.rencdankel_jadwal
    # except RencDankeljadwal.DoesNotExist:
    #     jadwal = 1
    
    if request.method == 'POST':
        tahun = request.POST.get('tahun')
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if tahun:
            tahun = tahun.replace('.', '')  # Menghapus titik
            try:
                tahun = int(tahun)
            except ValueError:
                messages.error(request, 'Tahun yang dimasukkan tidak valid.')
                return redirect('login')

        user = authenticate(request, username=username, password=password)
    
        tbljadwal=Jadwal.objects.filter(jadwal_tahun=tahun, jadwal_aktif=True).first()
        if tbljadwal:
            jadwal_id = tbljadwal.id
            jadwal_keterangan = tbljadwal.jadwal_keterangan
        else:
            jadwal_id = 0
            jadwal_keterangan = "Tidak ada jadwal"
        
        if user is not None:
            if user.is_active:
                login(request, user)
                
                # Cek jika user adalah superuser
                if user.is_superuser:
                    # Set session untuk menunjukkan semua menu dan submenu
                    request.session['is_superuser'] = True
                    request.session['jadwal'] = jadwal_id
                    request.session['tahun'] = int(tahun)
                else:
                    # Jika bukan superuser, ambil objek Userlevel
                    try:
                        userlevel = Userlevel.objects.get(user_nama=user)
                        submenu_ids = Levelsub.objects.filter(
                            levelsub_level=userlevel.userlevel
                        ).filter(
                            Q(lihat=True) | Q(simpan=True) | Q(edit=True) | Q(hapus=True)
                        ).values_list('levelsub_submenu__id', flat=True)
                        request.session['is_superuser'] = False
                        request.session['user_nama'] = user.username
                        request.session['subopd'] = userlevel.userlevelopd.sub_nama
                        request.session['idsubopd'] = userlevel.userlevelopd.id
                        request.session['level'] = userlevel.userlevel.level_nama
                        request.session['submenus'] = list(submenu_ids)
                        request.session['jadwal'] = jadwal_id
                        request.session['jadwal_ket'] = jadwal_keterangan
                        request.session['tahun'] = int(tahun)
                        
                    except Userlevel.DoesNotExist:
                        messages.error(request, 'Pengaturan level pengguna tidak ditemukan. Silakan hubungi administrator.')
                        return redirect('login')
                return redirect('dashboard')
            else:
                messages.error(request, 'Akun tidak aktif. Silakan hubungi administrator.')
        else:
            messages.error(request, 'Kombinasi username dan password salah.')
    

    
        
    return render(request, 'authapp/login.html',{'tahun':years})

def logout_view(request):
    logout(request)
    return redirect('login')
