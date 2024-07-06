# File: your_app/views.py
from django.shortcuts import render, get_object_or_404,redirect
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib import messages
from ..models import RencDankel, RencDankelsisa, Subrinc
from ..forms.form_sisa import RencDankelsisaForm

Model_data = RencDankelsisa
Form_data = RencDankelsisaForm
tag_url = 'dankelsisa_list'
template = 'dankel_sisa/dankelsisa_form.html'
template_list = 'dankel_sisa/dankelsisa_list.html'
sesidana = 'dana-kelurahan'
sesitahun = 2024
sesiidopd = 1

def delete(request, pk):
    try:
        data = Model_data.objects.get(id=pk)
        data.delete()
        messages.warning(request, "Data Berhasil dihapus")
    except Model_data.DoesNotExist:
        messages.error(request,"Dana tidak ditemukan")
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect(tag_url)

def update(request, pk):
    data = get_object_or_404(Model_data, id=pk)

    if request.method == 'POST':
        form = Form_data(request.POST or None, instance=data, sesiidopd=sesiidopd, sesidana=sesidana)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil Update')
            return redirect(tag_url)
    else:
        form = Form_data(instance=data, sesiidopd=sesiidopd,sesidana=sesidana)
    context = {
        'form': form,
        'judul': 'Update Rencana Kegiatan Sisa Tahun Lalu',
        'btntombol' : 'Update',
    }
    return render(request, template, context)


def simpan(request):
    if request.method == 'POST':
        form = Form_data(request.POST or None, sesiidopd=sesiidopd, sesidana=sesidana)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil Simpan')
            return redirect(tag_url)  # Ganti dengan URL redirect setelah berhasil
    else:
        form = Form_data(sesiidopd=sesiidopd, sesidana=sesidana)
    context = {
        'form': form,
        'judul': 'Form Rencana Kegiatan Sisa Tahun Lalu',
        'btntombol' : 'Simpan',
    }
    return render(request, template, context)

def list(request):
    try:
        dana = Subrinc.objects.get(subrinc_slug=sesidana)
    except Subrinc.DoesNotExist:
        dana = None

    # Membuat query secara dinamis
    query = Q(rencdankelsisa_tahun=sesitahun) & Q(rencdankelsisa_dana=dana)
    if sesiidopd is not None:
        query &= Q(rencdankelsisa_subopd=sesiidopd)

    data = RencDankelsisa.objects.filter(query)
    context = {
        'judul' : 'Rencana Kegiatan Sisa Tahun Lalu',
        'tombol' : 'Tambah Perencanaan Sisa Tahun Lalu',
        'data' : data,
        # 'datapagu' : total_pagu_nilai,
        # 'datasisa' : total_pagu_sisa,
    }
    return render(request, template_list, context)
