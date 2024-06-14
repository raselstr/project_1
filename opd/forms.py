from django import forms
from .models import Opd, SubOpd

class OpdForm(forms.ModelForm):
    class Meta:
        model = Opd
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['kode_opd'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Kode OPD'})
        self.fields['nama_opd'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nama OPD'})


# class BookForm(forms.ModelForm):
#     author_name = forms.CharField(max_length=100)
#     author_birthdate = forms.DateField(required=False)
#     author_biography = forms.CharField(widget=forms.Textarea, required=False)
#     publisher_name = forms.CharField(max_length=100)
#     publisher_address = forms.CharField(max_length=255, required=False)
#     publisher_website = forms.URLField(required=False)

#     class Meta:
#         model = Book
#         fields = [
#             "title",
#             "publication_date",
#             "isbn",
#             "author_name",
#             "author_birthdate",
#             "author_biography",
#             "publisher_name",
#             "publisher_address",
#             "publisher_website",
#         ]

#     def save(self, commit=True):
#         book = super().save(commit=False)

#         # Handling Author
#         author_data = {
#             "name": self.cleaned_data["author_name"],
#             "birthdate": self.cleaned_data["author_birthdate"],
#             "biography": self.cleaned_data["author_biography"],
#         }
#         author, created = Author.objects.get_or_create(
#             name=author_data["name"], defaults=author_data
#         )
#         if not created:
#             Author.objects.filter(pk=author.pk).update(**author_data)

#         # Handling Publisher
#         publisher_data = {
#             "name": self.cleaned_data["publisher_name"],
#             "address": self.cleaned_data["publisher_address"],
#             "website": self.cleaned_data["publisher_website"],
#         }
#         publisher, created = Publisher.objects.get_or_create(
#             name=publisher_data["name"], defaults=publisher_data
#         )
#         if not created:
#             Publisher.objects.filter(pk=publisher.pk).update(**publisher_data)

#         book.author = author
#         book.publisher = publisher

#         if commit:
#             book.save()
#         return book
