from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.models import User
from ..forms import PenggunaForm
from django.contrib import messages
from django.core.exceptions import ValidationError


def list_pengguna(request):
    data = User.objects.all()
    form = PenggunaForm()
    context = {
        "judul": "Daftar Pengguna", 
        "tombol" : "Tambah Pengguna",
        "form": form, 
        "datas": data
    }
    return render(request, "pengguna/pengguna_list.html", context) 

# def simpan_pengguna(request):
#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect('dashboard')
#     else:
#         form = CustomUserCreationForm()
#     return render(request, 'register.html', {'form': form})

def simpan_pengguna(request):
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

def update_pengguna(request, pk):
    data = get_object_or_404(User, id=pk)
    formupdate = PenggunaForm(request.POST or None, instance=data)
    if request.method == "POST":
        if formupdate.is_valid():
            formupdate.save()
            messages.success(request, "Data Berhasil diupdate")
            return redirect("list_pengguna")
    else:
        formupdate = PenggunaForm(instance=data)

    context = {"form": formupdate, "datas": data, "judul": "Update Pengguna"}
    return render(request, "pengguna/pengguna_edit.html", context)

def delete_pengguna(request, pk):
    try:
        data = User.objects.get(id=pk)
        data.delete()
        messages.warning(request, "Data Berhasil dihapus")
    except User.DoesNotExist:
        messages.error(request,"Dana tidak ditemukan")
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect("list_pengguna")
