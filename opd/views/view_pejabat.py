from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from project.decorators import menu_access_required, set_submenu_session


from ..models import Pejabat
from ..forms import PejabatForm, PejabatFotoForm

Form_data = PejabatForm
Model_data = Pejabat    
lokasitemplate = 'pejabat/pejabat_list.html'
lokasiupdate = 'pejabat/pejabat_edit.html'
tag_url = 'list_pejabat'
FormFoto = PejabatFotoForm

@set_submenu_session
def get_pejabat_foto_form(request):
    pejabat_id = request.GET.get('pejabat_id')
    pejabat = get_object_or_404(Pejabat, id=pejabat_id)
    form = FormFoto()
    return render(request, 'pejabat/form_upload.html', {'form_foto': form, 'pejabat_id': pejabat_id})

@set_submenu_session
@menu_access_required('list')
def upload_foto(request):
    if request.method == 'POST':
        form_foto = FormFoto(request.POST, request.FILES)
        if form_foto.is_valid():
            pejabat_id = request.POST.get('pejabat_id')
            try:
                pejabat = Pejabat.objects.get(id=pejabat_id)
                pejabat.pejabat_foto = form_foto.cleaned_data['pejabat_foto']
                pejabat.save()
                messages.success(request, 'Foto berhasil diupload!')
            except Pejabat.DoesNotExist:
                messages.error(request, 'Pejabat tidak ditemukan!')
            return redirect(tag_url)
    else:
        form_foto = FormFoto()
    
    return render(request, lokasitemplate, {'form_foto': form_foto}) 

@set_submenu_session
@menu_access_required('list')
def list(request):
    request.session['next'] = request.get_full_path()
    idsubopd = request.session.get('idsubopd')
    form_foto = FormFoto(request.POST, request.FILES)
    if idsubopd:
        data = Model_data.objects.filter(pejabat_sub=idsubopd)
    else:
        data = Model_data.objects.all().order_by('-pejabat_sub')
        
    form = Form_data(request.POST or None, idsubopd=idsubopd)
    
    context = {
        "judul": "Daftar Pejabat", 
        "tombol" : "Tambah Data Pejabat",
        "form": form, 
        "datas": data,
        "form_foto" : form_foto
        
    }
    return render(request, lokasitemplate, context) 

@set_submenu_session
@menu_access_required('simpan')
def simpan(request):
    request.session['next'] = request.get_full_path()
    idsubopd = request.session.get('idsubopd')
    if request.method == "POST":
        form = Form_data(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil disimpan')
            return redirect(tag_url)
    else:
        form = Form_data(idsubopd=idsubopd)
    context = {
        'form'  : form,
        'idsubopd':idsubopd
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

    context = {"form": formupdate, "datas": data, "judul": "Update Data Pejabat"}
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


