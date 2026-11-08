from decimal import Decimal

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

    def update(self, instance, validated_data):
        """Обновляет запись."""

        values = validated_data["values"]  # Получаем проверенные значения.

        json_values = {
            name: str(value) if isinstance(value, Decimal) else value
            for name, value in values.items()
        }   # Преобразуем Decimal в str, чтобы JSONField мог их сохранить.

        instance.values = json_values   # Обновляем instance.values.
        instance.save()     # Сохраняем запись.

        return instance

    def to_internal_value(self, data):
        """Объединяет существующие значения с переданными при PATCH."""

        if self.instance is not None and self.partial:   # Проверяет, что мы обновляем существующую запись и запрос является PATCH.
            current_values = self.instance.values.copy() # Копирует текущие значения записи.
            new_values = data.get("values", {})    # Получает новые значения из запроса.

            data = data.copy()
            data["values"] = {
                **current_values,
                **new_values,
            }   # Объединяет словари. Если поле присутствует в обоих словарях, новое значение заменяет старое.

        return super().to_internal_value(data)  # Передаёт полный словарь стандартной валидации DRF.

# """
# Здесь:
# 1. self.instance — существующая запись, которую обновляем.
# 2. self.partial — признак частичного обновления (PATCH).
# 3. current_values — копия старых значений.
# 4. new_values — значения из запроса.
# 5. **current_values и **new_values объединяют словари. Если ключ встречается дважды, побеждает значение из new_values.
# 6. super().to_internal_value(data) передаёт объединённые данные стандартному механизму DRF для дальнейшей обработки и валидации.
# Таким образом, PATCH не стирает поля, которые пользователь не передал.
# """


    class Meta:
        model = DataRecord
        fields = [
            "id",
            "values",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
