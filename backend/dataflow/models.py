from django.db import models
from django.conf import settings


class FieldType(models.TextChoices):
    TEXT = "text", "Текст"
    INTEGER = "integer", "Целое число"
    DECIMAL = "decimal", "Десятичное число"
    DATE = "date", "Дата"
    DATETIME = "datetime", "Дата и время"
    BOOLEAN = "boolean", "Да / Нет"


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


class DataField(models.Model):
    table = models.ForeignKey(
        DataTable,
        on_delete=models.CASCADE,
        related_name="fields",
    )
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=255)
    field_type = models.CharField(
        max_length=20,
        choices=FieldType.choices,
        default=FieldType.TEXT,
    )
    required = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    settings = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["table", "name"],
                name="unique_field_name_per_table",
            )
        ]
        ordering = ["order", "created_at"]

    def __str__(self):
        return f"{self.table.name} - {self.label}"


class DataRecord(models.Model):
    table = models.ForeignKey(
        DataTable,
        on_delete=models.CASCADE,
        related_name="records",
    )
    values = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Запись№{self.pk} - {self.table.name}"
