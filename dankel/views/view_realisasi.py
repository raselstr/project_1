# File: your_app/views.py
from django.shortcuts import render, get_object_or_404,redirect
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib import messages
from ..models import RealisasiDankel, RencDankelsisa, Subrinc
from ..forms.form_realisasi import RealisasiDankelFilterForm

# Model_data = RealisasiDankel
# Form_data = RealisasiDankelForm
# tag_url = 'dankelsisa_list'
# template = 'dankel_sisa/dankelsisa_form.html'
template_list = 'dankel_realisasi/realisasidankel_home.html'
# sesidana = 'dana-kelurahan'
# sesitahun = 2024
# sesiidopd = None

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
#     data = get_object_or_404(Model_data, id=pk)

#     if request.method == 'POST':
#         form = Form_data(request.POST or None, instance=data, sesiidopd=sesiidopd, sesidana=sesidana)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Data Berhasil Update')
#             return redirect(tag_url)
#     else:
#         form = Form_data(instance=data, sesiidopd=sesiidopd,sesidana=sesidana)
#     context = {
#         'form': form,
#         'judul': 'Update Rencana Kegiatan Sisa Tahun Lalu',
#         'btntombol' : 'Update',
#     }
#     return render(request, template, context)


# def simpan(request):
#     if request.method == 'POST':
#         form = Form_data(request.POST or None, sesiidopd=sesiidopd, sesidana=sesidana)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Data Berhasil Simpan')
#             return redirect(tag_url)  # Ganti dengan URL redirect setelah berhasil
#     else:
#         form = Form_data(sesiidopd=sesiidopd, sesidana=sesidana)
#     context = {
#         'form': form,
#         'judul': 'Form Rencana Kegiatan Sisa Tahun Lalu',
#         'btntombol' : 'Simpan',
#     }
#     return render(request, template, context)

def filter(request):
    if request.method == 'GET':
        form = RealisasiDankelFilterForm(request.GET)
        if form.is_valid():
            # Simpan data filter di sesi
            request.session['realisasidankel_tahun'] = form.cleaned_data.get('realisasidankel_tahun')
            request.session['realisasidankel_dana'] = form.cleaned_data.get('realisasidankel_dana').id if form.cleaned_data.get('realisasidankel_dana') else None
            request.session['realisasidankel_tahap'] = form.cleaned_data.get('realisasidankel_tahap').id if form.cleaned_data.get('realisasidankel_tahap') else None
            request.session['realisasidankel_subopd'] = form.cleaned_data.get('realisasidankel_subopd').id if form.cleaned_data.get('realisasidankel_subopd') else None
            
            return redirect('create_realisasi_dankel')
    else:
        form = RealisasiDankelFilterForm()
    
    context = {
        'judul' : 'Realisasi Tahun Berjalan',
        'tombol' : 'Tambah Perencanaan Sisa Tahun Lalu',
        'form': form
        # 'datasisa' : total_pagu_sisa,
    }
    return render(request, template_list, context)
