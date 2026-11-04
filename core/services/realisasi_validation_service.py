from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db.models import Sum, Q

from pagu.models import Pagudausg
from penerimaan.models import Penerimaan, DistribusiPenerimaan


class RealisasiValidationService:
    """
    Service validasi ketat untuk input Realisasi SP2D:
    1. Nilai Realisasi SP2D tidak boleh melebihi Total Dana yang diterima (Penerimaan) sesuai bidangnya (kumulatif per tahap dan total tahun).
    2. Nilai Realisasi SP2D tidak boleh melebihi Total Pagu per OPD (Pagudausg).
    3. Nilai Realisasi SP2D tidak boleh melebihi Nilai Rencana Sub Kegiatan terposting (posting_pagu / rencdankel_pagu).
    4. Akumulasi Realisasi Capaian Output tidak boleh melebihi Rencana Capaian Output terposting (posting_output).
    5. Untuk Dana Kelurahan:
       - SP2D TU, LPJ TU, dan STS TU konsisten (LPJ <= SP2D, STS == SP2D - LPJ).
       - Tidak boleh melebihi Distribusi Dana yang sudah diinput untuk kelurahan tersebut.
       - Sisa distribusi Tahap 1 diakumulasikan ke Tahap 2 dan seterusnya (akumulasi kumulatif Tahap 1..T).
       - Menampilkan warning ketat jika melebihi batas yang tersedia.
    """

    @classmethod
    def validate_realisasi(cls, instance):
        """
        Validasi ketat untuk Bidang Pendidikan, Kesehatan, dan Pekerjaan Umum (Utama maupun Sisa).
        """
        model_class = instance.__class__
        tahun = instance.realisasi_tahun
        dana = instance.realisasi_dana
        subopd = instance.realisasi_subopd
        tahap = instance.realisasi_tahap
        posting = getattr(instance, 'realisasi_rencanaposting', None)
        sp2d = getattr(instance, 'realisasi_sp2d', None)
        nilai_sp2d = Decimal(str(instance.realisasi_nilai or 0))
        output_saat_ini = Decimal(str(instance.realisasi_output or 0))
        pk = instance.pk

        # Lewatkan jika bukan input/edit transaksi realisasi (misal form filter yang hanya memilih tahun/dana/subopd/tahap)
        if not posting and not sp2d:
            return

        subopd_nama = getattr(subopd, 'sub_nama', str(subopd or 'OPD'))
        dana_nama = getattr(dana, 'sub_nama', str(dana or 'Bidang terkait'))

        # 1. Validasi nilai dasar
        if nilai_sp2d < 0:
            raise ValidationError("Nilai Realisasi SP2D tidak boleh kurang dari 0.")
        if output_saat_ini < 0:
            raise ValidationError("Capaian Output Realisasi tidak boleh kurang dari 0.")

        # 2. Validasi Nilai Rencana Sub Kegiatan terposting & Akumulasi Output terposting
        if posting:
            posting_pagu = Decimal(str(getattr(posting, 'posting_pagu', 0) or 0))
            posting_output = Decimal(str(getattr(posting, 'posting_output', 0) or 0))

            existing_subkeg = model_class.objects.filter(
                realisasi_tahun=tahun,
                realisasi_dana=dana,
                realisasi_subopd=subopd,
                realisasi_rencanaposting=posting,
            )
            if pk:
                existing_subkeg = existing_subkeg.exclude(pk=pk)

            # Akumulasi nilai SP2D sub kegiatan
            realisasi_subkeg_lain = existing_subkeg.aggregate(s=Sum('realisasi_nilai'))['s'] or Decimal(0)
            accum_sp2d_subkeg = realisasi_subkeg_lain + nilai_sp2d

            if accum_sp2d_subkeg > posting_pagu:
                sisa_pagu_subkeg = max(Decimal(0), posting_pagu - realisasi_subkeg_lain)
                selisih = accum_sp2d_subkeg - posting_pagu
                raise ValidationError(
                    f"Total Realisasi SP2D untuk Sub Kegiatan ini setelah ditambah saat ini menjadi "
                    f"Rp. {accum_sp2d_subkeg:,.2f}, melebihi Nilai Rencana Sub Kegiatan terposting "
                    f"sebesar Rp. {posting_pagu:,.2f}. "
                    f"(Sisa pagu yang tersedia untuk sub kegiatan ini: Rp. {sisa_pagu_subkeg:,.2f}, Kelebihan: Rp. {selisih:,.2f})."
                )

            # Akumulasi output sub kegiatan
            output_subkeg_lain = existing_subkeg.aggregate(s=Sum('realisasi_output'))['s'] or Decimal(0)
            accum_output_subkeg = output_subkeg_lain + output_saat_ini

            # Capaian output bisa diisi 0 saat capaian output yang sudah diinput sudah = rencana output terposting
            if output_saat_ini > 0:
                if output_subkeg_lain >= posting_output:
                    raise ValidationError(
                        f"Rencana Capaian Output terposting ({posting_output:,.2f}) untuk Sub Kegiatan ini "
                        f"sudah terpenuhi sepenuhnya oleh realisasi yang sudah diinput ({output_subkeg_lain:,.2f}). "
                        f"Capaian output pada transaksi SP2D ini harus diisi 0."
                    )
                elif accum_output_subkeg > posting_output:
                    sisa_output = max(Decimal(0), posting_output - output_subkeg_lain)
                    selisih_out = accum_output_subkeg - posting_output
                    raise ValidationError(
                        f"Akumulasi Realisasi Capaian Output untuk Sub Kegiatan ini menjadi "
                        f"{accum_output_subkeg:,.2f}, melebihi Rencana Capaian Output terposting "
                        f"sebesar {posting_output:,.2f}. "
                        f"(Sisa output yang dapat direalisasikan: {sisa_output:,.2f}, Kelebihan: {selisih_out:,.2f}). "
                        f"Jika capaian output sudah terpenuhi oleh transaksi sebelumnya, silakan isi 0."
                    )

        # 3. Validasi Total Pagu per OPD
        if subopd and dana:
            pagu_opd = Pagudausg.objects.filter(
                pagudausg_tahun=tahun,
                pagudausg_dana=dana,
                pagudausg_opd=subopd,
            ).aggregate(s=Sum('pagudausg_nilai'))['s'] or Decimal(0)

            pagu_configured = Pagudausg.objects.filter(pagudausg_tahun=tahun, pagudausg_dana=dana).exists()
            if pagu_configured:
                existing_opd = model_class.objects.filter(
                    realisasi_tahun=tahun,
                    realisasi_dana=dana,
                    realisasi_subopd=subopd,
                )
                if pk:
                    existing_opd = existing_opd.exclude(pk=pk)

                realisasi_opd_lain = existing_opd.aggregate(s=Sum('realisasi_nilai'))['s'] or Decimal(0)
                accum_opd_nilai = realisasi_opd_lain + nilai_sp2d

                if accum_opd_nilai > pagu_opd:
                    sisa_opd = max(Decimal(0), pagu_opd - realisasi_opd_lain)
                    selisih_opd = accum_opd_nilai - pagu_opd
                    raise ValidationError(
                        f"Total Realisasi SP2D untuk {subopd_nama} setelah ditambah saat ini menjadi "
                        f"Rp. {accum_opd_nilai:,.2f}, melebihi Total Pagu Alokasi OPD sebesar "
                        f"Rp. {pagu_opd:,.2f}. "
                        f"(Sisa alokasi pagu OPD tersedia: Rp. {sisa_opd:,.2f}, Kelebihan: Rp. {selisih_opd:,.2f})."
                    )

        # 4. Validasi Total Dana yang Diterima (Penerimaan Bidang)
        if dana:
            tahap_id = getattr(tahap, 'id', tahap)

            # Validasi Kumulatif s.d. Tahap yang sedang diinput
            if tahap_id:
                try:
                    t_int = int(tahap_id)
                    tahap_ids = list(range(1, t_int + 1))
                except (ValueError, TypeError):
                    tahap_ids = []

                if tahap_ids:
                    penerimaan_kumulatif = Penerimaan.objects.filter(
                        penerimaan_tahun=tahun,
                        penerimaan_dana=dana,
                        penerimaan_tahap_id__in=tahap_ids,
                    ).aggregate(s=Sum('penerimaan_nilai'))['s'] or Decimal(0)

                    # Jika terdapat data penerimaan bertahap, cek kumulatif tahap
                    if penerimaan_kumulatif > 0:
                        existing_tahap = model_class.objects.filter(
                            realisasi_tahun=tahun,
                            realisasi_dana=dana,
                            realisasi_tahap_id__in=tahap_ids,
                        )
                        if pk:
                            existing_tahap = existing_tahap.exclude(pk=pk)

                        realisasi_tahap_lain = existing_tahap.aggregate(s=Sum('realisasi_nilai'))['s'] or Decimal(0)
                        accum_tahap_nilai = realisasi_tahap_lain + nilai_sp2d

                        if accum_tahap_nilai > penerimaan_kumulatif:
                            sisa_penerimaan_tahap = max(Decimal(0), penerimaan_kumulatif - realisasi_tahap_lain)
                            selisih_tahap = accum_tahap_nilai - penerimaan_kumulatif
                            raise ValidationError(
                                f"Total Realisasi SP2D Bidang {dana_nama} s.d. Tahap {tahap_id} menjadi "
                                f"Rp. {accum_tahap_nilai:,.2f}, melebihi Total Dana Penerimaan yang diterima "
                                f"s.d. Tahap {tahap_id} sebesar Rp. {penerimaan_kumulatif:,.2f}. "
                                f"(Sisa dana penerimaan tersedia: Rp. {sisa_penerimaan_tahap:,.2f}, Kelebihan: Rp. {selisih_tahap:,.2f})."
                            )

            # Validasi Total Penerimaan Tahunan Keseluruhan
            penerimaan_total = Penerimaan.objects.filter(
                penerimaan_tahun=tahun,
                penerimaan_dana=dana,
            ).aggregate(s=Sum('penerimaan_nilai'))['s'] or Decimal(0)

            if penerimaan_total > 0:
                existing_total = model_class.objects.filter(
                    realisasi_tahun=tahun,
                    realisasi_dana=dana,
                )
                if pk:
                    existing_total = existing_total.exclude(pk=pk)

                realisasi_total_lain = existing_total.aggregate(s=Sum('realisasi_nilai'))['s'] or Decimal(0)
                accum_total_nilai = realisasi_total_lain + nilai_sp2d

                if accum_total_nilai > penerimaan_total:
                    sisa_total = max(Decimal(0), penerimaan_total - realisasi_total_lain)
                    selisih_total = accum_total_nilai - penerimaan_total
                    raise ValidationError(
                        f"Total Realisasi SP2D Bidang {dana_nama} setelah ditambah saat ini menjadi "
                        f"Rp. {accum_total_nilai:,.2f}, melebihi Total Dana Penerimaan yang diterima "
                        f"sebesar Rp. {penerimaan_total:,.2f}. "
                        f"(Sisa dana penerimaan tahunan tersedia: Rp. {sisa_total:,.2f}, Kelebihan: Rp. {selisih_total:,.2f})."
                    )

    @classmethod
    def validate_realisasi_dankel(cls, instance):
        """
        Validasi ketat khusus untuk Realisasi Dana Kelurahan (RealisasiDankel dan RealisasiDankelsisa):
        - SP2D TU, LPJ TU, dan STS TU konsisten
        - Tidak melebihi Distribusi Penerimaan yang sudah diinput untuk kelurahan tersebut
        - Sisa distribusi Tahap 1 diakumulasikan ke Tahap 2 dan seterusnya (Tahap 1..T)
        - Tidak melebihi Total Pagu per Kelurahan
        - Tidak melebihi Rencana Sub Kegiatan terposting
        - Akumulasi output tidak melebihi rencana output terposting
        """
        model_class = instance.__class__
        is_sisa = hasattr(instance, 'realisasidankelsisa_tahun')
        prefix = 'realisasidankelsisa_' if is_sisa else 'realisasidankel_'

        tahun = getattr(instance, f'{prefix}tahun')
        dana = getattr(instance, f'{prefix}dana')
        subopd = getattr(instance, f'{prefix}subopd')
        tahap = getattr(instance, f'{prefix}tahap')
        rencana = getattr(instance, f'{prefix}rencana', None)
        sp2d = getattr(instance, f'{prefix}sp2dtu', None)
        lpj = getattr(instance, f'{prefix}lpj', None)
        nilai_sp2d = Decimal(str(getattr(instance, f'{prefix}nilai', 0) or 0))
        nilai_lpj = Decimal(str(getattr(instance, f'{prefix}lpjnilai', 0) or 0))
        nilai_sts = Decimal(str(getattr(instance, f'{prefix}stsnilai', 0) or 0))
        output_saat_ini = Decimal(str(getattr(instance, f'{prefix}output', 0) or 0))
        pk = instance.pk

        # Lewatkan jika bukan input/edit transaksi realisasi (misal form filter yang hanya memilih tahun/dana/subopd/tahap)
        if not rencana and not sp2d and not lpj:
            return

        subopd_nama = getattr(subopd, 'sub_nama', str(subopd or 'Kelurahan'))

        # 1. Validasi nilai SP2D, LPJ, STS
        if nilai_sp2d < 0:
            raise ValidationError("Nilai SP2D TU tidak boleh kurang dari 0.")
        if nilai_lpj < 0:
            raise ValidationError("Nilai LPJ TU tidak boleh kurang dari 0.")
        if nilai_lpj > nilai_sp2d:
            raise ValidationError(
                f"Nilai LPJ TU (Rp. {nilai_lpj:,.2f}) tidak boleh lebih besar dari Nilai SP2D TU (Rp. {nilai_sp2d:,.2f})."
            )

        sisa_sts = nilai_sp2d - nilai_lpj
        if nilai_sts < 0:
            raise ValidationError("Nilai STS TU tidak boleh kurang dari 0.")
        if nilai_sts != sisa_sts:
            raise ValidationError(
                f"Nilai STS TU (Rp. {nilai_sts:,.2f}) harus sama persis dengan selisih SP2D TU dan LPJ TU yaitu Rp. {sisa_sts:,.2f}."
            )

        if output_saat_ini < 0:
            raise ValidationError("Capaian output realisasi tidak boleh kurang dari 0.")

        # 2. Validasi Nilai Rencana Sub Kegiatan Terposting & Akumulasi Output Terposting
        if rencana:
            pagu_posting = Decimal(str(getattr(rencana, 'rencdankelsisa_pagu', getattr(rencana, 'rencdankel_pagu', 0)) or 0))
            output_posting = Decimal(str(getattr(rencana, 'rencdankelsisa_output', getattr(rencana, 'rencdankel_output', 0)) or 0))

            filter_subkeg = {
                f'{prefix}tahun': tahun,
                f'{prefix}dana': dana,
                f'{prefix}subopd': subopd,
                f'{prefix}rencana': rencana,
            }
            existing_subkeg = model_class.objects.filter(**filter_subkeg)
            if pk:
                existing_subkeg = existing_subkeg.exclude(pk=pk)

            # Akumulasi nilai LPJ sub kegiatan
            realisasi_lpj_lain = existing_subkeg.aggregate(s=Sum(f'{prefix}lpjnilai'))['s'] or Decimal(0)
            accum_lpj_subkeg = realisasi_lpj_lain + nilai_lpj

            if accum_lpj_subkeg > pagu_posting:
                sisa_pagu_subkeg = max(Decimal(0), pagu_posting - realisasi_lpj_lain)
                selisih_pagu = accum_lpj_subkeg - pagu_posting
                raise ValidationError(
                    f"Total Realisasi LPJ untuk Sub Kegiatan ini setelah ditambah saat ini menjadi "
                    f"Rp. {accum_lpj_subkeg:,.2f}, melebihi Nilai Rencana Sub Kegiatan terposting "
                    f"sebesar Rp. {pagu_posting:,.2f}. "
                    f"(Sisa pagu tersedia untuk sub kegiatan ini: Rp. {sisa_pagu_subkeg:,.2f}, Kelebihan: Rp. {selisih_pagu:,.2f})."
                )

            # Akumulasi output sub kegiatan
            output_subkeg_lain = existing_subkeg.aggregate(s=Sum(f'{prefix}output'))['s'] or Decimal(0)
            accum_output_subkeg = output_subkeg_lain + output_saat_ini

            # Capaian output bisa diisi 0 saat capaian output yang sudah diinput sudah = rencana output terposting
            if output_saat_ini > 0:
                if output_subkeg_lain >= output_posting:
                    raise ValidationError(
                        f"Rencana Capaian Output terposting ({output_posting:,.2f}) untuk Sub Kegiatan ini "
                        f"sudah terpenuhi sepenuhnya oleh realisasi yang sudah diinput ({output_subkeg_lain:,.2f}). "
                        f"Capaian output pada transaksi realisasi ini harus diisi 0."
                    )
                elif accum_output_subkeg > output_posting:
                    sisa_output = max(Decimal(0), output_posting - output_subkeg_lain)
                    selisih_out = accum_output_subkeg - output_posting
                    raise ValidationError(
                        f"Akumulasi Realisasi Capaian Output untuk Sub Kegiatan ini menjadi "
                        f"{accum_output_subkeg:,.2f}, melebihi Rencana Capaian Output terposting "
                        f"sebesar {output_posting:,.2f}. "
                        f"(Sisa output yang dapat direalisasikan: {sisa_output:,.2f}, Kelebihan: {selisih_out:,.2f}). "
                        f"Jika capaian output sudah terpenuhi oleh transaksi sebelumnya, silakan isi 0."
                    )

        # 3. Validasi Total Pagu per Kelurahan (OPD)
        if subopd and dana:
            pagu_opd = Pagudausg.objects.filter(
                pagudausg_tahun=tahun,
                pagudausg_dana=dana,
                pagudausg_opd=subopd,
            ).aggregate(s=Sum('pagudausg_nilai'))['s'] or Decimal(0)

            pagu_configured = Pagudausg.objects.filter(pagudausg_tahun=tahun, pagudausg_dana=dana).exists()
            if pagu_configured:
                filter_opd = {
                    f'{prefix}tahun': tahun,
                    f'{prefix}dana': dana,
                    f'{prefix}subopd': subopd,
                }
                existing_opd = model_class.objects.filter(**filter_opd)
                if pk:
                    existing_opd = existing_opd.exclude(pk=pk)

                realisasi_opd_lain = existing_opd.aggregate(s=Sum(f'{prefix}lpjnilai'))['s'] or Decimal(0)
                accum_opd_lpj = realisasi_opd_lain + nilai_lpj

                if accum_opd_lpj > pagu_opd:
                    sisa_opd = max(Decimal(0), pagu_opd - realisasi_opd_lain)
                    selisih_opd = accum_opd_lpj - pagu_opd
                    raise ValidationError(
                        f"Total Realisasi LPJ untuk {subopd_nama} setelah ditambah saat ini menjadi "
                        f"Rp. {accum_opd_lpj:,.2f}, melebihi Total Pagu Alokasi Kelurahan sebesar "
                        f"Rp. {pagu_opd:,.2f}. "
                        f"(Sisa alokasi pagu tersedia: Rp. {sisa_opd:,.2f}, Kelebihan: Rp. {selisih_opd:,.2f})."
                    )

        # 4. Validasi Distribusi Dana Kelurahan per Tahap & Akumulasi Sisa antar Tahap
        if subopd and dana and tahap:
            tahap_id = getattr(tahap, 'id', tahap)
            try:
                t_int = int(tahap_id)
                tahap_ids = list(range(1, t_int + 1))
            except (ValueError, TypeError):
                tahap_ids = [1]
                t_int = 1

            # Akumulasi distribusi dana yang diinput dari Tahap 1 s/d Tahap saat ini
            distribusi_kumulatif = DistribusiPenerimaan.objects.filter(
                distri_penerimaan__penerimaan_tahun=tahun,
                distri_penerimaan__penerimaan_dana=dana,
                distri_subopd=subopd,
                distri_penerimaan__penerimaan_tahap_id__in=tahap_ids,
            ).aggregate(s=Sum('distri_nilai'))['s'] or Decimal(0)

            if distribusi_kumulatif == 0:
                raise ValidationError(
                    f"Distribusi Penerimaan Dana Kelurahan untuk {subopd_nama} sampai dengan Tahap {t_int} "
                    f"belum diinput. Realisasi tidak dapat disimpan sebelum distribusi dana diinput."
                )

            filter_tahap = {
                f'{prefix}tahun': tahun,
                f'{prefix}dana': dana,
                f'{prefix}subopd': subopd,
                f'{prefix}tahap_id__in': tahap_ids,
            }
            existing_tahap = model_class.objects.filter(**filter_tahap)
            if pk:
                existing_tahap = existing_tahap.exclude(pk=pk)

            # Cek terhadap SP2D TU
            sp2d_tu_lain = existing_tahap.aggregate(s=Sum(f'{prefix}nilai'))['s'] or Decimal(0)
            accum_sp2d_tu = sp2d_tu_lain + nilai_sp2d

            if accum_sp2d_tu > distribusi_kumulatif:
                sisa_sp2d = max(Decimal(0), distribusi_kumulatif - sp2d_tu_lain)
                selisih_sp2d = accum_sp2d_tu - distribusi_kumulatif
                raise ValidationError(
                    f"Total Realisasi Nilai SP2D TU untuk {subopd_nama} s.d. Tahap {t_int} "
                    f"setelah ditambah saat ini menjadi Rp. {accum_sp2d_tu:,.2f}, melebihi akumulasi distribusi dana "
                    f"yang diterima s.d. Tahap {t_int} sebesar Rp. {distribusi_kumulatif:,.2f}. "
                    f"(Sisa dana distribusi tersedia yang dapat direalisasikan: Rp. {sisa_sp2d:,.2f}, Kelebihan: Rp. {selisih_sp2d:,.2f})."
                )

            # Cek terhadap LPJ TU
            lpj_tu_lain = existing_tahap.aggregate(s=Sum(f'{prefix}lpjnilai'))['s'] or Decimal(0)
            accum_lpj_tu = lpj_tu_lain + nilai_lpj

            if accum_lpj_tu > distribusi_kumulatif:
                sisa_lpj = max(Decimal(0), distribusi_kumulatif - lpj_tu_lain)
                selisih_lpj = accum_lpj_tu - distribusi_kumulatif
                raise ValidationError(
                    f"Total Realisasi Nilai LPJ TU untuk {subopd_nama} s.d. Tahap {t_int} "
                    f"setelah ditambah saat ini menjadi Rp. {accum_lpj_tu:,.2f}, melebihi akumulasi distribusi dana "
                    f"yang diterima s.d. Tahap {t_int} sebesar Rp. {distribusi_kumulatif:,.2f}. "
                    f"(Sisa dana distribusi tersedia yang dapat di-LPJ-kan: Rp. {sisa_lpj:,.2f}, Kelebihan: Rp. {selisih_lpj:,.2f})."
                )

