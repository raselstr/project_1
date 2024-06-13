# from django.shortcuts import render, get_object_or_404, redirect
# from django.core.exceptions import ValidationError
# from collections import defaultdict
# from django.contrib import messages

# from . models import Rencana
# from . forms import RencanaForm

# Form_data = RencanaForm
# Model_data = Rencana
# lokasitemplate = 'penerimaan/penerimaan_list.html'
# lokasiupdate = 'penerimaan/penerimaan_edit.html'
# tag_url = 'list_penerimaan'

# def list(request):
    
#     data = Model_data.objects.all()
#     form = Form_data(request.POST or None)
    
#     context = {
#         "judul": "Daftar Penerimaan Dana", 
#         "tombol" : "Tambah Penerimaan",
#         "form": form, 
#         "datas": data,
        
#     }
#     return render(request, lokasitemplate, context) 

# def simpan(request):
#     if request.method == "POST":
#         form = Form_data(request.POST or None)
#         if form.is_valid():
#             try:
#                 form.save()
#                 messages.success(request, 'Data Berhasil disimpan')
#                 return redirect(tag_url)
#             except ValidationError as e:
#                 form.add_error(None, e.message)
#                 messages.error(request, e.message)
#     else:
#         form = Form_data()
#     context = {
#         'form'  : form,
#     }
#     # print(messages.error)
#     return render(request, lokasitemplate, context)

# def update(request, pk):
#     data = get_object_or_404(Model_data, id=pk)
#     formupdate = Form_data(request.POST or None, instance=data)
#     if request.method == "POST":
#         if formupdate.is_valid():
#             formupdate.save()
#             messages.success(request, "Data Berhasil diupdate")
#             return redirect(tag_url)
#     else:
#         formupdate = Form_data(instance=data)

#     context = {"form": formupdate, "datas": data, "judul": "Update Kegiatan"}
#     return render(request, lokasiupdate, context)

# def delete(request, pk):
#     data = Model_data.objects.get(id=pk)
#     data.delete()
#     messages.warning(request, "Data Berhasil dihapus")
#     return redirect(tag_url)


