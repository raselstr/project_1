from django.contrib import admin
from django import forms
from .models import *

# Register your models here.
class LevelAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "level_submenu":
            kwargs["widget"] = forms.SelectMultiple  # Menggunakan SelectMultiple hanya untuk field level_submenu
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Menu)
admin.site.register(Submenu)
admin.site.register(Userlevel)

admin.site.register(Levelsub)
admin.site.register(Level, LevelAdmin)


