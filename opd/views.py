from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import Opd, Book, Author, Publisher
from .forms import OpdForm, BookForm

# Create your views here.
def opd_list(request):
    opd = Opd.objects.all()
    form = OpdForm()
    context = {
        "judul": "Daftar OPD", 
        "form": form, 
        "opds": opd
    }
    return render(request, "opd/opd_list.html", context)

def simpan_opd(request):
    opd = Opd.objects.all()
    if request.method == "POST":
        form = OpdForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil disimpan')
            return redirect('opd_list')
    else:
        form = OpdForm()
    context = {
        'form'  : form,
        'opds'  : opd
    }
    return render(request, "opd/opd_list.html", context)


# View untuk mengedit data OPD
def update_opd(request, pk):
    opd = Opd.objects.get(id=pk)
    form = OpdForm(request.POST or None, instance=opd)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Data Berhasil diupdate")
            return redirect("opd_list")
    else:
        form = OpdForm(instance=opd)

    opd = Opd.objects.all()
    context = {"form": form, "opds": opd, "judul": "Update OPD"}
    return render(request, "opd/edit_opd.html", context)


def delete_opd(request, pk):
    try:
        opd = Opd.objects.get(id=pk)
        opd.delete()
        messages.warning(request, "Data Berhasil dihapus")
    except Opd.DoesNotExist:
        messages.error(request,"Dana tidak ditemukan")
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect("opd_list")


def book_create(request):
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("book_list")
    else:
        form = BookForm()
    return render(request, "opd/book_form.html", {"form": form})


def book_list(request):
    books = Book.objects.select_related("author", "publisher").all()
    return render(request, "opd/book_list.html", {"books": books})
