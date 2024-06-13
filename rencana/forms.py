from django import forms
from .models import Rencana

class RencanaForm(forms.ModelForm):
    class Meta:
        model = Rencana
        fields = '__all__'