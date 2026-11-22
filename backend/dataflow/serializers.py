from decimal import Decimal
from datetime import date, datetime

import re

from rest_framework import serializers
from dataflow.models import DataTable, DataField, DataRecord
from dataflow.services.validation import validate_record_values
from dataflow.services.records import  create_record


class DataTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataTable
        fields = [
            "id",
            "name",
            "description",
            "settings",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DataFieldSerializer(serializers.ModelSerializer):
    """Класс работы с полями таблицы."""

    name = serializers.CharField(
        max_length=50,
        trim_whitespace=False,
    )
    label = serializers.CharField(
        max_length=255,
        trim_whitespace=False,
    )

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


    def validate_settings(self, value):
        return value

    def validate(self, attrs):
        """Валидирование полей."""

        field_type = attrs.get(
            'field_type',
            self.instance.field_type if self.instance else None
        )

        settings = attrs.get(
            'settings',
            self.instance.settings if self.instance else {}
        )

        # Объединяем настройки при частичном обновлении.
        if self.instance and self.partial and 'settings' in attrs:
            settings = {
                **self.instance.settings,
                **settings,
            }

            attrs['settings'] = settings

        min_value = settings.get('min')
        max_value = settings.get('max')

        # Проверка числовых ограничений.
        if field_type in ('integer', 'decimal'):
            for name, value in (
                ('min', min_value),
                ('max', max_value),
            ):
                if value is None:
                    continue

                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    raise serializers.ValidationError({
                        'settings': f'Ограничение {name} должно быть числом.'
                    })

                if field_type == 'integer' and not isinstance(value, int):
                    raise serializers.ValidationError({
                        'settings': f'Ограничение {name} должно быть целым числом.'
                    })

        # Проверка ограничений даты и времени.
        if field_type in ('date', 'datetime'):
            for name, value in (
                ('min', min_value),
                ('max', max_value),
            ):
                if value is None:
                    continue

                try:
                    if not isinstance(value, str):
                        raise ValueError

                    if field_type == 'date':
                        date.fromisoformat(value)
                    else:
                        datetime.fromisoformat(value)

                except (ValueError, TypeError):
                    raise serializers.ValidationError({
                        'settings': (
                            f'Ограничение {name} содержит некорректную дату.'
                        )
                    })

        # Проверка порядка минимального и максимального значений.
        if min_value is not None and max_value is not None:
            if field_type == 'datetime':
                min_comparable = datetime.fromisoformat(min_value)
                max_comparable = datetime.fromisoformat(max_value)

                min_has_timezone = min_comparable.utcoffset() is not None
                max_has_timezone = max_comparable.utcoffset() is not None

                if min_has_timezone != max_has_timezone:
                    raise serializers.ValidationError({
                        'settings': (
                            'Ограничения min и max должны оба содержать '
                            'часовой пояс или оба не содержать его.'
                        )
                    })

            else:
                min_comparable = min_value
                max_comparable = max_value

            if min_comparable > max_comparable:
                raise serializers.ValidationError({
                    'settings': 'Минимальное значение не может превышать максимальное.'
                })

        # Проверка настроек текстового поля.
        if field_type == 'text':
            min_length = settings.get('min_length')
            max_length = settings.get('max_length')

            for name, value in (
                ('min_length', min_length),
                ('max_length', max_length),
            ):
                if value is not None and (
                    isinstance(value, bool) or
                    not isinstance(value, int) or
                    value < 0
                ):
                    raise serializers.ValidationError({
                        'settings': f'{name} должно быть целым неотрицательным числом.'
                    })

            if (
                min_length is not None and
                max_length is not None and
                min_length > max_length
            ):
                raise serializers.ValidationError({
                    'settings': 'Минимальная длина текста не может превышать максимальную.'
                })

        # Проверка количества знаков после запятой.
        if field_type == 'decimal':
            decimal_places = settings.get('decimal_places')

            if decimal_places is not None and (
                    isinstance(decimal_places, bool) or
                    not isinstance(decimal_places, int) or
                    decimal_places < 0
            ):
                raise serializers.ValidationError({
                    'settings': (
                        'Количество знаков после запятой должно быть '
                        'целым неотрицательным числом.'
                    )
                })

        # Проверка автоматической установки даты и времени.
        if field_type in ('date', 'datetime'):
            if (
                'auto_now' in settings and
                not isinstance(settings['auto_now'], bool)
            ):
                raise serializers.ValidationError({
                    'settings': 'Параметр auto_now должен быть true или false.'
                })

        return attrs

    def update(self, instance, validated_data):
        """Обновление полей."""

        new_settings = validated_data.get('settings')

        if new_settings is not None:
            validated_data['settings'] = {
                **instance.settings,
                **new_settings,
            }

        return super().update(instance, validated_data)

    def validate_name(self, value):
        """Проверяет техническое имя поля."""

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                'Техническое имя не может быть пустым.'
            )

        if not re.fullmatch(r'[a-z][a-z0-9_]*', value):
            raise serializers.ValidationError(
                'Используйте только строчные латинские буквы, '
                'цифры и символ _. Имя должно начинаться с буквы.'
            )

        table = (
            self.instance.table
            if self.instance
            else self.context.get("table")
        )

        if table:
            queryset = DataField.objects.filter(
                table=table,
                name=value,
            )

            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise serializers.ValidationError(
                    'Поле с таким техническим именем уже существует.'
                )

        return value

    def validate_label(self, value):
        """Проверяет отображение названия поля."""

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                'Название поля не может быть пустым.'
            )

        table = (
            self.instance.table
            if self.instance
            else self.context.get('table')
        )

        if table:
            queryset = DataField.objects.filter(
                table=table,
                label__iexact=value,
            )

            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise serializers.ValidationError(
                    'Поле с таким названием уже существует в этой таблице.'
                )

        return value


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
        """Объединяет актуальные значения с переданными при PATCH."""

        if self.instance is not None and self.partial:
            table = self.context.get("table")

            valid_field_names = set(
                table.fields.values_list("name", flat=True)
            )

            current_values = {
                name: value
                for name, value in self.instance.values.items()
                if name in valid_field_names
            }

            new_values = data.get("values", {})

            data = data.copy()
            data["values"] = {
                **current_values,
                **new_values,
            }

        return super().to_internal_value(data)

# Что изменилось:
#     1. Получаем список актуальных технических имён полей таблицы.
#     2. Из старой записи оставляем только значения существующих полей.
#     3. Добавляем новые значения из запроса.
#     4. Передаём результат стандартной проверке DRF.

    class Meta:
        model = DataRecord
        fields = [
            "id",
            "values",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
