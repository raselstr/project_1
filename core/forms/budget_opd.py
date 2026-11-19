from django.db.models import Q

from opd.models import Subopd
from pagu.models import Pagudausg


# ============================================================
# OPD "Khusus" = BKAD, Inspektorat (APIP), dan "Semua"
# User dengan OPD ini diperlakukan sebagai "user privileged":
# - Dapat melihat semua OPD yang memiliki data di suatu bidang
# - Dapat memfilter ke satu OPD tertentu jika dipilih
# - Jika tidak memilih OPD = tampilkan semua data
# ============================================================
SPECIAL_OPD_IDS = {124, 70, 67}
ALL_BUDGETED_OPD_LABEL = 'Semua OPD yang memiliki pagu'
EMPTY_OPD_VALUES = {None, '', 'None', 'none', 'NULL', 'null'}


def normalize_opd_id(opd_id):
    """Normalisasi opd_id: ekstrak pk dari objek, strip string, kembalikan None jika kosong."""
    if hasattr(opd_id, 'pk'):
        opd_id = opd_id.pk
    if isinstance(opd_id, str):
        opd_id = opd_id.strip()
    if opd_id in EMPTY_OPD_VALUES:
        return None
    return opd_id


def is_special_opd(opd_id):
    """
    True jika OPD ini adalah BKAD, APIP/Inspektorat, atau 'Semua'.
    User dengan OPD ini adalah user privileged.
    """
    opd_id = normalize_opd_id(opd_id)
    try:
        return int(opd_id) in SPECIAL_OPD_IDS
    except (TypeError, ValueError):
        return False


def is_privileged_user(session_opd_id):
    """
    True jika user adalah user privileged:
    - Django superuser (session_opd_id=None)
    - BKAD (id=67), APIP/Inspektorat (id=70), Semua (id=124)
    
    User privileged dapat melihat semua OPD di halaman bidang.
    """
    opd_id = normalize_opd_id(session_opd_id)
    if opd_id is None:
        return True  # superuser / tidak ada OPD di session
    return is_special_opd(opd_id)


def scoped_opd_id(opd_id):
    """
    Gunakan untuk membatasi query berdasarkan OPD session user.
    - Jika user adalah privileged (superuser/BKAD/APIP) → return None (tanpa filter)
    - Jika user regular dengan OPD tertentu → return id OPD tersebut
    
    CATATAN: Gunakan resolve_filter_opd() untuk menerapkan filter pilihan OPD dari form.
    """
    opd_id = normalize_opd_id(opd_id)
    if opd_id is None or is_special_opd(opd_id):
        return None
    return opd_id


def resolve_filter_opd(session_opd_id, selected_opd_id):
    """
    Menentukan OPD ID yang digunakan sebagai filter query berdasarkan:
    - session_opd_id  : OPD user yang login (dari session['idsubopd'])
    - selected_opd_id : OPD yang dipilih dari form filter (dari session['rencana_subopd'] / 'realisasi_subopd')

    Aturan:
    1. User privileged (superuser/BKAD/APIP):
       - Jika pilih OPD tertentu → filter ke OPD itu
       - Jika tidak pilih OPD → tanpa filter (tampilkan semua)
    2. User regular (OPD biasa):
       - Selalu difilter ke OPD-nya sendiri (session_opd_id)
       - selected_opd_id diabaikan (tidak bisa akses OPD lain)

    Returns: int OPD id untuk filter, atau None (tanpa filter / tampilkan semua)
    """
    session_id = normalize_opd_id(session_opd_id)
    selected_id = normalize_opd_id(selected_opd_id)

    # User privileged: gunakan selected_id (bisa None = semua, atau id tertentu)
    if is_privileged_user(session_id):
        if selected_id is not None:
            try:
                return int(selected_id)
            except (TypeError, ValueError):
                return None
        return None  # tidak ada pilihan = semua data

    # User regular: selalu gunakan OPD sendiri, abaikan selected_id
    if session_id is not None:
        try:
            return int(session_id)
        except (TypeError, ValueError):
            return None
    return None


def budgeted_subopd_queryset(tahun=None, dana_slug=None, opd_id=None):
    """
    Queryset OPD yang memiliki pagu di suatu bidang/tahun.
    - Jika opd_id adalah user privileged → tampilkan semua OPD yang punya pagu
    - Jika opd_id adalah user regular → hanya OPD-nya sendiri
    """
    opd_id = normalize_opd_id(opd_id)
    pagu_filters = Q()

    if tahun:
        pagu_filters &= Q(pagudausg_tahun=tahun)
    if dana_slug:
        pagu_filters &= Q(pagudausg_dana__sub_slug=dana_slug)

    if dana_slug and 'sisa' in dana_slug:
        pagu_filters &= Q(pagudausg_nilai__gt=0) | Q(pagudausg_sisa__gt=0)
    else:
        pagu_filters &= Q(pagudausg_nilai__gt=0)

    opd_ids = Pagudausg.objects.filter(pagu_filters).values('pagudausg_opd_id')
    queryset = Subopd.objects.filter(id__in=opd_ids).distinct().order_by('sub_nama')

    # User regular: batasi hanya OPD sendiri
    if opd_id is not None and not is_privileged_user(opd_id):
        queryset = queryset.filter(id=opd_id)

    return queryset


def allow_all_budgeted_subopd(field, label=ALL_BUDGETED_OPD_LABEL):
    """Jadikan field OPD opsional dengan empty label 'Semua OPD'."""
    field.required = False
    field.empty_label = label
    field.initial = None
    field.widget.attrs['data-placeholder'] = label
    field.widget.attrs['data-allow-clear'] = 'true'


def apply_opd_filter_to_form(field, session_opd_id):
    """
    Helper untuk form filter: atur field OPD berdasarkan tipe user.
    - User privileged (superuser/BKAD/APIP): field opsional, bisa pilih semua OPD
    - User regular: field required (hanya 1 OPD di queryset)
    """
    if is_privileged_user(session_opd_id):
        allow_all_budgeted_subopd(field)
