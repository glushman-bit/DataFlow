import phonenumbers
from django.core.exceptions import ValidationError


def validate_phone(field, value):
    """Проверяет и нормализует номер телефона."""

    if value in (None, ""):
        if field.required:
            raise ValidationError("Поле обязательно для заполнения.")

        return None

    if not isinstance(value, str):
        raise ValidationError("Номер телефона должен быть текстом.")

    try:
        phone_number = phonenumbers.parse(value, None)

        if not phonenumbers.is_valid_number(phone_number):
            raise ValidationError("Введите корректный номер телефона.")

        return phonenumbers.format_number(
            phone_number,
            phonenumbers.PhoneNumberFormat.E164,
        )

    except phonenumbers.NumberParseException:
        raise ValidationError(
            "Введите номер в международном формате, например +79991234567."
        )
