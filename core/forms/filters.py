from django import forms
from core.services.realisasi_service import RealisasiService


class RekapRealisasiFilterForm(forms.Form):
    tahun = forms.ChoiceField(
        required=False,
        label="Tahun",
        choices=[],
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    dana = forms.ChoiceField(
        required=False,
        label="Jenis Dana",
        choices=[],
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    tahap = forms.ChoiceField(
        required=False,
        label="Tahap",
        choices=[],
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["tahun"].choices = [("", "Semua Tahun")] + [
            (t, t) for t in RealisasiService.get_available_tahun()
        ]

        self.fields["dana"].choices = [("", "Semua Dana")] + \
            RealisasiService.get_available_dana()

        self.fields["tahap"].choices = [("", "Semua Tahap")] + \
            RealisasiService.get_available_tahap()
