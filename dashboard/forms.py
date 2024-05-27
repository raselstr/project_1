from django import forms

from .models import *

class Menuform(forms.ModelForm):
    class Meta:
        model = Menu
        field = '__all__'

class SubmenuForm(forms.ModelForm):
    class Meta:
        model = Submenu
        field = '__all__'

class LevelForm(forms.ModelForm):
    class Meta:
        model = Level
        field = '__all__'
        widget = {
            'level_submenu' : forms.SelectMultiple,
        }