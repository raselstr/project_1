# djpk/forms.py

from django import forms
from .models import Djpk


class DjpkUploadForm(forms.ModelForm):
    class Meta:
        model = Djpk
        fields = ["file"]
