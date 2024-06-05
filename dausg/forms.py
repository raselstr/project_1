from django import forms
from django.urls import reverse
from .models import DankelProg, DankelKeg

class DankelProgForm(forms.ModelForm):
    
    class Meta:
        model = DankelProg
        fields = '__all__'
        widgets = {
            'dankel_dana': forms.Select(attrs={
                'class': 'form-control', 
                'hx-target': '#id_dankel_subrinc',
                'hx-trigger': 'click',
                }),
            'dankel_subrinc': forms.Select(attrs={
                'class': 'form-control', 
                }),
            'dankel_prog': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dankel_dana'].widget.attrs['hx-get'] = reverse('load_dankelprog')
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance
    

class DankelKegForm(forms.ModelForm):
    
    class Meta:
        model = DankelKeg
        fields = '__all__'
        widgets = {
            'dankelkeg_subrinc': forms.Select(attrs={
                'class': 'form-control', 
                'hx-target': '#id_dankelkeg_prog',
                'hx-trigger': 'click',
                }),
            'dankelkeg_prog': forms.Select(attrs={
                'class': 'form-control', 
                }),
            'dankelkeg_nama': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dankelkeg_subrinc'].widget.attrs['hx-get'] = reverse('load_dankelkeg')
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance