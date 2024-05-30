from django import forms
from .models import Dana, Program, Kegiatan, Subkegiatan, SubRincian

class DanaForm(forms.ModelForm):
    class Meta:
        model = Dana
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dana_nama'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Jenis Dana'})

class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['program_dana'].widget.attrs.update({'class': 'form-control select2'})
        self.fields['program_nama'].widget.attrs.update({'class': 'form-control','placeholder': 'Nama Program'})

class KegiatanForm(forms.ModelForm):
    class Meta:
        model = Kegiatan
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['kegiatan_dana'].widget.attrs.update({'class': 'form-control'})
        self.fields['kegiatan_program'].widget.attrs.update({'class': 'form-control'})
        self.fields['kegiatan_nama'].widget.attrs.update({'class': 'form-control','placeholder': 'Nama Kegiatan'})

class SubkegiatanForm(forms.ModelForm):
    class Meta:
        model = Subkegiatan
        fields = '__all__'

class SubrRincianForm(forms.ModelForm):
    class Meta:
        model = SubRincian
        fields = '__all__'

