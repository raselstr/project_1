from django import forms
from django.db import transaction
from django.core.exceptions import ValidationError
from jadwal import models

Model = models.Jadwal

class JadwalForm(forms.ModelForm):
    class Meta:
        model = models.Jadwal
        fields = '__all__'
        exclude = ('id', 'user')
        widgets = {
            'jadwal_tahun': forms.NumberInput(),
            'jadwal_keterangan': forms.TextInput(),
            'jadwal_aktif': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_jadwal_aktif'}),
        }
        labels = {
            'jadwal_tahun': 'Tahun',
            'jadwal_keterangan': 'Keterangan',
            'jadwal_aktif': 'Aktif',
        }
        error_messages = {
            'jadwal_tahun': {'required': "Tahun harus diisi"},
            'jadwal_keterangan': {'required': "Keterangan harus diisi"},
        }

    def __init__(self, *args, **kwargs):
        self.tahun = kwargs.pop('tahun', None)
        super().__init__(*args, **kwargs)

        field_attrs = {
            'jadwal_tahun': {'class': 'form-control', 'readonly': True, 'placeholder': 'Tahun'},
            'jadwal_keterangan': {'class': 'form-control', 'placeholder': 'Keterangan'},
        }

        for field, attrs in field_attrs.items():
            self.fields[field].widget.attrs.update(attrs)

        if self.instance and self.instance.pk:
            if not self.tahun:
                self.tahun = self.instance.jadwal_tahun

        if self.tahun is not None:
            self.fields['jadwal_tahun'].initial = self.tahun

    def clean_jadwal_tahun(self):
        tahun = self.cleaned_data.get('jadwal_tahun')
        if not tahun and self.tahun:
            tahun = self.tahun
        return tahun

    def validate_unique(self):
        try:
            self.instance.validate_unique()
        except ValidationError as e:
            self._update_errors(e)

        try:
            self.instance.validate_constraints()
        except ValidationError as e:
            is_aktif = False
            if hasattr(self, 'cleaned_data'):
                is_aktif = self.cleaned_data.get('jadwal_aktif', False)
            elif self.instance:
                is_aktif = getattr(self.instance, 'jadwal_aktif', False)

            if is_aktif:
                if hasattr(e, 'error_dict'):
                    filtered = {k: [err for err in v if 'unique_active_jadwal_per_tahun' not in str(err)]
                                for k, v in e.error_dict.items()}
                    filtered = {k: v for k, v in filtered.items() if v}
                    if filtered:
                        self._update_errors(ValidationError(filtered))
                elif hasattr(e, 'error_list'):
                    rem = [err for err in e.error_list if 'unique_active_jadwal_per_tahun' not in str(err)]
                    if rem:
                        self._update_errors(ValidationError(rem))
                elif 'unique_active_jadwal_per_tahun' not in str(e):
                    self._update_errors(e)
            else:
                self._update_errors(e)

    def full_clean(self):
        super().full_clean()
        if not self.is_bound:
            return
        if hasattr(self, 'cleaned_data') and self.cleaned_data.get('jadwal_aktif') and hasattr(self, '_errors') and self._errors:
            for field in list(self._errors.keys()):
                err_list = self._errors[field]
                filtered = [err for err in err_list if 'unique_active_jadwal_per_tahun' not in str(err)]
                if filtered:
                    self._errors[field] = filtered
                else:
                    del self._errors[field]

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.jadwal_tahun and self.tahun:
            instance.jadwal_tahun = self.tahun

        with transaction.atomic():
            if instance.jadwal_aktif and instance.jadwal_tahun:
                models.Jadwal.objects.filter(
                    jadwal_tahun=instance.jadwal_tahun,
                    jadwal_aktif=True
                ).exclude(pk=instance.pk).update(jadwal_aktif=False)

            if commit:
                instance.save()
        return instance
        