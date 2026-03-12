from django import forms
from core.helpers.filter_helper import FilterHelper


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

        self.fields["tahun"].choices = FilterHelper.tahun_choices()
        self.fields["dana"].choices = FilterHelper.dana_choices()
        self.fields["tahap"].choices = FilterHelper.tahap_choices()