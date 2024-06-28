from django.contrib import admin
from .models import RencDankel, RencDankelsisa

class RencDankelAdmin(admin.ModelAdmin):
    list_display = ('rencdankel_tahun','rencdankel_dana', 'rencdankel_subopd', 'rencdankel_sub', 'rencdankel_pagu', 'rencdankel_output', 'rencdankel_verif')

class RencDankelsisaAdmin(admin.ModelAdmin):
    list_display = ('rencdankelsisa_tahun','rencdankelsisa_dana', 'rencdankelsisa_subopd', 'rencdankelsisa_sub', 'rencdankelsisa_pagu', 'rencdankelsisa_output', 'rencdankelsisa_verif')

admin.site.register(RencDankel, RencDankelAdmin)
admin.site.register(RencDankelsisa,RencDankelsisaAdmin)

