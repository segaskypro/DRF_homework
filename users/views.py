from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Payment  # ← добавили User
from .serializers import UserSerializer, PaymentSerializer



class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для модели User"""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Payment с фильтрацией и сортировкой"""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    # Настройка фильтрации и сортировки
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    # Поля для фильтрации
    filterset_fields = ['paid_course', 'paid_lesson', 'payment_method']

    # Поля для сортировки
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']