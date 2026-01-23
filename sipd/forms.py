from django import forms

class SipdUploadForm(forms.Form):
    file = forms.FileField(
        label="File Excel SIPD",
        help_text="Format .xlsx",
        required=True
    )
