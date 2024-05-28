from django import forms

from .models import Menu, Submenu, Level

class Menuform(forms.ModelForm):
    class Meta:
        model = Menu
        fields = '__all__'


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['menu_nama'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nama Menu'})
        self.fields['menu_link'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Link Menu'})
        self.fields['menu_icon'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Icon Menu'})

class SubmenuForm(forms.ModelForm):
    class Meta:
        model = Submenu
        fields = '__all__'

class LevelForm(forms.ModelForm):
    class Meta:
        model = Level
        fields = '__all__'
        widget = {
            'level_submenu' : forms.SelectMultiple,
        }