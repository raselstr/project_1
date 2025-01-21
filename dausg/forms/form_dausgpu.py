from django import forms
from django.urls import reverse
from ..models import DausgpuProg, DausgpuKeg, DausgpuSub

class DausgpuProgForm(forms.ModelForm):
    
    class Meta:
        model = DausgpuProg
        fields = '__all__'
        widgets = {
            'dausgpu_dana': forms.Select(attrs={
                'class': 'form-control', 
                'hx-target': '#id_dausgpu_subrinc',
                'hx-trigger': 'click',
                }),
            'dausgpu_subrinc': forms.Select(attrs={
                'class': 'form-control', 
                }),
            'dausgpu_prog': forms.TextInput(attrs={'class': 'form-control'}),
            'dausgpu_tahun': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dausgpu_dana'].widget.attrs['hx-get'] = reverse('load_dausgpuprog')
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance
    

class DausgpuKegForm(forms.ModelForm):
    
    class Meta:
        model = DausgpuKeg
        fields = '__all__'
       
    def __init__(self, *args, **kwargs):
        number = kwargs.pop('number', None)
        super().__init__(*args, **kwargs)
       
        self.fields['dausgpukeg_prog'].widget.attrs.update({'class':'form-control'})
        self.fields['dausgpukeg_nama'].widget.attrs.update({'class':'form-control','placeholder': 'Nama Kegiatan'})
        
        if number:
            self.initial['dausgpukeg_prog'] = number
                
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance


class DausgpuSubForm(forms.ModelForm):
    
    class Meta:
        model = DausgpuSub
        fields = '__all__'
       
    def __init__(self, *args, **kwargs):
        sub = kwargs.pop('sub', None)
        super().__init__(*args, **kwargs)
        self.fields['dausgpusub_keg'].widget.attrs.update({'class':'form-control'})
        self.fields['dausgpusub_nama'].widget.attrs.update({'class':'form-control','placeholder': 'Nama Sub Kegiatan'})
        self.fields['dausgpusub_satuan'].widget.attrs.update({'class':'form-control'})
        
        if sub:
            self.initial['dausgpusub_keg'] = sub
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance