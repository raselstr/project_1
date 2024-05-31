from django import forms
from django.urls import reverse
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
        widgets = {
            'kegiatan_dana': forms.Select(attrs={'class': 'form-control', 'hx-target': '#id_kegiatan_program'}),
            'kegiatan_program': forms.Select(attrs={'class': 'form-control'}),
            'kegiatan_nama': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['kegiatan_dana'].widget.attrs['hx-get'] = reverse('load_dana')

        if 'kegiatan_dana' in self.data:
            try:
                dana_id = int(self.data.get('kegiatan_dana'))
                self.fields['kegiatan_program'].queryset = Program.objects.filter(program_dana=dana_id)
            except (ValueError, TypeError):
                self.fields['kegiatan_program'].queryset = Program.objects.none()
        elif self.instance.pk:
            self.fields['kegiatan_program'].queryset = Program.objects.filter(program_dana=self.instance.kegiatan_dana)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance


# class KegiatanForm(forms.Form):
#     kegiatan_dana = forms.ModelChoiceField(queryset=Dana.objects.all(),
#             widget=forms.Select(attrs={'class':'form-control','hx-get':'load_dana/','hx-target':'#id_kegiatan_program'}))
#     kegiatan_program = forms.ModelChoiceField(queryset=Program.objects.none(),
#             widget=forms.Select(attrs={'class':'form-control'}))
#     kegiatan_nama = forms.CharField(max_length=200,
#             widget=forms.TextInput(attrs={'class':'form-control'}))

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         if 'kegiatan_dana' in self.data:
#             dana_id = int(self.data.get('kegiatan_dana'))
#             self.fields['kegiatan_program'].queryset = Program.objects.filter(program_dana=dana_id)

#     def save(self, commit=True):
#         kegiatan = Kegiatan(
#             kegiatan_dana=self.cleaned_data['kegiatan_dana'],
#             kegiatan_program=self.cleaned_data['kegiatan_program'],
#             kegiatan_nama=self.cleaned_data['kegiatan_nama']
#         )

#         if commit:
#             kegiatan.save()

#         return kegiatan

    

# class KegiatanForm(forms.ModelForm):
#     class Meta:
#         model = Kegiatan
#         fields = '__all__'

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['kegiatan_dana'].widget.attrs.update({'class': 'form-control'})
#         self.fields['kegiatan_program'].widget.attrs.update({'class': 'form-control'})
#         self.fields['kegiatan_nama'].widget.attrs.update({'class': 'form-control','placeholder': 'Nama Kegiatan'})

class SubkegiatanForm(forms.ModelForm):
    class Meta:
        model = Subkegiatan
        fields = '__all__'

class SubrRincianForm(forms.ModelForm):
    class Meta:
        model = SubRincian
        fields = '__all__'

