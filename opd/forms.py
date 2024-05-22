from django import forms
from .models import Opd

class OpdForm(forms.ModelForm):
    class Meta:
        model = Opd
        fields = '__all__'

