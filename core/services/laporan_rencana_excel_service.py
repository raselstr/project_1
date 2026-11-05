import io
from datetime import datetime
from decimal import Decimal

from django.http import HttpResponse

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


class LaporanRencanaExcelService:
    """
    Service untuk menghasilkan file Excel (.xlsx) Laporan Rencana Kegiatan
    untuk Bidang Pendidikan, Kesehatan, PU, dan Dana Kelurahan (Utama & Sisa).
    Mendukung mode Induk biasa dan mode Perbandingan (Induk vs Perubahan).
    Semua teks menggunakan font Arial yang bersih, jelas, dan rapi.
    """

    COLOR_HEADER_BG = "1F4E79"        # Dark steel blue
    COLOR_HEADER_TEXT = "FFFFFF"      # White
    COLOR_SUBHEADER_BG = "2E75B6"     # Medium blue
    COLOR_TOTAL_BG = "1F4E79"         # Dark steel blue
    COLOR_TOTAL_TEXT = "FFFFFF"       # White
    COLOR_BORDER = "C0D0E0"           # Subtle blue gray
    COLOR_DARK_BORDER = "1F4E79"
    COLOR_ZEBRA = "F7F9FC"            # Subtle alternating row

    @classmethod
    def _create_styles(cls):
        font_title = Font(name="Arial", size=13, bold=True, color="002060")
        font_subtitle = Font(name="Arial", size=11, bold=True, color="1F4E79")
        font_meta_lbl = Font(name="Arial", size=9.5, bold=True, color="333333")
        font_meta_val = Font(name="Arial", size=9.5, color="111111")

        font_header = Font(name="Arial", size=10, bold=True, color=cls.COLOR_HEADER_TEXT)
        fill_header = PatternFill(start_color=cls.COLOR_HEADER_BG, end_color=cls.COLOR_HEADER_BG, fill_type="solid")
        fill_subheader = PatternFill(start_color=cls.COLOR_SUBHEADER_BG, end_color=cls.COLOR_SUBHEADER_BG, fill_type="solid")

        font_data = Font(name="Arial", size=9.5, color="000000")
        font_data_bold = Font(name="Arial", size=9.5, bold=True, color="000000")
        fill_zebra = PatternFill(start_color=cls.COLOR_ZEBRA, end_color=cls.COLOR_ZEBRA, fill_type="solid")

        font_total = Font(name="Arial", size=10.5, bold=True, color=cls.COLOR_TOTAL_TEXT)
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
            'fill_subheader': fill_subheader,
            'font_data': font_data,
            'font_data_bold': font_data_bold,
            'fill_zebra': fill_zebra,
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
        if callable(val):
            try:
                val = val()
            except Exception:
                pass
        if hasattr(val, 'sub_nama'):
            return val.sub_nama
        if hasattr(val, 'uraian'):
            return val.uraian
        if hasattr(val, 'keg_nama'):
            return val.keg_nama
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

    @classmethod
    def export(cls, context, bidang='pendidikan', sumber='utama'):
        """
        Export Laporan Rencana Kegiatan ke format Excel (.xlsx).
        Mendukung:
          - bidang: 'pendidikan', 'kesehatan', 'pu', 'dankel'
          - sumber: 'utama', 'sisa'
          - mode: otomatis mendeteksi is_perubahan (Induk vs Perubahan)
        """
        wb = openpyxl.Workbook()
        ws = wb.active

        labels = {
            'pendidikan': 'Bidang Pendidikan',
            'kesehatan': 'Bidang Kesehatan',
            'pu': 'Bidang Pekerjaan Umum',
            'dankel': 'Dana Kelurahan',
        }
        bidang_label = labels.get(bidang, bidang.title())
        sumber_label = "Sisa Tahun Lalu" if sumber == 'sisa' else "Tahun Berjalan"

        ws.title = f"Rencana {bidang_label[:15]}"
        styles = cls._create_styles()

        is_draft_changed = bool(context.get('is_draft_changed'))
        is_perubahan = bool(context.get('is_perubahan')) or is_draft_changed
        lbl_semula = "Semula (Terposting)" if is_draft_changed else "Semula (Induk)"
        lbl_menjadi = "Menjadi (Draft)" if is_draft_changed else "Menjadi (Perubahan)"
        lbl_selisih = "Selisih (+/-)" if is_draft_changed else "Perubahan (+/-)"
        data = context.get('data') or []

        tahun = cls._clean_str(context.get('rencana_tahun') or context.get('tahun') or context.get('sesitahun'))
        dana = cls._clean_str(context.get('rencana_dana') or context.get('dana'))
        opd = cls._clean_str(context.get('rencana_subopd') or context.get('subopd') or context.get('sesiidopd') or 'Semua OPD')

        # Tentukan kolom-kolom tabel
        is_dankel = (bidang == 'dankel')

        if is_perubahan:
            if is_dankel:
                # Kolom Dankel Perubahan:
                # 1: No, 2: Sub OPD, 3: Kegiatan, 4: Sub Kegiatan,
                # 5: Semula Pagu, 6: Semula Output, 7: Menjadi Pagu, 8: Menjadi Output,
                # 9: Selisih Pagu, 10: Selisih Output, 11: Satuan, 12: Keterangan
                total_cols = 12
            else:
                # Kolom Pendidikan / Kesehatan / PU Perubahan:
                # 1: No, 2: OPD, 3: Sub Kegiatan,
                # 4: Semula Pagu, 5: Semula Output, 6: Menjadi Pagu, 7: Menjadi Output,
                # 8: Selisih Pagu, 9: Selisih Output, 10: Satuan, 11: Kode DPA Kegiatan, 12: Pagu DPA Kegiatan
                total_cols = 12
        else:
            if is_dankel:
                # Kolom Dankel Normal:
                # 1: No, 2: Sub OPD, 3: Kegiatan, 4: Sub Kegiatan, 5: Pagu, 6: Output, 7: Satuan, 8: Keterangan
                total_cols = 8
            else:
                # Kolom Pendidikan / Kesehatan / PU Normal:
                # 1: No, 2: OPD, 3: Sub Kegiatan, 4: Pagu, 5: Output, 6: Satuan, 7: Kode DPA Kegiatan, 8: Pagu DPA Kegiatan
                total_cols = 8

        max_col_letter = get_column_letter(total_cols)

        # Header Title
        ws.merge_cells(f"A1:{max_col_letter}1")
        ws["A1"] = "PEMERINTAH KABUPATEN ASAHAN"
        ws["A1"].font = styles['font_title']
        ws["A1"].alignment = styles['align_center']

        ws.merge_cells(f"A2:{max_col_letter}2")
        title_text = f"DAFTAR RENCANA KEGIATAN {bidang_label.upper()} ({sumber_label.upper()})"
        ws["A2"] = title_text
        ws["A2"].font = styles['font_subtitle']
        ws["A2"].alignment = styles['align_center']

        if is_perubahan:
            ws.merge_cells(f"A3:{max_col_letter}3")
            if is_draft_changed:
                ws["A3"] = f"PERUBAHAN RENCANA KEGIATAN (SEMULA VS MENJADI) TAHUN {tahun}"
            else:
                j_induk_nama = getattr(context.get('jadwal_induk'), 'jadwal_keterangan', None) or getattr(context.get('jadwal_induk'), 'jadwal_nama', 'Induk')
                j_perubahan_nama = getattr(context.get('jadwal_perubahan'), 'jadwal_keterangan', None) or getattr(context.get('jadwal_perubahan'), 'jadwal_nama', 'Perubahan')
                ws["A3"] = f"PERBANDINGAN INDUK ({j_induk_nama}) DAN PERUBAHAN ({j_perubahan_nama}) TAHUN {tahun}"
            ws["A3"].font = styles['font_meta_lbl']
            ws["A3"].alignment = styles['align_center']

        # Metadata filter
        ws["A5"] = "Tahun Anggaran"
        ws["A5"].font = styles['font_meta_lbl']
        ws["B5"] = f": {tahun}"
        ws["B5"].font = styles['font_meta_val']

        ws["D5"] = "Sumber Dana"
        ws["D5"].font = styles['font_meta_lbl']
        ws["E5"] = f": {dana}"
        ws["E5"].font = styles['font_meta_val']

        ws["A6"] = "OPD / Unit"
        ws["A6"].font = styles['font_meta_lbl']
        ws["B6"] = f": {opd}"
        ws["B6"].font = styles['font_meta_val']

        # Render Table Headers
        start_row = 8
        if is_perubahan:
            # Multi-row Header (Row 8 & 9)
            ws.row_dimensions[8].height = 24
            ws.row_dimensions[9].height = 22

            if is_dankel:
                # Merge row 8 & 9 for single columns
                merges = [("A8:A9", "No"), ("B8:B9", "Sub OPD"), ("C8:C9", "Kegiatan"), ("D8:D9", "Sub Kegiatan"),
                          ("E8:F8", lbl_semula), ("G8:H8", lbl_menjadi), ("I8:J8", lbl_selisih),
                          ("K8:K9", "Satuan"), ("L8:L9", "Keterangan")]
                for m_range, m_text in merges:
                    ws.merge_cells(m_range)
                    top_cell = m_range.split(":")[0]
                    ws[top_cell] = m_text

                # Subheaders on row 9
                ws["E9"] = "Pagu (Rp)"
                ws["F9"] = "Output"
                ws["G9"] = "Pagu (Rp)"
                ws["H9"] = "Output"
                ws["I9"] = "Pagu (Rp)"
                ws["J9"] = "Output"
            else:
                merges = [("A8:A9", "No"), ("B8:B9", "OPD"), ("C8:C9", "Sub Kegiatan"),
                          ("D8:E8", lbl_semula), ("F8:G8", lbl_menjadi), ("H8:I8", lbl_selisih),
                          ("J8:J9", "Satuan"), ("K8:K9", "Kode DPA Kegiatan"), ("L8:L9", "Pagu DPA Kegiatan (Rp)")]
                for m_range, m_text in merges:
                    ws.merge_cells(m_range)
                    top_cell = m_range.split(":")[0]
                    ws[top_cell] = m_text

                # Subheaders on row 9
                ws["D9"] = "Pagu (Rp)"
                ws["E9"] = "Output"
                ws["F9"] = "Pagu (Rp)"
                ws["G9"] = "Output"
                ws["H9"] = "Pagu (Rp)"
                ws["I9"] = "Output"

            # Style header rows 8 & 9
            for r in range(8, 10):
                for c in range(1, total_cols + 1):
                    cell = ws.cell(row=r, column=c)
                    cell.font = styles['font_header']
                    cell.fill = styles['fill_header']
                    cell.alignment = styles['align_center']
                    cell.border = styles['border_cell']

            current_row = 10
        else:
            # Single Header (Row 8)
            ws.row_dimensions[8].height = 26
            if is_dankel:
                headers = ["No", "Sub OPD", "Kegiatan", "Sub Kegiatan", "Pagu (Rp)", "Output", "Satuan", "Keterangan"]
            else:
                headers = ["No", "OPD", "Sub Kegiatan", "Pagu (Rp)", "Output", "Satuan", "Kode DPA Kegiatan", "Pagu DPA Kegiatan (Rp)"]

            for c, h in enumerate(headers, 1):
                cell = ws.cell(row=8, column=c, value=h)
                cell.font = styles['font_header']
                cell.fill = styles['fill_header']
                cell.alignment = styles['align_center']
                cell.border = styles['border_cell']

            current_row = 9

        # Render Data Rows
        sum_pagu_1 = 0.0
        sum_out_1 = 0.0
        sum_pagu_2 = 0.0
        sum_out_2 = 0.0
        sum_pagu_diff = 0.0
        sum_out_diff = 0.0
        sum_pagu_dpa = 0.0

        for idx, item in enumerate(data, 1):
            ws.row_dimensions[current_row].height = 20
            use_zebra = (idx % 2 == 0)

            # Ekstraksi field objek
            if is_dankel:
                subopd_val = cls._clean_str(getattr(item, 'get_subopd', getattr(item, 'rencdankel_subopd', getattr(item, 'rencdankelsisa_subopd', ''))))
                keg_val = cls._clean_str(getattr(item, 'get_kegiatan', getattr(item, 'rencdankel_kegiatan', getattr(item, 'rencdankelsisa_kegiatan', ''))))
                subkeg_val = cls._clean_str(getattr(item, 'get_subkegiatan', getattr(item, 'rencdankel_subkegiatan', getattr(item, 'rencdankelsisa_subkegiatan', ''))))
                satuan_val = cls._clean_str(getattr(item, 'get_satuan_kegiatan', getattr(item, 'rencdankel_satuan', getattr(item, 'rencdankelsisa_satuan', ''))))
                ket_val = cls._clean_str(getattr(item, 'get_keterangan', getattr(item, 'rencdankel_ket', getattr(item, 'rencdankelsisa_ket', ''))))
                pagudpa_val = 0.0
            else:
                subopd_val = cls._clean_str(getattr(item, 'rencana_subopd', getattr(item, 'rencanasisa_subopd', '')))
                keg_val = ""
                subkeg_val = cls._clean_str(getattr(item, 'get_subkegiatan', getattr(item, 'rencana_kegiatan', getattr(item, 'rencanasisa_kegiatan', ''))))
                satuan_val = cls._clean_str(getattr(item, 'get_satuan_kegiatan', getattr(item, 'rencana_satuan', '')))
                ket_val = cls._clean_str(getattr(item, 'rencana_ket', getattr(item, 'rencanasisa_ket', '')))
                pagudpa_val = cls._to_num(getattr(item, 'rencana_pagudpa', getattr(item, 'rencanasisa_pagudpa', 0.0)))
                sum_pagu_dpa += pagudpa_val

            if is_perubahan:
                p_induk = cls._to_num(getattr(item, 'induk_pagu', 0.0))
                o_induk = cls._to_num(getattr(item, 'induk_output', 0.0))
                p_perubahan = cls._to_num(getattr(item, 'perubahan_pagu', 0.0))
                o_perubahan = cls._to_num(getattr(item, 'perubahan_output', 0.0))
                p_selisih = cls._to_num(getattr(item, 'selisih_pagu', 0.0))
                o_selisih = cls._to_num(getattr(item, 'selisih_output', 0.0))

                sum_pagu_1 += p_induk
                sum_out_1 += o_induk
                sum_pagu_2 += p_perubahan
                sum_out_2 += o_perubahan
                sum_pagu_diff += p_selisih
                sum_out_diff += o_selisih

                if is_dankel:
                    row_vals = [idx, subopd_val, keg_val, subkeg_val, p_induk, o_induk, p_perubahan, o_perubahan, p_selisih, o_selisih, satuan_val, ket_val]
                    num_cols = (5, 6, 7, 8, 9, 10)
                    center_cols = (1, 11)
                else:
                    row_vals = [idx, subopd_val, subkeg_val, p_induk, o_induk, p_perubahan, o_perubahan, p_selisih, o_selisih, satuan_val, ket_val, pagudpa_val]
                    num_cols = (4, 5, 6, 7, 8, 9, 12)
                    center_cols = (1, 10, 11)
            else:
                if is_dankel:
                    pagu_val = cls._to_num(getattr(item, 'rencdankel_pagu', getattr(item, 'rencdankelsisa_pagu', 0.0)))
                    out_val = cls._to_num(getattr(item, 'rencdankel_output', getattr(item, 'rencdankelsisa_output', 0.0)))
                    row_vals = [idx, subopd_val, keg_val, subkeg_val, pagu_val, out_val, satuan_val, ket_val]
                    num_cols = (5, 6)
                    center_cols = (1, 7)
                else:
                    pagu_val = cls._to_num(getattr(item, 'rencana_pagu', getattr(item, 'rencanasisa_pagu', 0.0)))
                    out_val = cls._to_num(getattr(item, 'rencana_output', getattr(item, 'rencanasisa_output', 0.0)))
                    row_vals = [idx, subopd_val, subkeg_val, pagu_val, out_val, satuan_val, ket_val, pagudpa_val]
                    num_cols = (4, 5, 8)
                    center_cols = (1, 6, 7)

                sum_pagu_1 += pagu_val
                sum_out_1 += out_val

            for c, val in enumerate(row_vals, 1):
                cell = ws.cell(row=current_row, column=c, value=val)
                cell.font = styles['font_data']
                cell.border = styles['border_cell']
                if use_zebra:
                    cell.fill = styles['fill_zebra']

                if c in num_cols:
                    cell.alignment = styles['align_right']
                    cell.number_format = '#,##0.00'
                elif c in center_cols:
                    cell.alignment = styles['align_center']
                else:
                    cell.alignment = styles['align_left']

            current_row += 1

        # Render Total Row
        ws.row_dimensions[current_row].height = 24
        if is_perubahan:
            if is_dankel:
                ws.merge_cells(f"A{current_row}:D{current_row}")
                ws[f"A{current_row}"] = "Total Keseluruhan:"
                totals = {5: sum_pagu_1, 6: sum_out_1, 7: sum_pagu_2, 8: sum_out_2, 9: sum_pagu_diff, 10: sum_out_diff}
                empty_cols = (11, 12)
            else:
                ws.merge_cells(f"A{current_row}:C{current_row}")
                ws[f"A{current_row}"] = "Total Keseluruhan:"
                totals = {4: sum_pagu_1, 5: sum_out_1, 6: sum_pagu_2, 7: sum_out_2, 8: sum_pagu_diff, 9: sum_out_diff, 12: sum_pagu_dpa}
                empty_cols = (10, 11)
        else:
            if is_dankel:
                ws.merge_cells(f"A{current_row}:D{current_row}")
                ws[f"A{current_row}"] = "Total Keseluruhan:"
                totals = {5: sum_pagu_1, 6: sum_out_1}
                empty_cols = (7, 8)
            else:
                ws.merge_cells(f"A{current_row}:C{current_row}")
                ws[f"A{current_row}"] = "Total Keseluruhan:"
                totals = {4: sum_pagu_1, 5: sum_out_1, 8: sum_pagu_dpa}
                empty_cols = (6, 7)

        for c in range(1, total_cols + 1):
            cell = ws.cell(row=current_row, column=c)
            cell.font = styles['font_total']
            cell.fill = styles['fill_total']
            cell.border = styles['border_total']

            if c in totals:
                cell.value = totals[c]
                cell.alignment = styles['align_right']
                cell.number_format = '#,##0.00'
            elif c == 1:
                cell.alignment = styles['align_right']

        cls._adjust_column_widths(ws, start_row=8, total_cols=total_cols)

        filename = f"Laporan_Rencana_{bidang}_{sumber}_{tahun}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return cls._create_response(wb, filename)

