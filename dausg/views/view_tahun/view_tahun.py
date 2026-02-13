from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, render
from django.views import View
from django.db import transaction

from core.services.tahun_duplicate_service import TahunDuplicateService
from core.services.tahun_delete_service import TahunDeleteService

from ...models_log import LogCopyTahun
from ...models import *


class CopyTahunView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = "dausg/copy_tahun.html"

    # 🔐 hanya admin/staff
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    # ================= GET =================
    def get(self, request):
        logs = LogCopyTahun.objects.all()[:20]
        return render(request, self.template_name, {"logs": logs})

    # ================= POST =================
    def post(self, request):

        # fallback default → copy (biar Enter tidak error)
        action = request.POST.get("action") or "copy"

        sektor = request.POST.get("sektor")
        tahun_asal = request.POST.get("tahun_asal")
        tahun_tujuan = request.POST.get("tahun_tujuan")

        tahun_asal = int(tahun_asal) if tahun_asal else None
        tahun_tujuan = int(tahun_tujuan) if tahun_tujuan else None

        mapping = {
            "pendidikan": (
                DausgpendidikanProg, DausgpendidikanKeg, DausgpendidikanSub,
                "dausgpendidikankeg_prog", "dausgpendidikansub_keg", "dausgpendidikan_tahun",
            ),
            "kesehatan": (
                DausgkesehatanProg, DausgkesehatanKeg, DausgkesehatanSub,
                "dausgkesehatankeg_prog", "dausgkesehatansub_keg", "dausgkesehatan_tahun",
            ),
            "pu": (
                DausgpuProg, DausgpuKeg, DausgpuSub,
                "dausgpukeg_prog", "dausgpusub_keg", "dausgpu_tahun",
            ),
            "dankel": (
                DankelProg, DankelKeg, Dankelsub,
                "dankelkeg_prog", "dankelsub_keg", "dankel_tahun",
            ),
        }

        if sektor not in mapping:
            messages.error(request, "Sektor tidak valid.")
            return redirect(request.path)

        ModelProg, ModelKeg, ModelSub, fk_keg, fk_sub, field_tahun = mapping[sektor]

        # =====================================================
        # ======================= COPY ========================
        # =====================================================
        if action == "copy":

            if not tahun_asal or not tahun_tujuan:
                messages.error(request, "Tahun asal dan tujuan wajib diisi.")
                return redirect(request.path)

            try:
                success, msg, summary = TahunDuplicateService.duplicate_tree(
                    ModelProg, ModelKeg, ModelSub,
                    fk_keg, fk_sub, field_tahun,
                    tahun_asal, tahun_tujuan,
                )
                status = "SUCCESS" if success else "FAILED"

            except Exception as e:
                success = False
                msg = str(e)
                summary = {}
                status = "FAILED"

            LogCopyTahun.objects.create(
                sektor=sektor,
                tahun_asal=tahun_asal,
                tahun_tujuan=tahun_tujuan,
                status=status,
                pesan=f"{msg} | {summary}",
                user=request.user,
            )

            messages.success(request, msg) if success else messages.error(request, msg)
            return redirect(request.path)

        # =====================================================
        # ======================= DELETE ======================
        # =====================================================
        if action == "delete":

            if not tahun_tujuan:
                messages.error(request, "Tahun tujuan wajib diisi untuk hapus.")
                return redirect(request.path)

            try:
                with transaction.atomic():
                    total = TahunDeleteService.delete_tahun(
                        ModelProg, ModelKeg, ModelSub,
                        fk_keg, fk_sub, field_tahun,
                        tahun_tujuan,
                    )

                status = "SUCCESS"
                msg = (
                    f"Hapus tahun {tahun_tujuan} → "
                    f"Prog:{total['program']}, "
                    f"Keg:{total['kegiatan']}, "
                    f"Sub:{total['sub']}"
                )

            except Exception as e:
                status = "FAILED"
                msg = str(e)

            LogCopyTahun.objects.create(
                sektor=sektor,
                tahun_asal=tahun_tujuan,
                tahun_tujuan=tahun_tujuan,
                status=status,
                pesan=msg,
                user=request.user,
            )

            messages.success(request, msg) if status == "SUCCESS" else messages.error(request, msg)
            return redirect(request.path)

        # fallback (harusnya tidak pernah kena)
        messages.error(request, "Aksi tidak dikenali.")
        return redirect(request.path)
