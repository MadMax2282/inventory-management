from src.utils.exceptions import ValidationError


def require_positive(value, field_name):
    if value is None:
        raise ValidationError("Поле {} не може бути порожнім".format(field_name))
    if value <= 0:
        raise ValidationError("Поле {} має бути більше нуля".format(field_name))
    return value


def require_non_negative(value, field_name):
    if value is None:
        raise ValidationError("Поле {} не може бути порожнім".format(field_name))
    if value < 0:
        raise ValidationError("Поле {} не може бути відʼємним".format(field_name))
    return value


def require_non_empty(value, field_name):
    if value is None or str(value).strip() == "":
        raise ValidationError("Поле {} не може бути порожнім".format(field_name))
    return value


def require_integer(value, field_name):
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValidationError("Поле {} має бути цілим числом".format(field_name))
    return value
