from django import forms
from django.utils.html import escape
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.forms import inlineformset_factory


from .models import Menu, Submenu, Rinciansubmenu, Level, Userlevel, Levelsub


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
        self.fields['submenu_icon'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Icon Submenu (contoh: fas fa-file)'})
        self.fields['submenu_link'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Link Submenu'})
        if 'submenu_urutan' in self.fields:
            self.fields['submenu_urutan'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Urutan'})

class RinciansubmenuForm(forms.ModelForm):
    class Meta:
        model = Rinciansubmenu
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rinciansubmenu_submenu'].widget.attrs.update({'class': 'form-control select2'})
        self.fields['rinciansubmenu_nama'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nama Rincian Sub Menu'})
        self.fields['rinciansubmenu_icon'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Icon Rincian Sub Menu (contoh: fas fa-list)'})
        self.fields['rinciansubmenu_link'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Link Rincian Sub Menu (contoh: rencana_pendidikan_home)'})
        if 'rinciansubmenu_urutan' in self.fields:
            self.fields['rinciansubmenu_urutan'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Urutan'})

class LevelForm(forms.ModelForm):
    class Meta:
        model = Level
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['level_nama'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nama Level'})

class LevelsubForm(forms.ModelForm):
    class Meta:
        model = Levelsub
        fields = ['lihat', 'simpan', 'edit', 'hapus']
        widgets = {
            'lihat': forms.CheckboxInput(attrs={'class': 'custom-switch-input perm-input perm-lihat'}),
            'simpan': forms.CheckboxInput(attrs={'class': 'custom-switch-input perm-input perm-simpan'}),
            'edit': forms.CheckboxInput(attrs={'class': 'custom-switch-input perm-input perm-edit'}),
            'hapus': forms.CheckboxInput(attrs={'class': 'custom-switch-input perm-input perm-hapus'}),
        }
    
class UserlevelForm(forms.ModelForm):
    class Meta:
        model = Userlevel
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_nama'].widget.attrs.update({'class': 'form-control select2'})
        self.fields['userlevel'].widget.attrs.update({'class': 'form-control select2'})
        self.fields['userlevelopd'].widget.attrs.update({'class': 'form-control select2'})

class PenggunaForm(UserCreationForm):
    is_active = forms.BooleanField(label="Active", required=False, initial=True)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'is_active')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = self.cleaned_data['is_active']
        if commit:
            user.save()
        return 
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

class PenggunaAktifForm(UserChangeForm):
    is_active = forms.BooleanField(label="Active", required=False, initial=True)

    class Meta:
        model = User
        fields = ('username', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})

class UbahPasswordForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})