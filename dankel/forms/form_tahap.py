from django import forms
from ..models import RealisasiDankel

class RealisasiDankelForm(forms.ModelForm):
    class Meta:
        model = RealisasiDankel
        fields = '__all__'
        
        widgets = {
            'realisasidankel_tahun': forms.TextInput(attrs={'class': 'form-control'}),
            'realisasidankel_dana' : forms.Select(attrs={'class': 'form-control select2'}),
            'realisasidankel_tahap': forms.Select(attrs={'class': 'form-control select2'}),
            'realisasidankel_subopd': forms.Select(attrs={'class': 'form-control select2'}),
        }
        
    def __init__(self, *args, **kwargs):
        # sesiidopd = kwargs.pop('sesiidopd', None)
        # sesidana = kwargs.pop('sesidana', None)
        super().__init__(*args, **kwargs)
        
        # if sesiidopd is not None:
        #     self.fields['rencdankelsisa_subopd'].queryset = Subopd.objects.filter(id=sesiidopd)
        # else:
        #     self.fields['rencdankelsisa_subopd'].queryset = Subopd.objects.all()
            
        # if sesidana is not None:
        #     self.fields['rencdankelsisa_dana'].queryset = Subrinc.objects.filter(subrinc_slug=sesidana)
        # else:
        #     self.fields['rencdankelsisa_dana'].queryset = Subrinc.objects.all()
        
        
    
   