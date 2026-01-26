# sipd/filters.py
import django_filters
from django.db.models import Q
from .models import Sipd

class SipdFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(
        label="Cari",
        method="global_search"
    )

    class Meta:
        model = Sipd
        fields = []

    def global_search(self, queryset, name, value):
        return queryset.filter(
            Q(nama_sub_skpd__icontains=value) |
            Q(nama_program__icontains=value) |
            Q(nama_kegiatan__icontains=value)
        )
