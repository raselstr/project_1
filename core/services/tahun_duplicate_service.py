from django.db import transaction


class TahunDuplicateService:

    @staticmethod
    @transaction.atomic
    def duplicate_tree(
        ModelProg,
        ModelKeg,
        ModelSub,
        fk_keg_to_prog,
        fk_sub_to_keg,
        field_tahun,
        tahun_asal,
        tahun_tujuan,
    ):
        """
        Copy data 3 level: Program → Kegiatan → Sub
        - Aman dijalankan berulang (resume safe)
        - Tidak overwrite data tahun tujuan
        - Selalu return 3 nilai: status, message, summary dict
        """

        # ❌ Tahun sama
        if tahun_asal == tahun_tujuan:
            return False, "Tahun asal dan tujuan tidak boleh sama.", {}

        # ❌ Tidak ada data asal
        prog_lama = ModelProg.objects.filter(**{field_tahun: tahun_asal})
        if not prog_lama.exists():
            return False, f"Data tahun {tahun_asal} tidak ditemukan.", {}

        # ================= PROGRAM =================
        map_prog = {}

        prog_tujuan_existing = {
            getattr(p, field_tahun): p.id
            for p in ModelProg.objects.filter(**{field_tahun: tahun_tujuan})
        }

        created_prog = 0

        for old in prog_lama:
            old_id = old.id

            # kalau sudah pernah dicopy → skip
            if old_id in prog_tujuan_existing.values():
                continue

            old.pk = None
            setattr(old, field_tahun, tahun_tujuan)
            old.save()

            map_prog[old_id] = old.id
            created_prog += 1

        # ================= KEGIATAN =================
        map_keg = {}
        created_keg = 0

        keg_lama = ModelKeg.objects.filter(
            **{f"{fk_keg_to_prog}__{field_tahun}": tahun_asal}
        )

        for old in keg_lama:
            old_prog_id = getattr(old, f"{fk_keg_to_prog}_id")

            # skip kalau program tidak ikut tercopy / tidak ada mapping
            if old_prog_id not in map_prog:
                continue

            old_id = old.id
            old.pk = None
            setattr(old, f"{fk_keg_to_prog}_id", map_prog[old_prog_id])
            old.save()

            map_keg[old_id] = old.id
            created_keg += 1

        # ================= SUB =================
        created_sub = 0

        sub_lama = ModelSub.objects.filter(
            **{f"{fk_sub_to_keg}__{fk_keg_to_prog}__{field_tahun}": tahun_asal}
        )

        for old in sub_lama:
            old_keg_id = getattr(old, f"{fk_sub_to_keg}_id")

            # skip kalau kegiatan tidak ikut tercopy
            if old_keg_id not in map_keg:
                continue

            old.pk = None
            setattr(old, f"{fk_sub_to_keg}_id", map_keg[old_keg_id])
            old.save()

            created_sub += 1

        summary = {
            "program_dibuat": created_prog,
            "kegiatan_dibuat": created_keg,
            "sub_dibuat": created_sub,
        }
        
        if created_prog == 0 and created_keg == 0 and created_sub == 0:
            return False, "Tidak ada data baru yang dicopy.", summary

        return True, "Copy selesai.", summary


