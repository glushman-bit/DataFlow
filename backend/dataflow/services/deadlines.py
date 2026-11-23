from datetime import date, datetime

from django.utils import timezone


def get_overdue_records(table):
    """Возвращает просроченные записи таблицы."""

    fields = [
        field
        for field in table.fields.all()
        if (
            field.field_type in ('date', 'datetime')
            and (field.settings or {}).get('deadline', {}).get('enabled') is True
        )
    ]

    if not fields:
        return []

    today = timezone.localdate()
    now = timezone.now()

    overdue_records = []

    for record in table.records.all():
        overdue_fields = []

        for field in fields:
            value = record.values.get(field.name)

            if not value:
                continue

            try:
                if field.field_type == 'date':
                    field_value = date.fromisoformat(value)
                    is_overdue = field_value < today

                else:
                    field_value = datetime.fromisoformat(value)

                    if timezone.is_naive(field_value):
                        field_value = timezone.make_aware(
                            field_value,
                            timezone.get_current_timezone(),
                        )

                    is_overdue = field_value < now

            except (ValueError, TypeError):
                continue

            if is_overdue:
                overdue_fields.append({
                    'name': field.name,
                    'label': field.label,
                    'value': value,
                })

        if overdue_fields:
            overdue_records.append({
                'record': record,
                'overdue_fields': overdue_fields,
            })

    return overdue_records
