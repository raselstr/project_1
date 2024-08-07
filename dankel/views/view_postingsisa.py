# File: your_app/views.py
from django.shortcuts import render, get_object_or_404,redirect
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib import messages
from ..models import RencDankeljadwalsisa, RencDankelsisa
from ..forms.form_postingsisa import RencDankeljadwalsisaForm
from project.decorators import menu_access_required, set_submenu_session


Model_data = RencDankeljadwalsisa
Model_induk = RencDankelsisa
Form_filter = RencDankeljadwalsisaForm
tag_url = 'postingsisa_list'
template_form = 'dankel_postingsisa/postingsisa_form.html'
template_list = 'dankel_postingsisa/postingsisa_list.html'
# sesitahun = 2024

@set_submenu_session
@menu_access_required('list')    
def list(request):
    data = Model_data.objects.all()
        
    context = {
        'judul' : 'Posting Rencana Kegiatan Dana Kelurahan',
        'tombol' : 'Posting',
        'form': data
    }
    return render(request, template_list, context)


@set_submenu_session
@menu_access_required('simpan')
def posting(request):
    rencana = Model_induk.objects.all()
    jadwal = None
    
    if request.method == 'POST':
        form = RencDankeljadwalsisaForm(request.POST or None)
        if form.is_valid():
            jadwal = form.cleaned_data.get('rencdankelsisa_jadwal')  # Ambil nilai dari form
            
            if jadwal is not None:
                for item in rencana:
                    obj, created = Model_data.objects.update_or_create(
                        rencdankelsisa_tahun=item.rencdankelsisa_tahun,
                        rencdankelsisa_dana=item.rencdankelsisa_dana,
                        rencdankelsisa_subopd=item.rencdankelsisa_subopd,
                        rencdankelsisa_sub=item.rencdankelsisa_sub,
                        rencdankelsisa_jadwal=jadwal,
                        defaults={
                            'rencdankelsisa_pagu': item.rencdankelsisa_pagu,
                            'rencdankelsisa_output': item.rencdankelsisa_output,
                            'rencdankelsisa_ket': item.rencdankelsisa_ket,
                        }
                    )
                return redirect(tag_url)
            else:
                print("Field jadwal tidak ada di form.")
        else:
            print("Form tidak valid")
            print(form.errors)  # Tampilkan error form untuk debugging
    else:
        form = Form_filter()
    
    context = {
        'judul': 'Posting Rencana Kegiatan Dana Kelurahan',
        'tombol': 'Posting',
        'form': form
    }
    return render(request, template_form, context)


