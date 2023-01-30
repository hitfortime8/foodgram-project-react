from django.core.validators import RegexValidator


class SlugValidator(RegexValidator):
    regex = '^[-a-zA-Z0-9_]+$'


class HexValidator(RegexValidator):
    regex = '^#([A-Fa-f0-9]{3,6})$'


class LettersValidator(RegexValidator):
    regex = r'^[\w.@+-]+$'
    message = (
        'Имя пользователя может содержать лишь буквы, цифры и следующие'
        'символы: @,+,-'
    )
