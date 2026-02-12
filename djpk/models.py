from django.db import models
from django.core.validators import FileExtensionValidator
from dana.models import Subkegiatan, TahapDana


def upload_djpk_path(instance, filename):
    return f"djpk/{instance.tahun}/{filename}"


class Djpk(models.Model):
    tahun = models.PositiveIntegerField()
    jenis_dana = models.ForeignKey(Subkegiatan, verbose_name="Jenis Dana", on_delete=models.CASCADE)
    tahap = models.ForeignKey(TahapDana, verbose_name="Tahap Dana", on_delete=models.CASCADE)

    file = models.FileField(
        upload_to=upload_djpk_path,
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        help_text="Upload file PDF",
        error_messages={"invalid_extension": "Hanya file PDF yang diizinkan."},
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-tahun", "jenis_dana"]
        verbose_name = "DJPk"
        verbose_name_plural = "DJPk"
        constraints = [
            models.UniqueConstraint(
                fields=["tahun", "jenis_dana", "tahap"],
                name="unique_djpk_per_tahun_dana_tahap"
            )
        ]

    def __str__(self):
        return f"{self.jenis_dana} - {self.tahun}"
