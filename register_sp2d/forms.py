from django import forms


class RegisterSP2DUploadForm(forms.Form):
    file = forms.FileField(
        label="File Excel Register SP2D",
        help_text="Format .xlsx – Laporan Register SP2D dari SIPD (mulai baris data ke-8)",
        required=True,
        widget=forms.ClearableFileInput(attrs={
            "accept": ".xlsx",
            "class": "form-control"
        })
    )
