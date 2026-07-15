from rest_framework import viewsets, generics, permissions, status
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import User, Payment
from .serializers import UserSerializer, PaymentSerializer, UserCreateSerializer
from .permissions import IsOwner, IsOwnerOrReadOnly


class RegisterView(generics.CreateAPIView):
    """
    Регистрация нового пользователя.
    Доступно всем (без авторизации).
    """
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Генерируем JWT токены
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели User.

    Доступные действия:
    - list (GET /users/) - список всех пользователей (только админы/модераторы)
    - retrieve (GET /users/{id}/) - просмотр профиля
    - create (POST /users/) - создание пользователя (через регистрацию)
    - update (PUT /users/{id}/) - полное обновление
    - partial_update (PATCH /users/{id}/) - частичное обновление
    - destroy (DELETE /users/{id}/) - удаление пользователя
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """
        Назначаем разные права для разных действий (action).
        """
        if self.action == 'create':
            # Регистрация доступна всем
            permission_classes = [permissions.AllowAny]
        elif self.action in ['list']:
            # Список пользователей - только для авторизованных
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            # Просмотр, обновление, удаление - только владелец
            permission_classes = [permissions.IsAuthenticated, IsOwner]
        else:
            # На всякий случай
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """
        Используем разные сериализаторы для разных действий.
        """
        if self.action == 'create':
            # Для регистрации используем UserCreateSerializer
            return UserCreateSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        """
        Переопределяем create, чтобы при регистрации сразу возвращать токены.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Генерируем JWT токены
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """
        Кастомный экшн: получить информацию о текущем пользователе.
        GET /users/me/
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Payment.

    Пользователь может видеть только свои платежи.
    """

    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['paid_course', 'paid_lesson', 'payment_method']
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']

    def get_permissions(self):
        """
        Только авторизованные пользователи могут работать с платежами.
        """
        if self.action == 'create':
            # Создание платежа - только авторизованные
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['list', 'retrieve']:
            # Просмотр платежей - только авторизованные
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Изменение/удаление платежа - только владелец
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Фильтруем платежи: пользователь видит только свои.
        """
        user = self.request.user

        # Для суперпользователей показываем все
        if user.is_superuser:
            return Payment.objects.all()

        # Обычные пользователи видят только свои платежи
        return Payment.objects.filter(user=user)

    def perform_create(self, serializer):
        """
        При создании платежа автоматически привязываем текущего пользователя.
        """
        serializer.save(user=self.request.user)