from django.contrib import admin
from .models import RencDankel, RencDankelsisa

# class RencDankelsisaInline(admin.TabularInline):
#     model = RencDankelsisa
#     extra = 1  # Jumlah form tambahan yang ingin ditampilkan secara default

# @admin.register(RencDankel)
# class RencDankelAdmin(admin.ModelAdmin):
#     inlines = [RencDankelsisaInline]