# File: your_app/views.py
from django.shortcuts import render, get_object_or_404,redirect
from .models import RencDankel
from .forms import RencDankelForm, RencDankelsisaFormSet

# def rencdankel_form(request):
#     if request.method == 'POST':
#         form = RencDankelForm(request.POST)
#         formset = RencDankelsisaFormSet(request.POST)
#         if form.is_valid() and formset.is_valid():
#             rencdankel = form.save()
#             instances = formset.save(commit=False)
#             for instance in instances:
#                 instance.rencdankelsisa_rencana = rencdankel
#                 instance.save()
#             return redirect('success_url')  # Ganti dengan URL redirect setelah berhasil
#     else:
#         form = RencDankelForm()
#         formset = RencDankelsisaFormSet()
    
#     context = {
#         'form': form,
#         'formset': formset,
#         'judul' : 'Form Rencana Kegiatan'
#     }
#     return render(request, 'dankel/dankel_form.html', context)

def rencdankel_update(request, pk):
    # Mendapatkan instance RencDankel yang ingin diupdate
    rencdankel = get_object_or_404(RencDankel, pk=pk)

    if request.method == 'POST':
        # Membuat instance formulir dengan data yang dikirimkan
        form = RencDankelForm(request.POST, instance=rencdankel)
        formset = RencDankelsisaFormSet(request.POST, instance=rencdankel)
        if form.is_valid() and formset.is_valid():
            # Menyimpan perubahan pada objek RencDankel
            rencdankel = form.save()

            # Menyimpan perubahan pada setiap objek RencDankelsisa yang terkait
            instances = formset.save(commit=False)
            for instance in instances:
                instance.rencdankelsisa_rencana = rencdankel
                instance.save()

            return redirect('success_url')  # Ganti dengan URL redirect setelah berhasil
    else:
        # Menyiapkan formulir dan formset dengan data yang sudah ada
        form = RencDankelForm(instance=rencdankel)
        formset = RencDankelsisaFormSet(instance=rencdankel)
    
    context = {
        'form': form,
        'formset': formset,
    }
    return render(request, 'dankel/dankel_form.html', context)


def rencdankel_simpan(request):
    if request.method == 'POST':
        form = RencDankelForm(request.POST)
        formset = RencDankelsisaFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            rencdankel = form.save()
            instances = formset.save(commit=False)
            for instance in instances:
                instance.rencdankelsisa_rencana = rencdankel
                instance.save()
            formset.save_m2m()
            return redirect('rencdankel_list')  # Ganti dengan URL redirect setelah berhasil
    else:
        form = RencDankelForm()
        formset = RencDankelsisaFormSet()
    
    context = {
        'form': form,
        'formset': formset,
        'judul': 'Form Rencana Kegiatan'
    }
    return render(request, 'dankel/dankel_form.html', context)


def rencdankel_form(request):
    form = RencDankelForm()
    formset = RencDankelsisaFormSet()
    
    context = {
        'form': form,
        'formset': formset,
        'judul': 'Form Rencana Kegiatan'
    }
    return render(request, 'dankel/dankel_form.html', context)

def rencdankel_list(request):
    rencdankels = RencDankel.objects.select_related(
        'rencdankel_opd', 
        'rencdankel_sub__dankelsub_keg'
        ).prefetch_related('rencdankelsisa').all().order_by('rencdankel_sub__dankelsub_keg')

    context = {
        'rencdankels': rencdankels,
        'judul' : 'Rencana Kegiatan',
        'tombol' : 'Tambah Perencanaan',
    }
    return render(request, 'dankel/dankel_list.html', context)
