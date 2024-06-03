from django import forms

class BaseFormMixin:
    def apply_common_attrs(self):
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.widgets.TextInput):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.widgets.Select):
                field.widget.attrs.update({'class': 'form-control select2'})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_common_attrs()

