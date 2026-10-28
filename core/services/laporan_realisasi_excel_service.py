import io
from datetime import datetime
from decimal import Decimal

from django.http import HttpResponse

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


class LaporanRealisasiExcelService:
    """
    Service untuk menghasilkan file Excel (.xlsx) Laporan Realisasi
    untuk Bidang Pendidikan, Kesehatan, PU, dan Dana Kelurahan (Utama & Sisa).
    """

    # Palette Warna Styling
    COLOR_HEADER_BG = "1F4E79"        # Dark steel blue
    COLOR_HEADER_TEXT = "FFFFFF"      # White
    COLOR_PROG_BG = "D9E1F2"          # Soft periwinkle blue
    COLOR_KEG_BG = "F2F4F8"           # Light tinted gray
    COLOR_TOTAL_BG = "1F4E79"         # Dark steel blue
    COLOR_TOTAL_TEXT = "FFFFFF"       # White
    COLOR_BORDER = "C0D0E0"           # Subtle blue gray
    COLOR_DARK_BORDER = "1F4E79"

    @classmethod
    def _create_styles(cls):
        font_title = Font(name="Calibri", size=13, bold=True, color="002060")
        font_subtitle = Font(name="Calibri", size=11, bold=True, color="1F4E79")
        font_meta_lbl = Font(name="Calibri", size=9.5, bold=True, color="333333")
        font_meta_val = Font(name="Calibri", size=9.5, color="111111")

        font_header = Font(name="Calibri", size=10, bold=True, color=cls.COLOR_HEADER_TEXT)
        fill_header = PatternFill(start_color=cls.COLOR_HEADER_BG, end_color=cls.COLOR_HEADER_BG, fill_type="solid")

        font_prog = Font(name="Calibri", size=10, bold=True, color="000000")
        fill_prog = PatternFill(start_color=cls.COLOR_PROG_BG, end_color=cls.COLOR_PROG_BG, fill_type="solid")

        font_keg = Font(name="Calibri", size=9.5, bold=True, color="1F2421")
        fill_keg = PatternFill(start_color=cls.COLOR_KEG_BG, end_color=cls.COLOR_KEG_BG, fill_type="solid")

        font_sub = Font(name="Calibri", size=9.5, color="000000")

        font_total = Font(name="Calibri", size=10.5, bold=True, color=cls.COLOR_TOTAL_TEXT)
        fill_total = PatternFill(start_color=cls.COLOR_TOTAL_BG, end_color=cls.COLOR_TOTAL_BG, fill_type="solid")

        thin_side = Side(style="thin", color=cls.COLOR_BORDER)
        border_cell = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)

        double_bottom = Side(style="double", color="000000")
        thin_top = Side(style="thin", color=cls.COLOR_DARK_BORDER)
        border_total = Border(left=thin_side, right=thin_side, top=thin_top, bottom=double_bottom)

        align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
        align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)
        align_right = Alignment(horizontal="right", vertical="center")

        return {
            'font_title': font_title,
            'font_subtitle': font_subtitle,
            'font_meta_lbl': font_meta_lbl,
            'font_meta_val': font_meta_val,
            'font_header': font_header,
            'fill_header': fill_header,
            'font_prog': font_prog,
            'fill_prog': fill_prog,
            'font_keg': font_keg,
            'fill_keg': fill_keg,
            'font_sub': font_sub,
            'font_total': font_total,
            'fill_total': fill_total,
            'border_cell': border_cell,
            'border_total': border_total,
            'align_center': align_center,
            'align_left': align_left,
            'align_right': align_right,
        }

    @staticmethod
    def _clean_str(val, default='-'):
        if val is None:
            return default
        if hasattr(val, 'sub_nama'):
            return val.sub_nama
        if hasattr(val, 'tahap_dana'):
            return val.tahap_dana
        s = str(val).strip()
        return s if s and s not in ('None', 'none', 'null') else default

    @staticmethod
    def _to_num(val):
        if val is None or val == '':
            return 0.0
        try:
            return float(val)
        except (ValueError, TypeError):
            return 0.0

    @classmethod
    def _render_meta_block(cls, ws, styles, max_col_idx, title, subtitle, tahun, dana, tahap, opd):
        max_col_letter = get_column_letter(max_col_idx)

        # Baris 1: Pemerintah
        ws.merge_cells(f"A1:{max_col_letter}1")
        ws["A1"] = "PEMERINTAH KABUPATEN ASAHAN"
        ws["A1"].font = styles['font_title']
        ws["A1"].alignment = styles['align_center']

        # Baris 2: Judul
        ws.merge_cells(f"A2:{max_col_letter}2")
        ws["A2"] = title.upper()
        ws["A2"].font = styles['font_subtitle']
        ws["A2"].alignment = styles['align_center']

        # Baris 3: Subjudul
        if subtitle:
            ws.merge_cells(f"A3:{max_col_letter}3")
            ws["A3"] = subtitle
            ws["A3"].font = styles['font_meta_lbl']
            ws["A3"].alignment = styles['align_center']

        # Baris 4: Informasi Filter / Metadata
        ws["A5"] = "Tahun Anggaran"
        ws["A5"].font = styles['font_meta_lbl']
        ws["B5"] = f": {tahun}"
        ws["B5"].font = styles['font_meta_val']

        ws["D5"] = "Sumber Dana"
        ws["D5"].font = styles['font_meta_lbl']
        ws["E5"] = f": {dana}"
        ws["E5"].font = styles['font_meta_val']

        ws["A6"] = "Tahap Pencairan"
        ws["A6"].font = styles['font_meta_lbl']
        ws["B6"] = f": {tahap}"
        ws["B6"].font = styles['font_meta_val']

        ws["D6"] = "OPD / SKPD"
        ws["D6"].font = styles['font_meta_lbl']
        ws["E6"] = f": {opd}"
        ws["E6"].font = styles['font_meta_val']

    @classmethod
    def export_standard(cls, context, jenis_dana='pendidikan', sumber='utama'):
        """
        Export Laporan Realisasi untuk Bidang Pendidikan, Kesehatan, dan PU (Utama & Sisa).
        Pendidikan & Kesehatan memiliki 5 Tahap realisasi, PU memiliki 3 Tahap realisasi.
        """
        wb = openpyxl.Workbook()
        ws = wb.active

        # Tentukan label dan judul berdasarkan parameter
        labels = {
            'pendidikan': 'Bidang Pendidikan',
            'kesehatan': 'Bidang Kesehatan',
            'pu': 'Bidang Pekerjaan Umum',
        }
        bidang_label = labels.get(jenis_dana, jenis_dana.title())
        sumber_label = "Sisa Tahun Lalu" if sumber == 'sisa' else "Tahun Berjalan"

        title = f"Rekapitulasi Realisasi DAU SG {bidang_label}"
        if sumber == 'sisa':
            title += " (Sisa Tahun Lalu)"
        ws.title = f"Realisasi {bidang_label[:15]}"

        # Metadata
        tahun = cls._clean_str(context.get('realisasi_tahun'))
        dana = cls._clean_str(context.get('realisasi_dana'))
        tahap = cls._clean_str(context.get('realisasi_tahap'))
        opd = cls._clean_str(context.get('realisasi_subopd'))

        styles = cls._create_styles()

        # Deteksi jumlah tahap: PU = 3 tahap, Pendidikan & Kesehatan = 5 tahap
        is_3_tahap = (jenis_dana == 'pu') and ('total_tahap4_keseluruhan' not in context)
        num_tahaps = 3 if is_3_tahap else 5

        # Hitung total kolom
        # Kolom: No(A), Program/Kegiatan/Sub(B), OPD(C), Pagu(D), Output(E), [Tahap 1..N], Total Realisasi, Output Realisasi, Satuan
        # Jika 5 tahap: 13 kolom (A s.d. M)
        # Jika 3 tahap: 11 kolom (A s.d. K)
        total_cols = 5 + num_tahaps + 3

        cls._render_meta_block(
            ws, styles, total_cols,
            title=title,
            subtitle=f"DAU Yang Ditentukan Penggunaannya - {sumber_label}",
            tahun=tahun, dana=dana, tahap=tahap, opd=opd
        )

        header_row_1 = 8
        header_row_2 = 9

        # Set Header Row 1
        ws.cell(row=header_row_1, column=1, value="No")
        ws.merge_cells(start_row=header_row_1, start_column=1, end_row=header_row_2, end_column=1)

        ws.cell(row=header_row_1, column=2, value="Nama Program / Kegiatan / Sub Kegiatan")
        ws.merge_cells(start_row=header_row_1, start_column=2, end_row=header_row_2, end_column=2)

        ws.cell(row=header_row_1, column=3, value="OPD Pengelola")
        ws.merge_cells(start_row=header_row_1, start_column=3, end_row=header_row_2, end_column=3)

        ws.cell(row=header_row_1, column=4, value="Rencana")
        ws.merge_cells(start_row=header_row_1, start_column=4, end_row=header_row_1, end_column=5)

        ws.cell(row=header_row_1, column=6, value="Realisasi")
        ws.merge_cells(start_row=header_row_1, start_column=6, end_row=header_row_1, end_column=5 + num_tahaps + 2)

        satuan_col = total_cols
        ws.cell(row=header_row_1, column=satuan_col, value="Satuan")
        ws.merge_cells(start_row=header_row_1, start_column=satuan_col, end_row=header_row_2, end_column=satuan_col)

        # Set Header Row 2
        ws.cell(row=header_row_2, column=4, value="Pagu (Rp)")
        ws.cell(row=header_row_2, column=5, value="Output")

        for t_idx in range(1, num_tahaps + 1):
            ws.cell(row=header_row_2, column=5 + t_idx, value=f"Tahap {t_idx} (Rp)")

        total_real_col = 5 + num_tahaps + 1
        out_real_col = 5 + num_tahaps + 2
        ws.cell(row=header_row_2, column=total_real_col, value="Total Realisasi (Rp)")
        ws.cell(row=header_row_2, column=out_real_col, value="Output Realisasi")

        # Styling kedua baris header
        for r in (header_row_1, header_row_2):
            ws.row_dimensions[r].height = 24
            for c in range(1, total_cols + 1):
                cell = ws.cell(row=r, column=c)
                cell.font = styles['font_header']
                cell.fill = styles['fill_header']
                cell.alignment = styles['align_center']
                cell.border = styles['border_cell']

        # Render Isi Data Tabel
        current_row = 10
        prog_data = context.get('prog_data', [])

        for prog in prog_data:
            # Ambil nama program
            prog_obj = prog.get('prog')
            prog_nama = getattr(prog_obj, f"dausg{jenis_dana}_prog", None) or str(prog_obj or '')

            # Row Program
            ws.row_dimensions[current_row].height = 20
            ws.cell(row=current_row, column=1, value=str(prog.get('prog_number') or ''))
            ws.cell(row=current_row, column=2, value=prog_nama)
            ws.cell(row=current_row, column=3, value="")
            ws.cell(row=current_row, column=4, value=cls._to_num(prog.get('total_pagu_prog')))
            ws.cell(row=current_row, column=5, value=cls._to_num(prog.get('total_output_prog')))

            for t_idx in range(1, num_tahaps + 1):
                ws.cell(row=current_row, column=5 + t_idx, value=cls._to_num(prog.get(f'total_tahap{t_idx}_prog')))

            ws.cell(row=current_row, column=total_real_col, value=cls._to_num(prog.get('total_realisasi_prog')))
            ws.cell(row=current_row, column=out_real_col, value=cls._to_num(prog.get('total_realisasi_output_prog')))
            ws.cell(row=current_row, column=satuan_col, value="")

            # Styling row program
            for c in range(1, total_cols + 1):
                cell = ws.cell(row=current_row, column=c)
                cell.font = styles['font_prog']
                cell.fill = styles['fill_prog']
                cell.border = styles['border_cell']
                if c == 1:
                    cell.alignment = styles['align_center']
                elif c in (2, 3):
                    cell.alignment = styles['align_left']
                elif c in (5, out_real_col):
                    cell.alignment = styles['align_center']
                    cell.number_format = '#,##0.00'
                else:
                    cell.alignment = styles['align_right']
                    cell.number_format = '#,##0.00'

            current_row += 1

            for keg in prog.get('kegs', []):
                keg_obj = keg.get('keg')
                keg_nama = getattr(keg_obj, f"dausg{jenis_dana}keg_nama", None) or str(keg_obj or '')

                # Row Kegiatan
                ws.row_dimensions[current_row].height = 19
                ws.cell(row=current_row, column=1, value=str(keg.get('kegiatan_number') or ''))
                ws.cell(row=current_row, column=2, value=f"   {keg_nama}")
                ws.cell(row=current_row, column=3, value="")
                ws.cell(row=current_row, column=4, value=cls._to_num(keg.get('total_pagu_keg')))
                ws.cell(row=current_row, column=5, value=cls._to_num(keg.get('total_output_keg')))

                for t_idx in range(1, num_tahaps + 1):
                    ws.cell(row=current_row, column=5 + t_idx, value=cls._to_num(keg.get(f'total_tahap{t_idx}_keg')))

                ws.cell(row=current_row, column=total_real_col, value=cls._to_num(keg.get('total_realisasi_keg')))
                ws.cell(row=current_row, column=out_real_col, value=cls._to_num(keg.get('total_realisasi_output_keg')))
                ws.cell(row=current_row, column=satuan_col, value="")

                # Styling row kegiatan
                for c in range(1, total_cols + 1):
                    cell = ws.cell(row=current_row, column=c)
                    cell.font = styles['font_keg']
                    cell.fill = styles['fill_keg']
                    cell.border = styles['border_cell']
                    if c == 1:
                        cell.alignment = styles['align_center']
                    elif c in (2, 3):
                        cell.alignment = styles['align_left']
                    elif c in (5, out_real_col):
                        cell.alignment = styles['align_center']
                        cell.number_format = '#,##0.00'
                    else:
                        cell.alignment = styles['align_right']
                        cell.number_format = '#,##0.00'

                current_row += 1

                for sub in keg.get('subs', []):
                    sub_obj = sub.get('sub')
                    sub_nama = getattr(sub_obj, f"dausg{jenis_dana}sub_nama", None) or str(sub_obj or '')
                    sub_satuan = getattr(sub_obj, f"dausg{jenis_dana}sub_satuan", '') or getattr(sub_obj, 'satuan', '')

                    posting_subopd = sub.get('posting_subopd')
                    opd_nama = cls._clean_str(posting_subopd)

                    realisasi_dict = sub.get('realisasi', {})

                    # Row Sub Kegiatan
                    ws.row_dimensions[current_row].height = 18
                    ws.cell(row=current_row, column=1, value=str(sub.get('sub_number') or ''))
                    ws.cell(row=current_row, column=2, value=f"      {sub_nama}")
                    ws.cell(row=current_row, column=3, value=opd_nama)
                    ws.cell(row=current_row, column=4, value=cls._to_num(sub.get('pagu')))
                    ws.cell(row=current_row, column=5, value=cls._to_num(sub.get('output')))

                    for t_idx in range(1, num_tahaps + 1):
                        ws.cell(row=current_row, column=5 + t_idx, value=cls._to_num(realisasi_dict.get(f'tahap{t_idx}')))

                    ws.cell(row=current_row, column=total_real_col, value=cls._to_num(realisasi_dict.get('total_sp2d')))
                    ws.cell(row=current_row, column=out_real_col, value=cls._to_num(realisasi_dict.get('total_output')))
                    ws.cell(row=current_row, column=satuan_col, value=str(sub_satuan))

                    # Styling row sub kegiatan
                    for c in range(1, total_cols + 1):
                        cell = ws.cell(row=current_row, column=c)
                        cell.font = styles['font_sub']
                        cell.border = styles['border_cell']
                        if c in (1, satuan_col):
                            cell.alignment = styles['align_center']
                        elif c in (2, 3):
                            cell.alignment = styles['align_left']
                        elif c in (5, out_real_col):
                            cell.alignment = styles['align_center']
                            cell.number_format = '#,##0.00'
                        else:
                            cell.alignment = styles['align_right']
                            cell.number_format = '#,##0.00'

                    current_row += 1

        # Total Keseluruhan
        ws.row_dimensions[current_row].height = 24
        ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=3)
        ws.cell(row=current_row, column=1, value="TOTAL KESELURUHAN")

        ws.cell(row=current_row, column=4, value=cls._to_num(context.get('total_pagu_keseluruhan')))
        ws.cell(row=current_row, column=5, value=cls._to_num(context.get('total_output_keseluruhan')))

        for t_idx in range(1, num_tahaps + 1):
            ws.cell(row=current_row, column=5 + t_idx, value=cls._to_num(context.get(f'total_tahap{t_idx}_keseluruhan')))

        ws.cell(row=current_row, column=total_real_col, value=cls._to_num(context.get('total_realisasi_keseluruhan')))
        ws.cell(row=current_row, column=out_real_col, value=cls._to_num(context.get('total_realisasi_output_keseluruhan')))
        ws.cell(row=current_row, column=satuan_col, value="")

        for c in range(1, total_cols + 1):
            cell = ws.cell(row=current_row, column=c)
            cell.font = styles['font_total']
            cell.fill = styles['fill_total']
            cell.border = styles['border_total']
            if c <= 3:
                cell.alignment = styles['align_center']
            elif c in (5, out_real_col):
                cell.alignment = styles['align_center']
                cell.number_format = '#,##0.00'
            elif c == satuan_col:
                cell.alignment = styles['align_center']
            else:
                cell.alignment = styles['align_right']
                cell.number_format = '#,##0.00'

        # Auto-adjust column widths
        cls._adjust_column_widths(ws, start_row=8, total_cols=total_cols)

        # Output file
        filename = f"Laporan_Realisasi_{bidang_label.replace(' ', '_')}_{sumber.title()}_{tahun}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return cls._create_response(wb, filename)

    @classmethod
    def export_dankel_utama(cls, context):
        """
        Export Laporan Realisasi untuk Dana Kelurahan (Utama).
        Kolom: Program, Kegiatan, Sub Kegiatan, Pagu, Output, Tahap 1, Tahap 2, Total, Sisa, Output Realisasi, Satuan.
        """
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Realisasi Dana Kelurahan"

        title = "Rekapitulasi Realisasi Dana Kelurahan"
        subtitle = "DAU Dukungan Pembangunan Sarana dan Prasarana, dan Pemberdayaan Masyarakat di Kelurahan"

        tahun = cls._clean_str(context.get('tahunrealisasi'))
        dana = cls._clean_str(context.get('danarealisasi_id'))
        tahap = cls._clean_str(context.get('tahaprealisasi_id'))
        opd = cls._clean_str(context.get('subopdrealisasi_id'))

        styles = cls._create_styles()
        total_cols = 11

        cls._render_meta_block(
            ws, styles, total_cols,
            title=title, subtitle=subtitle,
            tahun=tahun, dana=dana, tahap=tahap, opd=opd
        )

        header_row_1 = 8
        header_row_2 = 9

        # Header Row 1
        ws.cell(row=header_row_1, column=1, value="Uraian Kegiatan")
        ws.merge_cells(start_row=header_row_1, start_column=1, end_row=header_row_1, end_column=3)

        ws.cell(row=header_row_1, column=4, value="Rencana")
        ws.merge_cells(start_row=header_row_1, start_column=4, end_row=header_row_1, end_column=5)

        ws.cell(row=header_row_1, column=6, value="Realisasi")
        ws.merge_cells(start_row=header_row_1, start_column=6, end_row=header_row_1, end_column=11)

        # Header Row 2
        ws.cell(row=header_row_2, column=1, value="Program")
        ws.cell(row=header_row_2, column=2, value="Kegiatan")
        ws.cell(row=header_row_2, column=3, value="Sub Kegiatan")
        ws.cell(row=header_row_2, column=4, value="Pagu (Rp)")
        ws.cell(row=header_row_2, column=5, value="Output")
        ws.cell(row=header_row_2, column=6, value="Tahap 1 (Rp)")
        ws.cell(row=header_row_2, column=7, value="Tahap 2 (Rp)")
        ws.cell(row=header_row_2, column=8, value="Total Realisasi (Rp)")
        ws.cell(row=header_row_2, column=9, value="Sisa (Rp)")
        ws.cell(row=header_row_2, column=10, value="Output")
        ws.cell(row=header_row_2, column=11, value="Satuan")

        for r in (header_row_1, header_row_2):
            ws.row_dimensions[r].height = 24
            for c in range(1, total_cols + 1):
                cell = ws.cell(row=r, column=c)
                cell.font = styles['font_header']
                cell.fill = styles['fill_header']
                cell.alignment = styles['align_center']
                cell.border = styles['border_cell']

        current_row = 10
        prog_data = context.get('prog_data', [])

        for prog in prog_data:
            prog_obj = prog.get('prog')
            prog_nama = getattr(prog_obj, 'dankel_prog', None) or str(prog_obj or '')

            ws.row_dimensions[current_row].height = 20
            ws.cell(row=current_row, column=1, value=prog_nama)
            ws.cell(row=current_row, column=2, value="")
            ws.cell(row=current_row, column=3, value="")
            ws.cell(row=current_row, column=4, value=cls._to_num(prog.get('total_pagu_prog')))
            ws.cell(row=current_row, column=5, value=cls._to_num(prog.get('total_output_prog')))
            ws.cell(row=current_row, column=6, value=cls._to_num(prog.get('total_t1_prog')))
            ws.cell(row=current_row, column=7, value=cls._to_num(prog.get('total_t2_prog')))
            ws.cell(row=current_row, column=8, value=cls._to_num(prog.get('total_realisasi_prog')))
            ws.cell(row=current_row, column=9, value=cls._to_num(prog.get('sisa_prog')))
            ws.cell(row=current_row, column=10, value=cls._to_num(prog.get('total_realisasi_output_prog')))
            ws.cell(row=current_row, column=11, value="")

            for c in range(1, total_cols + 1):
                cell = ws.cell(row=current_row, column=c)
                cell.font = styles['font_prog']
                cell.fill = styles['fill_prog']
                cell.border = styles['border_cell']
                if c <= 3:
                    cell.alignment = styles['align_left']
                elif c in (5, 10):
                    cell.alignment = styles['align_center']
                    cell.number_format = '#,##0.00'
                elif c == 11:
                    cell.alignment = styles['align_center']
                else:
                    cell.alignment = styles['align_right']
                    cell.number_format = '#,##0.00'

            current_row += 1

            for keg in prog.get('kegs', []):
                keg_obj = keg.get('keg')
                keg_nama = getattr(keg_obj, 'dankelkeg_nama', None) or str(keg_obj or '')

                ws.row_dimensions[current_row].height = 19
                ws.cell(row=current_row, column=1, value="")
                ws.cell(row=current_row, column=2, value=keg_nama)
                ws.cell(row=current_row, column=3, value="")
                ws.cell(row=current_row, column=4, value=cls._to_num(keg.get('total_pagu_keg')))
                ws.cell(row=current_row, column=5, value=cls._to_num(keg.get('total_output_keg')))
                ws.cell(row=current_row, column=6, value=cls._to_num(keg.get('total_t1_keg')))
                ws.cell(row=current_row, column=7, value=cls._to_num(keg.get('total_t2_keg')))
                ws.cell(row=current_row, column=8, value=cls._to_num(keg.get('total_realisasi_keg')))
                ws.cell(row=current_row, column=9, value=cls._to_num(keg.get('sisa_keg')))
                ws.cell(row=current_row, column=10, value=cls._to_num(keg.get('total_realisasi_output_keg')))
                ws.cell(row=current_row, column=11, value="")

                for c in range(1, total_cols + 1):
                    cell = ws.cell(row=current_row, column=c)
                    cell.font = styles['font_keg']
                    cell.fill = styles['fill_keg']
                    cell.border = styles['border_cell']
                    if c <= 3:
                        cell.alignment = styles['align_left']
                    elif c in (5, 10):
                        cell.alignment = styles['align_center']
                        cell.number_format = '#,##0.00'
                    elif c == 11:
                        cell.alignment = styles['align_center']
                    else:
                        cell.alignment = styles['align_right']
                        cell.number_format = '#,##0.00'

                current_row += 1

                for sub in keg.get('subs', []):
                    sub_obj = sub.get('sub')
                    sub_nama = getattr(sub_obj, 'dankelsub_nama', None) or str(sub_obj or '')
                    sub_satuan = getattr(sub_obj, 'dankelsub_satuan', '') or ''

                    realisasi_dict = sub.get('realisasi', {})

                    ws.row_dimensions[current_row].height = 18
                    ws.cell(row=current_row, column=1, value="")
                    ws.cell(row=current_row, column=2, value="")
                    ws.cell(row=current_row, column=3, value=sub_nama)
                    ws.cell(row=current_row, column=4, value=cls._to_num(sub.get('pagu')))
                    ws.cell(row=current_row, column=5, value=cls._to_num(sub.get('output')))
                    ws.cell(row=current_row, column=6, value=cls._to_num(realisasi_dict.get('total_t1')))
                    ws.cell(row=current_row, column=7, value=cls._to_num(realisasi_dict.get('total_t2')))
                    ws.cell(row=current_row, column=8, value=cls._to_num(realisasi_dict.get('total_lpj')))
                    ws.cell(row=current_row, column=9, value=cls._to_num(sub.get('sisa')))
                    ws.cell(row=current_row, column=10, value=cls._to_num(realisasi_dict.get('total_output')))
                    ws.cell(row=current_row, column=11, value=str(sub_satuan))

                    for c in range(1, total_cols + 1):
                        cell = ws.cell(row=current_row, column=c)
                        cell.font = styles['font_sub']
                        cell.border = styles['border_cell']
                        if c <= 3:
                            cell.alignment = styles['align_left']
                        elif c in (5, 10):
                            cell.alignment = styles['align_center']
                            cell.number_format = '#,##0.00'
                        elif c == 11:
                            cell.alignment = styles['align_center']
                        else:
                            cell.alignment = styles['align_right']
                            cell.number_format = '#,##0.00'

                    current_row += 1

        # Total Keseluruhan
        ws.row_dimensions[current_row].height = 24
        ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=3)
        ws.cell(row=current_row, column=1, value="TOTAL KESELURUHAN")

        ws.cell(row=current_row, column=4, value=cls._to_num(context.get('total_pagu_keseluruhan')))
        ws.cell(row=current_row, column=5, value=cls._to_num(context.get('total_output_keseluruhan')))
        ws.cell(row=current_row, column=6, value=cls._to_num(context.get('total_t1_keseluruhan')))
        ws.cell(row=current_row, column=7, value=cls._to_num(context.get('total_t2_keseluruhan')))
        ws.cell(row=current_row, column=8, value=cls._to_num(context.get('total_realisasi_keseluruhan')))
        ws.cell(row=current_row, column=9, value=cls._to_num(context.get('sisa_keseluruhan')))
        ws.cell(row=current_row, column=10, value=cls._to_num(context.get('total_realisasi_output_keseluruhan')))
        ws.cell(row=current_row, column=11, value="")

        for c in range(1, total_cols + 1):
            cell = ws.cell(row=current_row, column=c)
            cell.font = styles['font_total']
            cell.fill = styles['fill_total']
            cell.border = styles['border_total']
            if c <= 3:
                cell.alignment = styles['align_center']
            elif c in (5, 10):
                cell.alignment = styles['align_center']
                cell.number_format = '#,##0.00'
            elif c == 11:
                cell.alignment = styles['align_center']
            else:
                cell.alignment = styles['align_right']
                cell.number_format = '#,##0.00'

        cls._adjust_column_widths(ws, start_row=8, total_cols=total_cols)

        filename = f"Laporan_Realisasi_Dana_Kelurahan_{tahun}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return cls._create_response(wb, filename)

    @classmethod
    def export_dankel_sisa(cls, context):
        """
        Export Laporan Realisasi untuk Sisa Dana Kelurahan.
        Kolom: Program, Kegiatan, Sub Kegiatan, Pagu Rencana, Output Rencana, Satuan, Realisasi LPJ, Output Realisasi, Satuan.
        """
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Realisasi Sisa Dana Kelurahan"

        title = "Rekapitulasi Realisasi Sisa Dana Kelurahan"
        subtitle = "Laporan Realisasi Belanja Sisa Dana Kelurahan Tahun Lalu"

        tahun = cls._clean_str(context.get('tahunrealisasi') or context.get('tahunrealisasisisa'))
        dana = cls._clean_str(context.get('danarealisasi_id') or context.get('danarealisasisisa_id'))
        tahap = cls._clean_str(context.get('tahaprealisasi_id') or context.get('tahaprealisasisisa_id'))
        opd = cls._clean_str(context.get('subopdrealisasi_id') or context.get('subopdrealisasisisa_id'))

        styles = cls._create_styles()
        total_cols = 9

        cls._render_meta_block(
            ws, styles, total_cols,
            title=title, subtitle=subtitle,
            tahun=tahun, dana=dana, tahap=tahap, opd=opd
        )

        header_row_1 = 8
        header_row_2 = 9

        # Header Row 1
        ws.cell(row=header_row_1, column=1, value="Uraian Kegiatan")
        ws.merge_cells(start_row=header_row_1, start_column=1, end_row=header_row_1, end_column=3)

        ws.cell(row=header_row_1, column=4, value="Rencana Sisa")
        ws.merge_cells(start_row=header_row_1, start_column=4, end_row=header_row_1, end_column=6)

        ws.cell(row=header_row_1, column=7, value="Realisasi")
        ws.merge_cells(start_row=header_row_1, start_column=7, end_row=header_row_1, end_column=9)

        # Header Row 2
        ws.cell(row=header_row_2, column=1, value="Program")
        ws.cell(row=header_row_2, column=2, value="Kegiatan")
        ws.cell(row=header_row_2, column=3, value="Sub Kegiatan")
        ws.cell(row=header_row_2, column=4, value="Pagu (Rp)")
        ws.cell(row=header_row_2, column=5, value="Output")
        ws.cell(row=header_row_2, column=6, value="Satuan")
        ws.cell(row=header_row_2, column=7, value="Realisasi LPJ (Rp)")
        ws.cell(row=header_row_2, column=8, value="Output")
        ws.cell(row=header_row_2, column=9, value="Satuan")

        for r in (header_row_1, header_row_2):
            ws.row_dimensions[r].height = 24
            for c in range(1, total_cols + 1):
                cell = ws.cell(row=r, column=c)
                cell.font = styles['font_header']
                cell.fill = styles['fill_header']
                cell.alignment = styles['align_center']
                cell.border = styles['border_cell']

        current_row = 10
        prog_data = context.get('prog_data', [])

        for prog in prog_data:
            prog_obj = prog.get('prog')
            prog_nama = getattr(prog_obj, 'dankel_prog', None) or str(prog_obj or '')

            ws.row_dimensions[current_row].height = 20
            ws.cell(row=current_row, column=1, value=prog_nama)
            ws.cell(row=current_row, column=2, value="")
            ws.cell(row=current_row, column=3, value="")
            ws.cell(row=current_row, column=4, value=cls._to_num(prog.get('total_pagu_prog')))
            ws.cell(row=current_row, column=5, value=cls._to_num(prog.get('total_output_prog')))
            ws.cell(row=current_row, column=6, value="")
            ws.cell(row=current_row, column=7, value=cls._to_num(prog.get('total_realisasi_prog')))
            ws.cell(row=current_row, column=8, value=cls._to_num(prog.get('total_realisasi_output_prog')))
            ws.cell(row=current_row, column=9, value="")

            for c in range(1, total_cols + 1):
                cell = ws.cell(row=current_row, column=c)
                cell.font = styles['font_prog']
                cell.fill = styles['fill_prog']
                cell.border = styles['border_cell']
                if c <= 3:
                    cell.alignment = styles['align_left']
                elif c in (5, 8):
                    cell.alignment = styles['align_center']
                    cell.number_format = '#,##0.00'
                elif c in (6, 9):
                    cell.alignment = styles['align_center']
                else:
                    cell.alignment = styles['align_right']
                    cell.number_format = '#,##0.00'

            current_row += 1

            for keg in prog.get('kegs', []):
                keg_obj = keg.get('keg')
                keg_nama = getattr(keg_obj, 'dankelkeg_nama', None) or str(keg_obj or '')

                ws.row_dimensions[current_row].height = 19
                ws.cell(row=current_row, column=1, value="")
                ws.cell(row=current_row, column=2, value=keg_nama)
                ws.cell(row=current_row, column=3, value="")
                ws.cell(row=current_row, column=4, value=cls._to_num(keg.get('total_pagu_keg')))
                ws.cell(row=current_row, column=5, value=cls._to_num(keg.get('total_output_keg')))
                ws.cell(row=current_row, column=6, value="")
                ws.cell(row=current_row, column=7, value=cls._to_num(keg.get('total_realisasi_keg')))
                ws.cell(row=current_row, column=8, value=cls._to_num(keg.get('total_realisasi_output_keg')))
                ws.cell(row=current_row, column=9, value="")

                for c in range(1, total_cols + 1):
                    cell = ws.cell(row=current_row, column=c)
                    cell.font = styles['font_keg']
                    cell.fill = styles['fill_keg']
                    cell.border = styles['border_cell']
                    if c <= 3:
                        cell.alignment = styles['align_left']
                    elif c in (5, 8):
                        cell.alignment = styles['align_center']
                        cell.number_format = '#,##0.00'
                    elif c in (6, 9):
                        cell.alignment = styles['align_center']
                    else:
                        cell.alignment = styles['align_right']
                        cell.number_format = '#,##0.00'

                current_row += 1

                for sub in keg.get('subs', []):
                    sub_obj = sub.get('sub')
                    sub_nama = getattr(sub_obj, 'dankelsub_nama', None) or str(sub_obj or '')
                    sub_satuan = getattr(sub_obj, 'dankelsub_satuan', '') or ''

                    realisasi_dict = sub.get('realisasi', {})

                    ws.row_dimensions[current_row].height = 18
                    ws.cell(row=current_row, column=1, value="")
                    ws.cell(row=current_row, column=2, value="")
                    ws.cell(row=current_row, column=3, value=sub_nama)
                    ws.cell(row=current_row, column=4, value=cls._to_num(sub.get('pagu')))
                    ws.cell(row=current_row, column=5, value=cls._to_num(sub.get('output')))
                    ws.cell(row=current_row, column=6, value=str(sub_satuan))
                    ws.cell(row=current_row, column=7, value=cls._to_num(realisasi_dict.get('total_lpj')))
                    ws.cell(row=current_row, column=8, value=cls._to_num(realisasi_dict.get('total_output')))
                    ws.cell(row=current_row, column=9, value=str(sub_satuan))

                    for c in range(1, total_cols + 1):
                        cell = ws.cell(row=current_row, column=c)
                        cell.font = styles['font_sub']
                        cell.border = styles['border_cell']
                        if c <= 3:
                            cell.alignment = styles['align_left']
                        elif c in (5, 8):
                            cell.alignment = styles['align_center']
                            cell.number_format = '#,##0.00'
                        elif c in (6, 9):
                            cell.alignment = styles['align_center']
                        else:
                            cell.alignment = styles['align_right']
                            cell.number_format = '#,##0.00'

                    current_row += 1

        # Total Keseluruhan
        ws.row_dimensions[current_row].height = 24
        ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=3)
        ws.cell(row=current_row, column=1, value="TOTAL KESELURUHAN")

        ws.cell(row=current_row, column=4, value=cls._to_num(context.get('total_pagu_keseluruhan')))
        ws.cell(row=current_row, column=5, value=cls._to_num(context.get('total_output_keseluruhan')))
        ws.cell(row=current_row, column=6, value="")
        ws.cell(row=current_row, column=7, value=cls._to_num(context.get('total_realisasi_keseluruhan')))
        ws.cell(row=current_row, column=8, value=cls._to_num(context.get('total_realisasi_output_keseluruhan')))
        ws.cell(row=current_row, column=9, value="")

        for c in range(1, total_cols + 1):
            cell = ws.cell(row=current_row, column=c)
            cell.font = styles['font_total']
            cell.fill = styles['fill_total']
            cell.border = styles['border_total']
            if c <= 3:
                cell.alignment = styles['align_center']
            elif c in (5, 8):
                cell.alignment = styles['align_center']
                cell.number_format = '#,##0.00'
            elif c in (6, 9):
                cell.alignment = styles['align_center']
            else:
                cell.alignment = styles['align_right']
                cell.number_format = '#,##0.00'

        cls._adjust_column_widths(ws, start_row=8, total_cols=total_cols)

        filename = f"Laporan_Realisasi_Sisa_Dana_Kelurahan_{tahun}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return cls._create_response(wb, filename)

    @classmethod
    def _adjust_column_widths(cls, ws, start_row, total_cols):
        for col_idx in range(1, total_cols + 1):
            col_letter = get_column_letter(col_idx)
            max_len = 0
            for row_idx in range(start_row, ws.max_row + 1):
                val = ws.cell(row=row_idx, column=col_idx).value
                if val is not None:
                    s = str(val)
                    if isinstance(val, (int, float)):
                        s = f"{val:,.2f}"
                    max_len = max(max_len, len(s))
            ws.column_dimensions[col_letter].width = max(max_len + 3, 11)

    @classmethod
    def _create_response(cls, wb, filename):
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        response = HttpResponse(
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

