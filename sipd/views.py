import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.management import call_command
from .forms import SipdUploadForm


def upload_sipd(request):
    # 🔑 ambil tahun dari session
    tahun = request.session.get("tahun")
   
    if request.method == "POST":
        form = SipdUploadForm(request.POST, request.FILES)

        if form.is_valid():
            file = form.cleaned_data["file"]
            upload_dir = settings.MEDIA_ROOT / "import"
            os.makedirs(upload_dir, exist_ok=True)

            file_path = upload_dir / file.name

            with open(file_path, "wb+") as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            try:
                # 🔥 import langsung
                call_command(
                    "import_sipd_excel",
                    str(file_path),
                    tahun=tahun,
                )

                messages.success(
                    request,
                    f"Import SIPD berhasil untuk Tahun Anggaran {tahun}."
                )

            except Exception as e:
                messages.error(
                    request,
                    f"Gagal import data: {e}"
                )

            return redirect("upload_sipd")

        else:
            messages.error(request, "Form tidak valid. File Excel wajib diisi.")

    else:
        form = SipdUploadForm()

    context = {
        "form": form,
        "judul": "Upload Excel SIPD",
        "btntombol": "Upload",
        "tahun": tahun,
    }

    return render(request, "sipd/upload.html", context)
