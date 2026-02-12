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

        # Tahun
        tahun_choices = [(t, t) for t in RealisasiService.get_available_tahun()]
        self.fields["tahun"].choices = [("", "Semua Tahun")] + tahun_choices

        # Dana
        dana_choices = RealisasiService.get_available_dana()
        self.fields["dana"].choices = [("", "Semua Dana")] + list(dana_choices)

        # Tahap
        tahap_choices = RealisasiService.get_available_tahap()
        self.fields["tahap"].choices = [("", "Semua Tahap")] + list(tahap_choices)
