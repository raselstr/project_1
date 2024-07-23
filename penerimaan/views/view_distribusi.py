from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ValidationError
from collections import defaultdict
from django.contrib import messages
from project.decorators import menu_access_required, set_submenu_session

from .. models import DistribusiPenerimaan
from .. forms import DistribusiForm

Form_data = DistribusiForm
Model_data = DistribusiPenerimaan
lokasitemplate = 'distribusi/distribusi_list.html'
lokasiupdate = 'distribusi/distribusi_form.html'
tag_url = 'list_distribusi'

@set_submenu_session
@menu_access_required('list')
def list(request, number):
    request.session['next'] = request.get_full_path()
    data = Model_data.objects.filter(distri_penerimaan=number).order_by('distri_penerimaan')
    context = {
        'judul': 'Daftar Distribusi Penerimaan Dana', 
        'tombol' : 'Tambah Distribusi Dana',
        'datas': data,
        'number': number
    }
    return render(request, lokasitemplate, context) 

@set_submenu_session
@menu_access_required('simpan')
def simpan(request, number):
    request.session['next'] = request.get_full_path()
    if request.method == "POST":
        form = Form_data(request.POST or None, number=number)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Data Berhasil disimpan')
                return redirect(tag_url, number=number)
            except ValidationError as e:
                form.add_error(None, e.message)
                messages.error(request, e.message)
    else:
        form = Form_data(number=number)
    context = {
        'form'  : form,
        'tombol' : 'Simpan',
        'number' : number
    }
    # print(messages.error)
    return render(request, lokasiupdate, context)

@set_submenu_session
@menu_access_required('update')
def update(request, number, pk):
    request.session['next'] = request.get_full_path()
    data = get_object_or_404(Model_data, id=pk)
    formupdate = Form_data(request.POST or None, instance=data, number=number)
    if request.method == "POST":
        if formupdate.is_valid():
            formupdate.save()
            messages.success(request, "Data Berhasil diupdate")
            return redirect(tag_url, number=number)
    else:
        formupdate = Form_data(instance=data, number=number)

    context = {"form": formupdate, "datas": data, "judul": "Update Kegiatan", 'number':number,'tombol':'Update Data'}
    return render(request, lokasiupdate, context)

@set_submenu_session
@menu_access_required('delete')
def delete(request, number, pk):
    request.session['next'] = request.get_full_path()
    try:
        data = Model_data.objects.get(id=pk)
        data.delete()
        messages.warning(request, "Data Berhasil dihapus")
    except Model_data.DoesNotExist:
        messages.error(request,"Dana tidak ditemukan")
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect(tag_url, number=number)


