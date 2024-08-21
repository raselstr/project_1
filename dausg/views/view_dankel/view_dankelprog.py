from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from dana.utils import datasubrinc
from project.decorators import menu_access_required, set_submenu_session
from django.http import HttpResponse
from ...resources import DankelProgResource
from tablib import Dataset



from ...models import DankelProg
from ...forms.form_dankel import DankelProgForm

Form_data = DankelProgForm
Nilai_data = DankelProg

@set_submenu_session
@menu_access_required('list')
def export(request):
    mymodel_resource = DankelProgResource()
    dataset = mymodel_resource.export()
    
    # Konversi dataset menjadi file Excel
    excel_data = dataset.export('xlsx')
    
    # Buat respon HTTP dengan file Excel
    response = HttpResponse(excel_data, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="dankelprog.xlsx"'
    return response

@set_submenu_session
@menu_access_required('import')
def upload(request):
    if request.method == 'POST':
        mymodel_resource = DankelProgResource()
        dataset = Dataset()
        new_data = request.FILES['myfile']

        try:
            imported_data = dataset.load(new_data.read(), format='xlsx')
            result = mymodel_resource.import_data(dataset, dry_run=True)  # Test the import

            if not result.has_errors():
                mymodel_resource.import_data(dataset, dry_run=False)  # Actually import now
                return HttpResponse("Upload berhasil!", status=200)
            else:
                return HttpResponse("Terjadi kesalahan saat mengimpor data.", status=400)
        except Exception as e:
            return HttpResponse(f"Error: {e}", status=500)

    return render(request, "dankel/dankelprog/dankelprog_list.html")  # Gantilah dengan nama view yang sesuai


@set_submenu_session
@menu_access_required('list')
def list(request):
    request.session['next'] = request.get_full_path()
    data = (Nilai_data.objects
            .select_related('dankel_dana')
            .prefetch_related('dankelkegs__dankelsubs')
            .all())
    form = Form_data()
    context = {
        "judul": "Daftar Program Dana Kelurahan", 
        "tombol" : "Tambah Program Dana Kelurahan",
        "upload" : "Upload Program Dana Kelurahan",
        "form": form, 
        "datas": data
    }
    return render(request, "dankel/dankelprog/dankelprog_list.html", context) 

@set_submenu_session
@menu_access_required('simpan')
def simpan(request):
    request.session['next'] = request.get_full_path()
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

@set_submenu_session
@menu_access_required('update')
def update(request, pk):
    request.session['next'] = request.get_full_path()
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

@set_submenu_session
@menu_access_required('delete')
def delete(request, pk):
    request.session['next'] = request.get_full_path()
    try:
        data = Nilai_data.objects.get(id=pk)
        data.delete()
        messages.warning(request, "Data Berhasil dihapus")
    except Nilai_data.DoesNotExist:
        messages.error(request,"Dana tidak ditemukan")
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect("list_dankel")


def load(request):
    kwargs = {
        'nama_app'  : 'dana',
        'model_name' : 'Subkegiatan',
        'fieldsmodel' : ['sub_dana'],
        'template_name' : 'load/load_subrinckeg.html',
        'fieldget' : 'dankel_dana',
        
    }
    return datasubrinc(request, **kwargs)

    