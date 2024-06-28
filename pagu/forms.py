from django import forms
from .models import Pagudausg


class PagudausgForm(forms.ModelForm):
    class Meta:
        model = Pagudausg
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pagudausg_tahun'].widget.attrs.update({'class':'form-control'})
        self.fields['pagudausg_opd'].widget.attrs.update({'class':'form-control select2'})
        self.fields['pagudausg_dana'].widget.attrs.update({'class':'form-control select2'})
        self.fields['pagudausg_nilai'].widget.attrs.update({'class':'form-control'})
        self.fields['pagudausg_sisa'].widget.attrs.update({'class':'form-control'})
        