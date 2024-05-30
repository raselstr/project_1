# views.py

# from django.shortcuts import render, redirect
# from .forms import DanaForm, ProgramForm, KegiatanForm, SubkegiatanForm, SubRincianForm

# def combo_bertingkat(request):
#     dana_form = DanaForm()
#     program_form = ProgramForm()
#     kegiatan_form = KegiatanForm()
#     subkegiatan_form = SubkegiatanForm()
#     subrincian_form = SubRincianForm()
    
#     dana_id = None
#     program_id = None
#     kegiatan_id = None
#     subkegiatan_id = None

#     if request.method == 'POST':
#         dana_form = DanaForm(request.POST)
#         if dana_form.is_valid():
#             dana_id = dana_form.cleaned_data['dana'].id

#         program_form = ProgramForm(request.POST, dana_id=dana_id)
#         if program_form.is_valid():
#             program_id = program_form.cleaned_data['program'].id

#         kegiatan_form = KegiatanForm(request.POST, program_id=program_id)
#         if kegiatan_form.is_valid():
#             kegiatan_id = kegiatan_form.cleaned_data['kegiatan'].id

#         subkegiatan_form = SubkegiatanForm(request.POST, kegiatan_id=kegiatan_id)
#         if subkegiatan_form.is_valid():
#             subkegiatan_id = subkegiatan_form.cleaned_data['subkegiatan'].id

#         subrincian_form = SubRincianForm(request.POST, subkegiatan_id=subkegiatan_id)
#         if subrincian_form.is_valid():
#             # Proses data akhir atau lanjutkan ke logika lainnya
#             return redirect('dana_list')  # Redirect ke halaman sukses atau lainnya

#     context = {
#         'dana_form': dana_form,
#         'program_form': program_form,
#         'kegiatan_form': kegiatan_form,
#         'subkegiatan_form': subkegiatan_form,
#         'subrincian_form': subrincian_form,
#     }
#     return render(request, 'dana/dana_list.html', context)
