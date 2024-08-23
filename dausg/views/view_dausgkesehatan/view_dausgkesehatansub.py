from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from dana.utils import datasubrinc
from project.decorators import menu_access_required, set_submenu_session


from ...models import DausgkesehatanKeg,DausgkesehatanSub
from ...forms.form_dausgkesehatan import DausgkesehatanSubForm

from django.http import HttpResponse
from ...resources import DausgkesehatanSubResource
from tablib import Dataset

Form_data = DausgkesehatanSubForm
Model_data = DausgkesehatanSub
Model_induk = DausgkesehatanKeg
lokasitemplate = 'dausgkesehatan/dausgkesehatansub/dausgkesehatansub_list.html'
lokasiupdate = 'dausgkesehatan/dausgkesehatansub/dausgkesehatansub_edit.html'
tag_url = 'list_dausgkesehatansub'

resource = DausgkesehatanSubResource

@set_submenu_session
@menu_access_required('list')
def export(request):
    mymodel_resource = resource()
    dataset = mymodel_resource.export()
    
    # Konversi dataset menjadi file Excel
    excel_data = dataset.export('xlsx')
    
    # Buat respon HTTP dengan file Excel
    response = HttpResponse(excel_data, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="DAU SG Kesehatan Sub Kegiatan.xlsx"'
    return response

@set_submenu_session
@menu_access_required('list')
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
def list(request, number, sub):
    request.session['next'] = request.get_full_path()
    
    dausgkesehatan_keg = get_object_or_404(Model_induk, id=sub)
    data = dausgkesehatan_keg.dausgkesehatansubs.all()
    # data = Model_data.objects.all()
    form = Form_data(request.POST or None, sub=sub)
    
    context = {
        "judul": "Daftar Sub Kegiatan DAU SG kesehatan", 
        'dausgkesehatan_keg': dausgkesehatan_keg,
        "tombol" : "Tambah Sub Kegiatan DAUSG kesehatan",
        "form": form, 
        "datas": data,
        "number":number,
        "sub":sub,
        
    }
    return render(request, lokasitemplate, context) 

@set_submenu_session
@menu_access_required('simpan')
def simpan(request, number, sub):
    request.session['next'] = request.get_full_path()
    if request.method == "POST":
        form = Form_data(request.POST or None,  sub=sub)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil disimpan')
            return redirect(tag_url, number=number, sub=sub)
    else:
        form = Form_data(sub=sub)
    context = {
        'form'  : form,
        'sub':sub,
    }
    return render(request, lokasitemplate, context)

@set_submenu_session
@menu_access_required('update')
def update(request, number, sub, pk):
    request.session['next'] = request.get_full_path()
    data = get_object_or_404(Model_data, id=pk)
    formupdate = Form_data(request.POST or None, instance=data)
    if request.method == "POST":
        if formupdate.is_valid():
            formupdate.save()
            messages.success(request, "Data Berhasil diupdate")
            return redirect(tag_url, number=number, sub=sub)
    else:
        formupdate = Form_data(instance=data)

    context = {"form": formupdate, "datas": data, "number": number, "sub": sub, "judul": "Update Kegiatan"}
    return render(request, lokasiupdate, context)

@set_submenu_session
@menu_access_required('delete')
def delete(request, number, sub, pk):
    request.session['next'] = request.get_full_path()
    try:
        data = Model_data.objects.get(id=pk)
        data.delete()
        messages.warning(request, "Data Berhasil dihapus")
    except Model_data.DoesNotExist:
        messages.error(request,"Dana tidak ditemukan")
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect(tag_url, number=number, sub=sub)


