from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from project.decorators import menu_access_required, set_submenu_session
from django.forms import modelformset_factory

from ..models import Levelsub, Submenu, Level
from ..forms import LevelsubForm

Model_data = Levelsub
Form_data = LevelsubForm
template_list = 'levelsub/levelsub_list.html'


@set_submenu_session
@menu_access_required('simpan')
def manage_levelsubs(request, number):
    request.session['next'] = request.get_full_path()
    LevelsubFormSet = modelformset_factory(Levelsub, form=LevelsubForm, extra=0)
    level = get_object_or_404(Level, pk=number)
    submenus = Submenu.objects.all().order_by('submenu_menu')
    
    for submenu in submenus:
        Levelsub.objects.get_or_create(levelsub_level_id=number, levelsub_submenu=submenu)
    

    if request.method == 'POST':
        formset = LevelsubFormSet(request.POST, queryset=Levelsub.objects.filter(levelsub_level=level))
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.levelsub_level = level
                instance.save()
                
            return redirect('list_level')  # Ganti dengan URL yang sesuai
    else:
        
        formset = LevelsubFormSet(queryset=Levelsub.objects.filter(levelsub_level=level))
    
    return render(request, template_list, {'formset': formset, 'level': level, 'judul':'Daftar List Aktifitas'})


# def list(request, number):
#     submenus = Submenu.objects.all().order_by('submenu_menu')
    
#     # Pastikan setiap Submenu memiliki entri di Levelsub untuk level yang diberikan
#     for submenu in submenus:
#         Levelsub.objects.get_or_create(levelsub_level_id=number, levelsub_submenu=submenu)
    
#     if request.method == 'POST':
#         formset = LevelsubFormSet(request.POST)
#         if formset.is_valid():
#             formset.save()
#             return redirect('list_level')  # Ganti dengan URL yang sesuai
#     else:
#         formset = LevelsubFormSet(queryset=Levelsub.objects.filter(levelsub_level=number))
    
#     context = {
#         'formset': formset,
#         'number': number,
#         'tbltombol': 'Simpan Pengaturan'
#     }
#     return render(request, 'levelsub/levelsub_list.html', context)

# LevelsubFormSet = modelformset_factory(Levelsub, form=LevelsubForm, extra=0)
# @menu_access_required
# def list(request, number):
#     data = Submenu.objects.prefetch_related('levelsub_set').order_by('submenu_menu')
    
#     form = Form_data(request.POST or None, number)

#     context = {
#         'data': data,
#         'form':form,
#         'number':number,
#         'tbltombol' : 'Simpan Pengaturan'
#     }
#     return render(request, template_list, context)

# @menu_access_required
# def simpan_level(request):
#     data = Level.objects.all()
#     if request.method == "POST":
#         form = LevelForm(request.POST or None)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Data Berhasil disimpan')
#             return redirect('list_level')
#     else:
#         form = LevelForm()
#     context = {
#         'form'  : form,
#         'datas': data
#     }
#     return render(request, "level/level_list.html", context)

# @menu_access_required
# def update_level(request, pk):
#     data = get_object_or_404(Level, id=pk)
#     formupdate = LevelForm(request.POST or None, instance=data)
#     if request.method == "POST":
#         if formupdate.is_valid():
#             formupdate.save()
#             messages.success(request, "Data Berhasil diupdate")
#             return redirect("list_level")
#     else:
#         formupdate = LevelForm(instance=data)

#     context = {"form": formupdate, "datas": data, "judul": "Update Level"}
#     return render(request, "level/level_edit.html", context)

# @menu_access_required
# def delete_level(request, pk):
#     try:
#         data = Level.objects.get(id=pk)
#         data.delete()
#         messages.warning(request, "Data Berhasil dihapus")
#     except Level.DoesNotExist:
#         messages.error(request,"Dana tidak ditemukan")
#     except ValidationError as e:
#         messages.error(request, str(e))
#     return redirect("list_level")
