from django.core.exceptions import ValidationError

class SpecialCharacterRequiredValidator:

    def validate(self, password, user=None):
        special_characters = '!@#$%^&*()_+'
        if not any(char in special_characters for char in password):
            raise ValidationError(
                'Your password must contain a special character.'
            )

    def get_help_text(self):
        return "Your password must contain a special character."
