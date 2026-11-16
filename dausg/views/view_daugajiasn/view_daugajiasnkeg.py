from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from dana.utils import datasubrinc
from project.decorators import menu_access_required, set_submenu_session

from ...models import DauGajiAsnKeg, DauGajiAsnProg
from ...forms.form_daugajiasn import DauGajiAsnKegForm

from django.http import HttpResponse
from ...resources import DauGajiAsnKegResource
from tablib import Dataset

Form_data = DauGajiAsnKegForm
Model_data = DauGajiAsnKeg
Model_induk = DauGajiAsnProg
lokasitemplate = 'daugajiasn/daugajiasnkeg/daugajiasnkeg_list.html'
lokasiupdate = 'daugajiasn/daugajiasnkeg/daugajiasnkeg_edit.html'
tag_url = 'list_daugajiasnkeg'
lokasiload = 'load/load_subrinckeg.html'
resource = DauGajiAsnKegResource

@set_submenu_session
@menu_access_required('list')
def export(request):
    mymodel_resource = resource()
    tahun = request.session.get('tahun')
    
    # Filter data berdasarkan tahun jika tahun ada
    if tahun:
        queryset = Model_data.objects.filter(daugajikeg_prog__daugajiprog_tahun=tahun)
    else:
        queryset = Model_data.objects.all()
        
    dataset = mymodel_resource.export(queryset)
    
    # Konversi dataset menjadi file Excel
    excel_data = dataset.export('xlsx')
    
    # Buat respon HTTP dengan file Excel
    response = HttpResponse(excel_data, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="DAU SG Gaji ASN Kegiatan.xlsx"'
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
def list(request, number):
    request.session['next'] = request.get_full_path()
    
    daugaji_prog = get_object_or_404(Model_induk, id=number)
    data = daugaji_prog.daugajikegs.prefetch_related('daugajisubs').all()
    form = Form_data(request.POST or None, number=number)
    
    context = {
        "judul": "Daftar Kegiatan DAU SG Gaji ASN", 
        'daugaji_prog': daugaji_prog,
        "tombol": "Tambah Kegiatan DAUSG Gaji ASN",
        "form": form, 
        "datas": data,
        "number": number,
    }
    return render(request, lokasitemplate, context)

@set_submenu_session
@menu_access_required('simpan')
def simpan(request, number):
    request.session['next'] = request.get_full_path()
    daugaji_prog = get_object_or_404(Model_induk, id=number)
    data = daugaji_prog.daugajikegs.all()
    form = Form_data(request.POST or None, number=number)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil disimpan')
            return redirect(reverse(tag_url, kwargs={'number': number}))
    else:
        form = Form_data(number=number)
    context = {
        'form': form,
        'datas': data,
        'number': number
    }
    return render(request, lokasitemplate, context)

@set_submenu_session
@menu_access_required('update')
def update(request, number, pk):
    request.session['next'] = request.get_full_path()
    data = get_object_or_404(Model_data, id=pk)
    formupdate = Form_data(request.POST or None, instance=data)
    if request.method == "POST":
        if formupdate.is_valid():
            formupdate.save()
            messages.success(request, "Data Berhasil diupdate")
            return redirect(reverse(tag_url, kwargs={'number': number}))
    else:
        formupdate = Form_data(instance=data)

    context = {"form": formupdate, "datas": data, "judul": "Update Kegiatan DAUSG Gaji ASN", 'number': number}
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
        messages.error(request, "Data tidak ditemukan")
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect(reverse(tag_url, kwargs={'number': number}))
