from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from project.decorators import menu_access_required, set_submenu_session
from django.http import HttpResponse
from tablib import Dataset

from dausg.resources import PaguResource


from .models import Pagudausg
from .forms import PagudausgForm

Form_data = PagudausgForm
Model_data = Pagudausg
lokasitemplate = 'pagu/pagu_list.html'
lokasiupdate = 'pagu/pagu_edit.html'
tag_url = 'list_pagudausg'

resource = PaguResource

@set_submenu_session
@menu_access_required('list')
def export(request):
    mymodel_resource = resource()
    dataset = mymodel_resource.export()
    
    # Konversi dataset menjadi file Excel
    excel_data = dataset.export('xlsx')
    
    # Buat respon HTTP dengan file Excel
    response = HttpResponse(excel_data, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="pagu.xlsx"'
    return response

@set_submenu_session
@menu_access_required('update')
def upload(request):
    if request.method == 'POST':
        mymodel_resource = resource()
        dataset = Dataset()
        new_data = request.FILES.get('myfile')

        if not new_data:
            messages.error(request, 'File tidak ditemukan. Silakan pilih file')
            return redirect(tag_url)

        try:
            imported_data = dataset.load(new_data.read(), format='xlsx')
            if not imported_data.headers:
                messages.error(request, 'File tidak memiliki header atau struktur yang salah.')
                return redirect(tag_url)

            result = mymodel_resource.import_data(dataset, dry_run=True)  # Test the import
            if result.has_errors():
                error_messages = []
                for row_errors in result.row_errors():
                    row, errors = row_errors
                    error_messages.append(f"Kesalahan di baris {row}: {', '.join([str(e.error) for e in errors])}")
                
                messages.error(request, f"Terjadi kesalahan saat mengimpor data: {'; '.join(error_messages)}")
                return redirect(tag_url)
            else:
                mymodel_resource.import_data(dataset, dry_run=False)  # Actually import now
                messages.success(request, 'Upload berhasil!')
                return redirect(tag_url)
        except Exception as e:
            messages.error(request, f"Error: {e}")
            return redirect(tag_url)

    return render(request, lokasitemplate)


@set_submenu_session
@menu_access_required('list')
def list(request):
    request.session['next'] = request.get_full_path()
    tahun = request.session.get('tahun')
    total_dana = Pagudausg().total_nilai_by_dana(tahun=tahun)
    idopd = request.session.get('idsubopd')
    
    if idopd is not None and idopd != 125 and idopd != 67 :
        data = Model_data.objects.filter(pagudausg_opd=idopd, pagudausg_tahun=tahun).order_by('pagudausg_dana')
    else:
        data = Model_data.objects.filter(pagudausg_tahun=tahun).order_by('pagudausg_dana')
    form = Form_data(request.POST or None)
    context = {
        "judul": "Daftar Pagu TKDD", 
        "tombol" : "Tambah Pagu TKDD",
        "datas": data,
        'form': form,
        'total_dana' : total_dana,
    }
    return render(request, lokasitemplate, context) 

@set_submenu_session
@menu_access_required('simpan')
def simpan(request):
    request.session['next'] = request.get_full_path()
    if request.method == "POST":
        form = Form_data(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil disimpan')
            return redirect(tag_url)
    else:
        form = Form_data()
    context = {
        'form'  : form,
    }
    return render(request, lokasitemplate, context)

@set_submenu_session
@menu_access_required('update')
def update(request, pk):
    request.session['next'] = request.get_full_path()
    data = get_object_or_404(Model_data, id=pk)
    formupdate = Form_data(request.POST or None, instance=data)
    if request.method == "POST":
        if formupdate.is_valid():
            formupdate.save()
            messages.success(request, "Data Berhasil diupdate")
            return redirect(tag_url)
    else:
        formupdate = Form_data(instance=data)

    context = {"form": formupdate, "datas": data,"judul": "Update Pagu"}
    return render(request, lokasiupdate, context)

@set_submenu_session
@menu_access_required('delete')
def delete(request, pk):
    request.session['next'] = request.get_full_path()
    try:
        data = Model_data.objects.get(id=pk)
        data.delete()
        messages.warning(request, "Data Berhasil dihapus")
    except Model_data.DoesNotExist:
        messages.error(request,"Dana tidak ditemukan")
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect(tag_url)


