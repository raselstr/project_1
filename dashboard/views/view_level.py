from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from project.decorators import menu_access_required, set_submenu_session

from ..models import Level, Submenu, Levelsub, Userlevel
from ..forms import LevelForm

@set_submenu_session
@menu_access_required('list')
def list_level(request):
    request.session['next'] = request.get_full_path()
    data = Level.objects.annotate(
        total_users=Count('userlevel', distinct=True),
        active_subs=Count(
            'levelsub',
            filter=Q(levelsub__lihat=True) | Q(levelsub__simpan=True) | Q(levelsub__edit=True) | Q(levelsub__hapus=True),
            distinct=True
        )
    ).order_by('id')
    total_submenus = Submenu.objects.count()
    total_users = Userlevel.objects.count()
    form = LevelForm()
    context = {
        "judul": "Daftar Level Pengguna", 
        "tombol": "Tambah Level Baru",
        "form": form, 
        "datas": data,
        "total_submenus": total_submenus,
        "total_users": total_users,
        "total_levels": data.count(),
    }
    return render(request, "level/level_list.html", context) 

@set_submenu_session
@menu_access_required('simpan')
def simpan_level(request):
    request.session['next'] = request.get_full_path()
    data = Level.objects.annotate(
        total_users=Count('userlevel', distinct=True),
        active_subs=Count(
            'levelsub',
            filter=Q(levelsub__lihat=True) | Q(levelsub__simpan=True) | Q(levelsub__edit=True) | Q(levelsub__hapus=True),
            distinct=True
        )
    ).order_by('id')
    if request.method == "POST":
        form = LevelForm(request.POST or None)
        if form.is_valid():
            new_level = form.save()
            # Otomatis inisialisasi entri Levelsub untuk level baru
            submenus = Submenu.objects.all()
            for submenu in submenus:
                Levelsub.objects.get_or_create(levelsub_level=new_level, levelsub_submenu=submenu)
            messages.success(request, f'Level "{new_level.level_nama}" berhasil ditambahkan. Silakan atur hak akses sub menu.')
            return redirect('list_levelsub', number=new_level.id)
    else:
        form = LevelForm()
    context = {
        "judul": "Daftar Level Pengguna", 
        "tombol": "Tambah Level Baru",
        'form': form,
        'datas': data,
        "total_submenus": Submenu.objects.count(),
        "total_users": Userlevel.objects.count(),
        "total_levels": data.count(),
    }
    return render(request, "level/level_list.html", context)

@set_submenu_session
@menu_access_required('update')
def update_level(request, pk):
    request.session['next'] = request.get_full_path()
    data = get_object_or_404(Level, id=pk)
    formupdate = LevelForm(request.POST or None, instance=data)
    if request.method == "POST":
        if formupdate.is_valid():
            formupdate.save()
            messages.success(request, f'Level "{data.level_nama}" berhasil diupdate')
            return redirect("list_level")
    else:
        formupdate = LevelForm(instance=data)

    context = {"form": formupdate, "datas": data, "judul": f"Update Level {data.level_nama}"}
    return render(request, "level/level_edit.html", context)

@set_submenu_session
@menu_access_required('delete')
def delete_level(request, pk):
    request.session['next'] = request.get_full_path()
    try:
        data = Level.objects.get(id=pk)
        level_nama = data.level_nama
        data.delete()
        messages.warning(request, f'Level "{level_nama}" berhasil dihapus.')
    except Level.DoesNotExist:
        messages.error(request, "Level tidak ditemukan.")
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect("list_level")
