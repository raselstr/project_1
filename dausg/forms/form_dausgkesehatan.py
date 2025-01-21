from django import forms
from django.urls import reverse
from ..models import DausgkesehatanProg, DausgkesehatanKeg, DausgkesehatanSub

class DausgkesehatanProgForm(forms.ModelForm):
    
    class Meta:
        model = DausgkesehatanProg
        fields = '__all__'
        widgets = {
            'dausgkesehatan_dana': forms.Select(attrs={
                'class': 'form-control', 
                'hx-target': '#id_dausgkesehatan_subrinc',
                'hx-trigger': 'click',
                }),
            'dausgkesehatan_subrinc': forms.Select(attrs={
                'class': 'form-control', 
                }),
            'dausgkesehatan_prog': forms.TextInput(attrs={'class': 'form-control'}),
            'dausgkesehatan_tahun': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dausgkesehatan_dana'].widget.attrs['hx-get'] = reverse('load_dausgkesehatanprog')
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance
    

class DausgkesehatanKegForm(forms.ModelForm):
    
    class Meta:
        model = DausgkesehatanKeg
        fields = '__all__'
       
    def __init__(self, *args, **kwargs):
        number = kwargs.pop('number', None)
        super().__init__(*args, **kwargs)
       
        self.fields['dausgkesehatankeg_prog'].widget.attrs.update({'class':'form-control'})
        self.fields['dausgkesehatankeg_nama'].widget.attrs.update({'class':'form-control','placeholder': 'Nama Kegiatan'})
        
        if number:
            self.initial['dausgkesehatankeg_prog'] = number
                
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance


class DausgkesehatanSubForm(forms.ModelForm):
    
    class Meta:
        model = DausgkesehatanSub
        fields = '__all__'
       
    def __init__(self, *args, **kwargs):
        sub = kwargs.pop('sub', None)
        super().__init__(*args, **kwargs)
        self.fields['dausgkesehatansub_keg'].widget.attrs.update({'class':'form-control'})
        self.fields['dausgkesehatansub_nama'].widget.attrs.update({'class':'form-control','placeholder': 'Nama Sub Kegiatan'})
        self.fields['dausgkesehatansub_satuan'].widget.attrs.update({'class':'form-control'})
        
        if sub:
            self.initial['dausgkesehatansub_keg'] = sub
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance