from django.contrib import admin
from .models import Pagudausg

class PagudausgAdmin(admin.ModelAdmin):
    list_display = ('pagudausg_tahun', 'pagudausg_opd', 'pagudausg_dana', 'pagudausg_nilai', 'pagudausg_sisa')

admin.site.register(Pagudausg, PagudausgAdmin)
