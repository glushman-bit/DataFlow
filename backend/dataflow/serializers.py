from rest_framework import serializers
from dataflow.models import DataTable, DataField, DataRecord
from dataflow.services import validate_record_values, create_record


class DataTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataTable
        fields = [
            "id",
            "name",
            "settings",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DataFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataField
        fields = [
            "id",
            "name",
            "label",
            "field_type",
            "required",
            "order",
            "settings",
            "created_at",
        ]
        read_only_fields = ["id", "created_at",]


class DataRecordSerializer(serializers.ModelSerializer):
    """Сериализатор записи данных."""

    def validate_values(self, values):
        """Валидация данных."""

        table = self.context.get("table")

        if table is None:
            raise serializers.ValidationError("Не указана таблица для записи.")

        return validate_record_values(table, values)

    def create(self, validated_data):
        """Создание записи."""
        table = self.context.get("table")
        request = self.context.get("request")

        if table is None:
            raise serializers.ValidationError("Не указана таблица для записи.")

        if request is None:
            raise serializers.ValidationError("Не передан HTTP-запрос.")


        return create_record(
            table=table,
            user=request.user,
            values=validated_data["values"],
        )

    class Meta:
        model = DataRecord
        fields = [
            "id",
            "values",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

