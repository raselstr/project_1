from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from project.decorators import menu_access_required, set_submenu_session

from ..models import Rinciansubmenu, Level, Levelsub
from ..forms import RinciansubmenuForm

@set_submenu_session
@menu_access_required('list')
def list_rinciansubmenu(request):
    request.session['next'] = request.get_full_path()
    data = Rinciansubmenu.objects.all().select_related('rinciansubmenu_submenu__submenu_menu')
    form = RinciansubmenuForm()
    context = {
        "judul": "Daftar Rincian Sub Menu", 
        "tombol": "Tambah Rincian Sub Menu",
        "form": form, 
        "datas": data
    }
    return render(request, "rinciansubmenu/rinciansubmenu_list.html", context) 

@set_submenu_session
@menu_access_required('simpan')
def simpan_rinciansubmenu(request):
    request.session['next'] = request.get_full_path()
    data = Rinciansubmenu.objects.all().select_related('rinciansubmenu_submenu__submenu_menu')
    if request.method == "POST":
        form = RinciansubmenuForm(request.POST or None)
        if form.is_valid():
            new_rincian = form.save()
            # Inisialisasi hak akses Levelsub untuk semua level pengguna yang ada
            for level in Level.objects.all():
                Levelsub.objects.get_or_create(
                    levelsub_level=level,
                    levelsub_rinciansubmenu=new_rincian,
                    defaults={'lihat': False, 'simpan': False, 'edit': False, 'hapus': False}
                )
            messages.success(request, 'Rincian Sub Menu berhasil disimpan')
            return redirect('list_rinciansubmenu')
    else:
        form = RinciansubmenuForm()
    context = {
        'form': form,
        'datas': data,
        "judul": "Daftar Rincian Sub Menu",
        "tombol": "Tambah Rincian Sub Menu"
    }
    return render(request, "rinciansubmenu/rinciansubmenu_list.html", context)

@set_submenu_session
@menu_access_required('update')
def update_rinciansubmenu(request, pk):
    request.session['next'] = request.get_full_path()
    data = get_object_or_404(Rinciansubmenu, id=pk)
    if request.method == "POST":
        formupdate = RinciansubmenuForm(request.POST or None, instance=data)
        if formupdate.is_valid():
            formupdate.save()
            messages.success(request, "Rincian Sub Menu berhasil diupdate")
            return redirect("list_rinciansubmenu")
    else:
        formupdate = RinciansubmenuForm(instance=data)

    context = {"form": formupdate, "datas": data, "judul": "Update Rincian Sub Menu"}
    return render(request, "rinciansubmenu/rinciansubmenu_edit.html", context)

@set_submenu_session
@menu_access_required('delete')
def delete_rinciansubmenu(request, pk):
    request.session['next'] = request.get_full_path()
    try:
        data = Rinciansubmenu.objects.get(id=pk)
        data.delete()
        messages.warning(request, "Rincian Sub Menu berhasil dihapus")
    except Rinciansubmenu.DoesNotExist:
        messages.error(request, "Data tidak ditemukan")
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect("list_rinciansubmenu")
