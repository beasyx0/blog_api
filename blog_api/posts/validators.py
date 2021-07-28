from django.core.exceptions import ValidationError


def validate_title_min_8_words(value):
    words = value.split(' ')
    count = 0
    for word in words:
        count += 1

    if count < 8:
        raise ValidationError(
            'Post title must be 8 words or longer.',
            params={'value': value},
        )
