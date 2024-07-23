from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from project.decorators import menu_access_required, set_submenu_session

from ..models import Program
from ..forms import ProgramForm

@set_submenu_session
@menu_access_required('list')
def list_program(request):
    request.session['next'] = request.get_full_path()
    data = Program.objects.all()
    form = ProgramForm()
    context = {
        "judul": "Daftar Jenis program", 
        "tombol" : "Tambah Jenis program",
        "form": form, 
        "datas": data
    }
    return render(request, "program/program_list.html", context) 

@set_submenu_session
@menu_access_required('simpan')
def simpan_program(request):
    request.session['next'] = request.get_full_path()
    data = Program.objects.all()
    if request.method == "POST":
        form = ProgramForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil disimpan')
            return redirect('list_program')
    else:
        form = ProgramForm()
    context = {
        'form'  : form,
        'datas': data
    }
    return render(request, "program/program_list.html", context)

@set_submenu_session
@menu_access_required('update')
def update_program(request, pk):
    request.session['next'] = request.get_full_path()
    data = get_object_or_404(Program, id=pk)
    formupdate = ProgramForm(request.POST or None, instance=data)
    if request.method == "POST":
        if formupdate.is_valid():
            formupdate.save()
            messages.success(request, "Data Berhasil diupdate")
            return redirect("list_program")
    else:
        formupdate = ProgramForm(instance=data)

    context = {"form": formupdate, "datas": data, "judul": "Update program"}
    return render(request, "program/program_edit.html", context)

@set_submenu_session
@menu_access_required('delete')
def delete_program(request, pk):
    request.session['next'] = request.get_full_path()
    try:
        data = Program.objects.get(id=pk)
        data.delete()
        messages.warning(request, "Data Berhasil dihapus")
    except Program.DoesNotExist:
        messages.error(request,"Dana tidak ditemukan")
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect("list_program")
