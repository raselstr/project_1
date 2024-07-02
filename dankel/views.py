# File: your_app/views.py
from django.shortcuts import render, get_object_or_404,redirect
from django.core.exceptions import ValidationError
from django.contrib import messages
from .models import RencDankel, RencDankelsisa, Subrinc
from .forms import RencDankelForm

Model_data = RencDankel
Form_data = RencDankelForm
tag_url = 'rencdankel_list'
template = 'dankel/dankel_form.html'
template_list = 'dankel/dankel_list.html'
template_home = 'dankel/dankel_home.html'
# sesidana = 'Dana Kelurahan'
# sesitahun = 2024
# sesiidopd = 1

# def delete(request, pk):
#     try:
#         data = Model_data.objects.get(id=pk)
#         data.delete()
#         messages.warning(request, "Data Berhasil dihapus")
#     except Model_data.DoesNotExist:
#         messages.error(request,"Dana tidak ditemukan")
#     except ValidationError as e:
#         messages.error(request, str(e))
#     return redirect(tag_url)

# def update(request, pk):
#     # Mendapatkan instance RencDankel yang ingin diupdate
#     rencdankel = get_object_or_404(Model_data, pk=pk)

#     if request.method == 'POST':
#         # Membuat instance formulir dengan data yang dikirimkan
#         form = Form_data(request.POST, instance=rencdankel)
#         formset = RencDankelsisaFormSet(request.POST, instance=rencdankel)
#         if form.is_valid() and formset.is_valid():
#             # Menyimpan perubahan pada objek RencDankel
#             rencdankel = form.save()
#             messages.success(request, 'Data Berhasil Update')

#             # Menyimpan perubahan pada setiap objek RencDankelsisa yang terkait
#             instances = formset.save(commit=False)
#             for instance in instances:
#                 instance.rencdankelsisa_rencana = rencdankel
#                 instance.save()

#             return redirect(tag_url)  # Ganti dengan URL redirect setelah berhasil
#     else:
#         # Menyiapkan formulir dan formset dengan data yang sudah ada
#         form = Form_data(instance=rencdankel)
#         formset = RencDankelsisaFormSet(instance=rencdankel)
    
#     context = {
#         'form': form,
#         'formset': formset,
#         'judul': 'Update Rencana Kegiatan',
#         'btntombol' : 'Update',
#     }
#     return render(request, template, context)


# def simpan(request):
    
#     if request.method == 'POST':
#         form = Form_data(request.POST)
#         formset = RencDankelsisaFormSet(request.POST)
#         if form.is_valid() and formset.is_valid():
#             rencdankel = form.save()
#             instances = formset.save(commit=False)
#             for instance in instances:
#                 instance.rencdankelsisa_rencana = rencdankel
#                 instance.save()
#             messages.success(request, 'Data Berhasil Simpan')
#             return redirect(tag_url)  # Ganti dengan URL redirect setelah berhasil
#     else:
#         form = Form_data()
#         formset = RencDankelsisaFormSet()
    
#     context = {
#         'form': form,
#         'formset': formset,
#         'judul': 'Form Rencana Kegiatan',
#         'btntombol' : 'Simpan',
        
#     }
#     return render(request, template, context)

def home(request):
    
    sesidana = 'dana-kelurahan'
    sesitahun = 2024
    sesiidopd = None
    data = Model_data.objects.all()
    try:
        dana = Subrinc.objects.get(subrinc_slug=sesidana)
    except Subrinc.DoesNotExist:
        dana = None
        
    if dana:
        total_pagu_nilai = RencDankel().get_pagudausg(tahun=sesitahun, opd=sesiidopd, dana=dana)
    else:
        total_pagu_nilai = None
        
    if dana:
        total_pagu_sisa = RencDankelsisa().get_sisapagudausg(tahun=sesitahun, opd=sesiidopd, dana=dana)
    else:
        total_pagu_sisa = None
        
    context = {
        'judul' : 'Rencana Kegiatan',
        'tombol' : 'Tambah Perencanaan',
        'data' : data,
        'datapagu' : total_pagu_nilai,
        'datasisa' : total_pagu_sisa,
        
    }
    return render(request, template_home, context)
