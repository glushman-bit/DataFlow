from django.core.exceptions import ValidationError


def validate_text(field, value):
    """Проверяет текстовое значение и его настройки."""

    if not isinstance(value, str):
        raise ValidationError("Ожидается текст.")

    settings = field.settings or {}

    min_length = settings.get("min_length")
    max_length = settings.get("max_length")

    for setting, limit in [
        ("min_length", min_length),
        ("max_length", max_length),
    ]:
        if limit is None:
            continue

        if (
            isinstance(limit, bool)
            or not isinstance(limit, int)
            or limit < 0
        ):
            raise ValidationError(
                f"Некорректная настройка {setting}."
            )

    if min_length is not None and len(value) < min_length:
        raise ValidationError(
            f"Минимальная длина текста — {min_length} символов."
        )

    if max_length is not None and len(value) > max_length:
        raise ValidationError(
            f"Максимальная длина текста — {max_length} символов."
        )

    return value
