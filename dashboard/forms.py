from django import forms
from django.utils.html import escape

from .models import Menu, Submenu, Level, Userlevel

class Menuform(forms.ModelForm):
    class Meta:
        model = Menu
        fields = '__all__'


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['menu_nama'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nama Menu'})
        self.fields['menu_link'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Link Menu'})
        self.fields['menu_icon'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Icon Menu'})
    
    def clean_menu_nama(self):
        data = self.cleaned_data['menu_nama']
        return escape(data)

    def clean_menu_link(self):
        data = self.cleaned_data['menu_link']
        return escape(data)

    def clean_menu_icon(self):
        data = self.cleaned_data['menu_icon']
        return escape(data)

class SubmenuForm(forms.ModelForm):
    class Meta:
        model = Submenu
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['submenu_menu'].widget.attrs.update({'class': 'form-control select2'})
        self.fields['submenu_nama'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nama Submenu'})
        self.fields['submenu_icon'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Icon Submenu'})
        self.fields['submenu_link'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Link Submenu'})
    
    def clean_menu_nama(self):
        data = self.cleaned_data['submenu_menu']
        return escape(data)

    def clean_menu_link(self):
        data = self.cleaned_data['submenu_nama']
        return escape(data)

    def clean_menu_icon(self):
        data = self.cleaned_data['submenu_icon']
        return escape(data)
    
    def clean_menu_icon(self):
        data = self.cleaned_data['submenu_link']
        return escape(data)

class LevelForm(forms.ModelForm):
    class Meta:
        model = Level
        fields = '__all__'
        widget = {
            'level_submenu': forms.SelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['level_nama'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nama Level'})
        self.fields['level_submenu'].widget.attrs.update({'class': 'form-control select2'})
    
    def clean_menu_nama(self):
        data = self.cleaned_data['level_nama']
        return escape(data)

    def clean_menu_link(self):
        data = self.cleaned_data['level_submenu']
        return escape(data)

class UserlevelForm(forms.ModelForm):
    class Meta:
        model = Userlevel
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_nama'].widget.attrs.update({'class': 'form-control select2'})
        self.fields['userlevel'].widget.attrs.update({'class': 'form-control select2'})