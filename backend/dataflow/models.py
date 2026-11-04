from django.db import models
from django.conf import settings


class DataTable(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="data_tables",
    )
    name = models.CharField(max_length=255)
    settings = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "name"],
                name="unique_table_name_per_owner",
            )
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
