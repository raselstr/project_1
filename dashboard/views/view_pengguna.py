from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from ..forms import PenggunaForm, PenggunaAktifForm, UbahPasswordForm
from django.contrib import messages
from django.core.exceptions import ValidationError
from project.decorators import menu_access_required, set_submenu_session


@set_submenu_session
@menu_access_required('list')
def list_pengguna(request):
    request.session['next'] = request.get_full_path()
    data = User.objects.all()
    form = PenggunaForm()
    context = {
        "judul": "Daftar Pengguna", 
        "tombol" : "Tambah Pengguna",
        "form": form, 
        "datas": data
    }
    return render(request, "pengguna/pengguna_list.html", context) 

@set_submenu_session
@menu_access_required('simpan')
def simpan_pengguna(request):
    request.session['next'] = request.get_full_path()
    data = User.objects.all()
    if request.method == "POST":
        form = PenggunaForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil disimpan')
            return redirect('list_pengguna')
    else:
        form = PenggunaForm()
    context = {
        'form'  : form,
        'datas': data
    }
    return render(request, "pengguna/pengguna_list.html", context)

@set_submenu_session
@menu_access_required('update')
def update_pengguna(request, pk):
    request.session['next'] = request.get_full_path()
    data = get_object_or_404(User, id=pk)
    if request.method == "POST":
        formupdate = PenggunaAktifForm(request.POST or None, instance=data)
        if formupdate.is_valid():
            formupdate.save()
            messages.success(request, "Data Berhasil diupdate")
            return redirect("list_pengguna")
    else:
        formupdate = PenggunaAktifForm(instance=data)

    context = {"form": formupdate, "datas": data, "judul": "Update Pengguna"}
    return render(request, "pengguna/pengguna_edit.html", context)

@set_submenu_session
@menu_access_required('update')
def ubah_password(request, pk):
    request.session['next'] = request.get_full_path()
    user = User.objects.get(pk=pk)
    
    if request.method == 'POST':
        password_form = UbahPasswordForm(request.POST)
        
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
        
        return redirect('list_pengguna')
    else:
        password_form = UbahPasswordForm(request.user)
    return render(request, 'pengguna/pengguna_password.html', {'form': password_form})

@set_submenu_session
@menu_access_required('delete')
def delete_pengguna(request, pk):
    request.session['next'] = request.get_full_path()
    try:
        data = User.objects.get(id=pk)
        data.delete()
        messages.warning(request, "Data Berhasil dihapus")
    except User.DoesNotExist:
        messages.error(request,"Dana tidak ditemukan")
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect("list_pengguna")
