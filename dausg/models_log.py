from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class LogCopyTahun(models.Model):
    sektor = models.CharField(max_length=50)
    tahun_asal = models.IntegerField()
    tahun_tujuan = models.IntegerField()

    status = models.CharField(
        max_length=20,
        choices=[
            ("SUCCESS", "Berhasil"),
            ("FAILED", "Gagal"),
        ],
    )

    pesan = models.TextField(blank=True, null=True)

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.sektor} {self.tahun_asal}→{self.tahun_tujuan} ({self.status})"
