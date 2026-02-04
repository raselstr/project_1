def get_nama_subkegiatan(obj):
    """
    Mengambil nama sub kegiatan secara umum
    untuk semua jenis (pendidikan, kesehatan, PU, kelurahan, dll)
    """
    for attr in dir(obj):
        if attr.endswith('sub_nama'):
            value = getattr(obj, attr, None)
            if isinstance(value, str) and value.strip():
                return value

    return str(obj)
