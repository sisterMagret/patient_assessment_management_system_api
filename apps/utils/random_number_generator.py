from django.utils.crypto import get_random_string


def unique_alpha_numeric_generator(
    model, field, length=6, allowed_chars="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
):
    unique = get_random_string(length=length, allowed_chars=allowed_chars)
    kwargs = {field: unique}
    qs_exists = model.objects.filter(**kwargs).exists()
    if qs_exists:
        return unique_alpha_numeric_generator(model, field)
    return unique


def unique_number_generator(model, field, length=6, allowed_chars="0123456789"):
    unique = get_random_string(length=length, allowed_chars=allowed_chars)
    kwargs = {field: unique}
    qs_exists = model.objects.filter(**kwargs).exists()
    if qs_exists:
        return unique_number_generator(model, field, length)
    return unique
