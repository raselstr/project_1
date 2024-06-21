from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.DankelProg)
admin.site.register(models.DankelKeg)
admin.site.register(models.Dankelsub)

admin.site.register(models.DausgpendidikanProg)
admin.site.register(models.DausgpendidikanKeg)
admin.site.register(models.DausgpendidikanSub)

admin.site.register(models.DausgkesehatanProg)
admin.site.register(models.DausgkesehatanKeg)
admin.site.register(models.DausgkesehatanSub)

admin.site.register(models.DausgpuProg)
admin.site.register(models.DausgpuKeg)
admin.site.register(models.DausgpuSub)