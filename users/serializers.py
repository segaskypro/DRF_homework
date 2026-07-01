from rest_framework import serializers
from .models import User, Payment


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Payment"""

    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'user', 'user_email', 'payment_date', 'paid_course',
                  'paid_lesson', 'amount', 'payment_method']


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User с историей платежей"""

    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'city', 'avatar', 'payments']
        read_only_fields = ['id', 'email']