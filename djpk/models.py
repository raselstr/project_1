from django.db import models
from django.core.validators import FileExtensionValidator


def upload_djpk_path(instance, filename):
    return f"djpk/{instance.tahun}/{filename}"


class Djpk(models.Model):
    tahun = models.PositiveIntegerField()
    jenis_dana = models.CharField(max_length=100)

    file = models.FileField(
        upload_to=upload_djpk_path,
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        help_text="Upload file PDF",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-tahun", "jenis_dana"]
        verbose_name = "DJPk"
        verbose_name_plural = "DJPk"

    def __str__(self):
        return f"{self.jenis_dana} - {self.tahun}"
