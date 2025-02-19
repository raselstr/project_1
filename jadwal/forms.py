from django import forms
from jadwal import models

Model = models.Jadwal


class JadwalForm(forms.ModelForm):
    class Meta:
        model = Model
        fields = '__all__'
        exclude = ('id', 'user')
        widgets = {
            'jadwal_tahun': forms.NumberInput(attrs={'class': 'form-control'}),
            'jadwal_keterangan': forms.TextInput(attrs={'class': 'form-control'}),
            'jadwal_aktif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'jadwal_tahun': 'Tahun',
            'jadwal_keterangan': 'Keterangan',
            'jadwal_aktif': 'Aktif',
        }
        help_texts = {
            'jadwal_tahun': 'Masukkan tahun',
            'jadwal_tanggal': 'Masukkan keterangan',
            'jadwal_aktif': 'Centang jika aktif',
        }
        error_messages = {
            'jadwal_tahun': {
                'required': "Tahun harus diisi",
            },
            'jadwal_keterangan': {
                'required': "Keterangan harus diisi",
            },
        }
        error_css_class = 'error'
        required_css_class = 'required'
    
    def __init__(self, *args, **kwargs):
        super(JadwalForm, self).__init__(*args, **kwargs)
        self.fields['jadwal_tahun'].widget.attrs['readonly'] = True
        self.fields['jadwal_tahun'].widget.attrs['style'] = 'background-color: #f7f7f7;'
        self.fields['jadwal_tahun'].widget.attrs['class'] = 'form-control'
        self.fields['jadwal_tahun'].widget.attrs['placeholder'] = 'Tahun'
        self.fields['jadwal_tahun'].widget.attrs['required'] = True
        self.fields['jadwal_tahun'].widget.attrs['autofocus'] = True
        self.fields['jadwal_tahun'].widget.attrs['tabindex'] = 1
        self.fields['jadwal_keterangan'].widget.attrs['class'] = 'form-control'
        self.fields['jadwal_keterangan'].widget.attrs['placeholder'] = 'keterangan'
        self.fields['jadwal_keterangan'].widget.attrs['required'] = True
        self.fields['jadwal_keterangan'].widget.attrs['tabindex'] = 2
        self.fields['jadwal_aktif'].widget.attrs['class'] = 'form-check-input'
        self.fields['jadwal_aktif'].widget.attrs['tabindex'] = 3
        

class JadwalFormUpdate(JadwalForm):
    class Meta:
        model = Model
        fields = '__all__'
        exclude = ('id', 'user')
        widgets = {
            'jadwal_tahun': forms.NumberInput(attrs={'class': 'form-control'}),
            'jadwal_tanggal': forms.DateInput(attrs={'class': 'form-control'}),
            'jadwal_aktif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'jadwal_tahun': 'Tahun',
            'jadwal_tanggal': 'Tanggal',
            'jadwal_aktif': 'Aktif',
        }
        help_texts = {
            'jadwal_tahun': 'Masukkan tahun',
            'jadwal_tanggal': 'Masukkan tanggal',
            'jadwal_aktif': 'Centang jika aktif',
        }
        error_messages = {
            'jadwal_tahun': {
                'required': "Tahun harus diisi",
            },
            'jadwal_tanggal': {
                'required': "Tanggal harus diisi",
            },
        }
        error_css_class = 'error'
        required_css_class = 'required'
        input_formats = ['%Y-%m-%d']
        input_formats = ['%d-%m-%Y']
        input_formats = ['%d/%m/%Y']
        input_formats = ['%d %m %Y']
        
    def __init__(self, *args, **kwargs):
        super(JadwalFormUpdate, self).__init__(*args, **kwargs)
        self.fields['jadwal_tahun'].widget.attrs['readonly'] = True
        self.fields['jadwal_tahun'].widget.attrs['style'] = 'background-color: #f7f7f7;'
        self.fields['jadwal_tahun'].widget.attrs['class'] = 'form-control'
        self.fields['jadwal_tanggal'].widget.attrs['readonly'] = True
        self.fields['jadwal_tanggal'].widget.attrs['style'] = 'background-color: #f7f7f7;'
        self.fields['jadwal_tanggal'].widget.attrs['class'] = 'form-control'
        self.fields['jadwal_aktif'].widget.attrs['class'] = 'form-check-input'
        self.fields['jadwal_aktif'].widget.attrs['tabindex'] = 3
        self.fields['jadwal_tahun'].widget.attrs['tabindex'] = 1
        self.fields['jadwal_tanggal'].widget.attrs['tabindex'] = 2
        self.fields['jadwal_tahun'].widget.attrs['placeholder'] = 'Tahun'
        self.fields['jadwal_tanggal'].widget.attrs['placeholder'] = 'Tanggal'
        self.fields['jadwal_tahun'].widget.attrs['required'] = True
        self.fields['jadwal_tanggal'].widget.attrs['required'] = True
        self.fields['jadwal_tahun'].widget.attrs['autofocus'] = True
        self.fields['jadwal_tahun'].widget.attrs['tabindex'] = 1
        self.fields['jadwal_tanggal'].widget.attrs['tabindex'] = 2
        self.fields['jadwal_aktif'].widget.attrs['class'] = 'form-check-input'
        self.fields['jadwal_aktif'].widget.attrs['tabindex'] = 3
        self.fields['jadwal_tahun'].widget.attrs['readonly'] = True
        self.fields['jadwal_tahun'].widget.attrs['style'] = 'background-color: #f7f7f7;'
        self.fields['jadwal_tahun'].widget.attrs['class'] = 'form-control'
        self.fields['jadwal_tahun'].widget.attrs['placeholder'] = 'Tahun'
        self.fields['jadwal_tahun'].widget.attrs['required'] = True
        self.fields['jadwal_tahun'].widget.attrs['autofocus'] = True
        
        
        
        
        
        
        

            