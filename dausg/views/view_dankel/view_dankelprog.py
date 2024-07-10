from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from dana.utils import datasubrinc
from project.decorators import menu_access_required   


from ...models import DankelProg
from ...forms.form_dankel import DankelProgForm

Form_data = DankelProgForm
Nilai_data = DankelProg

@menu_access_required
def list(request):
    data = (Nilai_data.objects
            .select_related('dankel_dana', 'dankel_subrinc')
            .prefetch_related('dankelkegs__dankelsubs')
            .all())
    form = Form_data()
    context = {
        "judul": "Daftar Program Dana Kelurahan", 
        "tombol" : "Tambah Program Dana Kelurahan",
        "form": form, 
        "datas": data
    }
    return render(request, "dankel/dankelprog/dankelprog_list.html", context) 

@menu_access_required
def simpan(request):
    data = Nilai_data.objects.all()
    if request.method == "POST":
        form = Form_data(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil disimpan')
            return redirect('list_dankel')
    else:
        form = Form_data()
    context = {
        'form'  : form,
        'datas': data
    }
    return render(request, "dankel/dankelprog/dankelprog_list.html", context)

@menu_access_required
def update(request, pk):
    data = get_object_or_404(Nilai_data, id=pk)
    formupdate = Form_data(request.POST or None, instance=data)
    if request.method == "POST":
        if formupdate.is_valid():
            formupdate.save()
            messages.success(request, "Data Berhasil diupdate")
            return redirect("list_dankel")
    else:
        formupdate = Form_data(instance=data)

    context = {"form": formupdate, "datas": data, "judul": "Update dankelprog"}
    return render(request, "dankel/dankelprog/dankelprog_edit.html", context)

@menu_access_required
def delete(request, pk):
    try:
        data = Nilai_data.objects.get(id=pk)
        data.delete()
        messages.warning(request, "Data Berhasil dihapus")
    except Nilai_data.DoesNotExist:
        messages.error(request,"Dana tidak ditemukan")
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect("list_dankel")

@menu_access_required
def load(request):
    kwargs = {
        'nama_app'  : 'dana',
        'model_name' : 'Subrinc',
        'fieldsmodel' : ['subrinc_dana'],
        'template_name' : 'load/load_subrinckeg.html',
        'fieldget' : 'dankel_dana',
        
    }
    return datasubrinc(request, **kwargs)

    