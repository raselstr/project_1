from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from dana.utils import datasubrinc
from project.decorators import menu_access_required, set_submenu_session

from django.http import HttpResponse
from ...resources import DausgpendidikanProgResource
from tablib import Dataset


from ...models import DausgpendidikanProg
from ...forms.form_dausgpendidikan import DausgpendidikanProgForm

Form_data = DausgpendidikanProgForm
Nilai_data = DausgpendidikanProg
tag_url = 'list_dausgpendidikanprog'
template_list = 'dausgpendidikan/dausgpendidikanprog/dausgpendidikanprog_list.html'


@set_submenu_session
@menu_access_required('list')
def export(request):
    mymodel_resource = DausgpendidikanProgResource()
    tahun = request.session.get('tahun')
    
    # Filter data berdasarkan tahun jika tahun ada
    if tahun:
        queryset = Nilai_data.objects.filter(dausgpendidikan_tahun=tahun)
    else:
        queryset = Nilai_data.objects.all()
    
    dataset = mymodel_resource.export(queryset)
    
    # Konversi dataset menjadi file Excel
    excel_data = dataset.export('xlsx')
    
    # Buat respon HTTP dengan file Excel
    response = HttpResponse(excel_data, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="DAU SG Pendidikan Program.xlsx"'
    return response

@set_submenu_session
@menu_access_required('list')
def upload(request):
    if request.method == 'POST':
        mymodel_resource = DausgpendidikanProgResource()
        dataset = Dataset()
        new_data = request.FILES.get('myfile')

        if not new_data:
            messages.error(request, 'File tidak ditemukan. Silakan pilih file.')
            return redirect(tag_url)

        try:
            # Load data dari file Excel
            imported_data = dataset.load(new_data.read(), format='xlsx')
            
            # Coba import data secara dry run (tanpa menyimpan ke database)
            result = mymodel_resource.import_data(imported_data, dry_run=True)

            # Jika ada error saat import, tampilkan pesan error
            if result.has_errors():
                error_messages = "; ".join([str(error) for row in result.row_errors() for error in row[1]])
                messages.error(request, f'Terjadi kesalahan saat mengimpor data: {error_messages}')
                return redirect(tag_url)
            else:
                # Jika tidak ada error, simpan data ke database
                mymodel_resource.import_data(imported_data, dry_run=False)
                messages.success(request, 'Upload berhasil!')
                return redirect(tag_url)
        except Exception as e:
            # Tangkap dan tampilkan exception lainnya
            messages.error(request, f"Error: {e}")
            return redirect(tag_url)

    return render(request, template_list)





@set_submenu_session
@menu_access_required('list')
def list(request):
    request.session['next'] = request.get_full_path()
    tahun = request.session.get('tahun')
    data = (Nilai_data.objects
            .select_related('dausgpendidikan_dana')
            .prefetch_related('dausgpendidikankegs__dausgpendidikansubs')
            .filter(dausgpendidikan_tahun=tahun) if tahun else Nilai_data.objects
            .select_related('dausgpendidikan_dana')
            .prefetch_related('dausgpendidikankegs__dausgpendidikansubs')
            .all())
    form = Form_data()
    context = {
        "judul": "Daftar Program DAU SG Pendidikan", 
        "tombol" : "Tambah Program DAUSG Pendidikan",
        "form": form, 
        "datas": data
    }
    return render(request, "dausgpendidikan/dausgpendidikanprog/dausgpendidikanprog_list.html", context) 

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
            return redirect(tag_url)
    else:
        form = Form_data()
    context = {
        'form'  : form,
        'datas': data
    }
    return render(request, "dausgpendidikan/dausgpendidikanprog/dausgpendidikanprog_list.html", context)

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
            return redirect(tag_url)
    else:
        formupdate = Form_data(instance=data)

    context = {"form": formupdate, "datas": data, "judul": "Update dausgpendidikanprog"}
    return render(request, "dausgpendidikan/dausgpendidikanprog/dausgpendidikanprog_edit.html", context)

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
    return redirect(tag_url)

def load(request):
    kwargs = {
        'nama_app'  : 'dana',
        'model_name' : 'Subkegiatan',
        'fieldsmodel' : ['sub_dana'],
        'template_name' : 'load/load_subrinckeg.html',
        'fieldget' : 'dausgpendidikan_dana',
        
    }
    return datasubrinc(request, **kwargs)

    