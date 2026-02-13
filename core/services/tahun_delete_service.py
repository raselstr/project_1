from django.db import transaction

class TahunDeleteService:

    @staticmethod
    def delete_tahun(
        ModelProg,
        ModelKeg,
        ModelSub,
        fk_keg_to_prog,
        fk_sub_to_keg,
        field_tahun,
        tahun,
    ):
        """
        Hapus seluruh tree berdasarkan tahun
        urutan: SUB → KEG → PROG
        return total data terhapus
        """

        # ================= SUB =================
        sub_qs = ModelSub.objects.filter(
            **{f"{fk_sub_to_keg}__{fk_keg_to_prog}__{field_tahun}": tahun}
        )
        total_sub = sub_qs.count()
        sub_qs.delete()

        # ================= KEG =================
        keg_qs = ModelKeg.objects.filter(
            **{f"{fk_keg_to_prog}__{field_tahun}": tahun}
        )
        total_keg = keg_qs.count()
        keg_qs.delete()

        # ================= PROG =================
        prog_qs = ModelProg.objects.filter(**{field_tahun: tahun})
        total_prog = prog_qs.count()
        prog_qs.delete()

        return {
            "program": total_prog,
            "kegiatan": total_keg,
            "sub": total_sub,
        }
