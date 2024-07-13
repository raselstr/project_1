from django import forms
from django.utils.html import escape
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.forms import inlineformset_factory


from .models import Menu, Submenu, Level, Userlevel, Levelsub


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
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['level_nama'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nama Level'})

class LevelsubForm(forms.ModelForm):
    class Meta:
        model = Levelsub
        fields = '__all__'
LevelsubFormSet = inlineformset_factory(Submenu, Levelsub, form=LevelsubForm, extra=1, can_delete=False)
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['levelsub_level'].widget.attrs.update({'class': 'form-control'})
    #     self.fields['levelsub_submenu'].widget.attrs.update({'class': 'form-control'})
    #     self.fields['lihat'].widget.attrs.update({'class': 'form-control'})
    #     self.fields['simpan'].widget.attrs.update({'class': 'form-control'})
    #     self.fields['update'].widget.attrs.update({'class': 'form-control'})
    #     self.fields['delete'].widget.attrs.update({'class': 'form-control'})
    
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