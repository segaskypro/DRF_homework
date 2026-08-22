from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User с историей платежей"""

    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'city', 'avatar', 'payments']
        read_only_fields = ['id', 'email']


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации нового пользователя.
    Используется только при создании (POST /api/register/).
    """
    password = serializers.CharField(
        write_only=True,
        min_length=6,
        help_text="Пароль должен быть минимум 6 символов"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        min_length=6,
        help_text="Подтверждение пароля"
    )

    class Meta:
        model = User
        fields = ['email', 'password',
                  'password_confirm', 'phone', 'city', 'avatar']

    def validate_email(self, value):
        """Проверяем, что email уникален"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует')
        return value

    def validate(self, data):
        """Проверяем, что пароли совпадают"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Пароли не совпадают'
            })
        return data

    def create(self, validated_data):
        """Создаем пользователя с хешированным паролем"""
        validated_data.pop('password_confirm')

        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления данных пользователя.
    Не позволяет менять email и пароль.
    Используется при PUT/PATCH /api/users/<id>/
    """

    class Meta:
        model = User
        fields = ['phone', 'city', 'avatar']
