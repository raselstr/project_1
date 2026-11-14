from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.forms import modelformset_factory
from project.decorators import menu_access_required, set_submenu_session

from ..models import Levelsub, Submenu, Level
from ..forms import LevelsubForm

template_list = 'levelsub/levelsub_list.html'


@set_submenu_session
@menu_access_required('simpan')
def manage_levelsubs(request, number):
    request.session['next'] = request.get_full_path()
    level = get_object_or_404(Level, pk=number)
    
    # Pastikan setiap Submenu yang ada memiliki entri Levelsub untuk level ini
    submenus = Submenu.objects.all().select_related('submenu_menu').order_by('submenu_menu__id', 'id')
    for submenu in submenus:
        Levelsub.objects.get_or_create(levelsub_level=level, levelsub_submenu=submenu)
    
    LevelsubFormSet = modelformset_factory(Levelsub, form=LevelsubForm, extra=0)
    queryset = Levelsub.objects.filter(levelsub_level=level).select_related(
        'levelsub_submenu__submenu_menu'
    ).order_by('levelsub_submenu__submenu_menu__id', 'levelsub_submenu__id')

    if request.method == 'POST':
        formset = LevelsubFormSet(request.POST, queryset=queryset)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.levelsub_level = level
                instance.save()
            
            messages.success(request, f'Hak akses sub menu untuk level "{level.level_nama}" berhasil disimpan!')
            
            if request.POST.get('simpan_kembali') == '1':
                return redirect('list_level')
            return redirect('list_levelsub', number=level.id)
        else:
            messages.error(request, 'Terjadi kesalahan saat memvalidasi form. Silakan periksa kembali.')
    else:
        formset = LevelsubFormSet(queryset=queryset)

    # Kelompokkan formset berdasarkan Menu induk
    menu_groups = []
    current_menu_id = None
    current_group = None

    for form in formset.forms:
        submenu = form.instance.levelsub_submenu
        menu = submenu.submenu_menu
        if current_menu_id != menu.id:
            current_menu_id = menu.id
            current_group = {
                'menu': menu,
                'items': [],
                'total_count': 0,
                'active_count': 0,
            }
            menu_groups.append(current_group)

        # Cek apakah form memiliki hak akses aktif (Lihat, Simpan, Edit, atau Hapus)
        is_active = bool(
            form['lihat'].value() or 
            form['simpan'].value() or 
            form['edit'].value() or 
            form['hapus'].value()
        )
        current_group['items'].append({
            'form': form,
            'submenu': submenu,
            'is_active': is_active,
        })
        current_group['total_count'] += 1
        if is_active:
            current_group['active_count'] += 1

    total_submenus = len(formset.forms)
    total_active = sum(g['active_count'] for g in menu_groups)
    all_levels = Level.objects.all().order_by('id')

    context = {
        'formset': formset,
        'menu_groups': menu_groups,
        'level': level,
        'all_levels': all_levels,
        'total_submenus': total_submenus,
        'total_active': total_active,
        'judul': f'Hak Akses Sub Menu - {level.level_nama}',
    }
    return render(request, template_list, context)
