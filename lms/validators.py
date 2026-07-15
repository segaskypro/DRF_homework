import re
from rest_framework import serializers


def validate_youtube_url(value):
    """
    Валидатор для проверки, что ссылка ведет на youtube.com.
    """
    # Проверяем, что ссылка содержит youtube.com или youtu.be
    if not value:
        return value

    # Регулярное выражение для проверки youtube ссылок
    youtube_pattern = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+'

    if not re.match(youtube_pattern, value):
        raise serializers.ValidationError(
            'Разрешены только ссылки на YouTube (youtube.com или youtu.be)'
        )

    return value


class YouTubeValidator:
    """
    Класс-валидатор для проверки youtube ссылок.
    Используется в Meta.validators сериализатора.
    """

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        # Получаем значение поля
        url = value.get(self.field) if isinstance(value, dict) else value

        if not url:
            return value

        # Проверяем, что ссылка содержит youtube.com или youtu.be
        youtube_pattern = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+'

        if not re.match(youtube_pattern, url):
            raise serializers.ValidationError(
                {self.field: 'Разрешены только ссылки на YouTube (youtube.com или youtu.be)'}
            )

        return value