# File: your_app/views.py
from django.shortcuts import render, get_object_or_404,redirect
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib import messages
from ..models import RencDankeljadwal, RencDankel
from ..forms.form_posting import RencDankeljadwalForm
from project.decorators import menu_access_required, set_submenu_session


Model_data = RencDankeljadwal
Form_filter = RencDankeljadwalForm
tag_url = 'posting_list'
template_home = 'dankel_posting/posting_home.html'
template_form = 'dankel_posting/posting_form.html'
template_list = 'dankel_posting/posting_list.html'
# sesitahun = 2024

@set_submenu_session
@menu_access_required('list')    
def list(request):
    data = RencDankeljadwal.objects.all()
        
    context = {
        'judul' : 'Posting Rencana Kegiatan Dana Kelurahan',
        'tombol' : 'Posting',
        'form': data
    }
    return render(request, template_list, context)


@set_submenu_session
@menu_access_required('simpan')
def posting(request):
    rencana = RencDankel.objects.all()
    jadwal = None
    
    if request.method == 'POST':
        form = RencDankeljadwalForm(request.POST or None)
        if form.is_valid():
            jadwal = form.cleaned_data.get('rencdankel_jadwal')  # Ambil nilai dari form
            
            if jadwal is not None:
                for item in rencana:
                    obj, created = Model_data.objects.update_or_create(
                        rencdankel_tahun=item.rencdankel_tahun,
                        rencdankel_dana=item.rencdankel_dana,
                        rencdankel_subopd=item.rencdankel_subopd,
                        rencdankel_sub=item.rencdankel_sub,
                        rencdankel_jadwal=jadwal,
                        defaults={
                            'rencdankel_pagu': item.rencdankel_pagu,
                            'rencdankel_output': item.rencdankel_output,
                            'rencdankel_ket': item.rencdankel_ket,
                        }
                    )
                return redirect(tag_url)
            else:
                print("Field jadwal tidak ada di form.")
        else:
            print("Form tidak valid")
            print(form.errors)  # Tampilkan error form untuk debugging
    else:
        form = RencDankeljadwalForm()
    
    context = {
        'judul': 'Posting Rencana Kegiatan Dana Kelurahan',
        'tombol': 'Posting',
        'form': form
    }
    return render(request, template_form, context)

@set_submenu_session
@menu_access_required('list')    
def home(request):
    request.session['next'] = request.get_full_path()
            
    context = {
        'judul' : 'Posting Kegiatan Dana Kelurahan',
        'tab1'      : 'Posting Kegiatan Tahun Berjalan',
        'tab2'      : 'Posting Kegiatan Sisa Tahun Lalu',
       
    }
    return render(request, template_home, context)
