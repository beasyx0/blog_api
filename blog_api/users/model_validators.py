from django.core.exceptions import ValidationError


def validate_username_min_3_letters(value):
    letters = [l for l in value if l.isalpha()]
    if len(letters) < 3:
        raise ValidationError(
            'Your username must contain at least 3 letters.',
            params={'value': value},
        )


def validate_username_max_3_special_chars(value):
        special_character_count = 0
        for char in value:
            if not char.isalnum():
                special_character_count += 1

        if not special_character_count < 3:
            raise ValidationError(
                'Your username must have less than 3 special characters e.g. @/./+/-/_ and no spaces.',
                params={'value': value},
            )


def validate_name_no_special_chars(value):
    if any(not c.isalnum() for c in value if not c == ' '):
        raise ValidationError(
            'Your name must have no special characters e.g. @/./+/-/_ ',
            params={'value': value},
        )