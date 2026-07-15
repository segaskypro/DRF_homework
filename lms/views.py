# lms/views.py

from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from .permissions import IsModerator, IsOwner, IsModeratorOrOwner


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Course.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['title']
    ordering_fields = ['title']
    ordering = ['title']

    def get_permissions(self):
        """
        Назначаем разные права для разных действий (action).
        """
        if self.action == 'create':
            # Создание курса: только для обычных пользователей (не модераторов)
            permission_classes = [permissions.IsAuthenticated, ~IsModerator]
        elif self.action == 'list':
            # Список курсов: только для авторизованных
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['retrieve']:
            # Просмотр курса: модератор или владелец
            permission_classes = [permissions.IsAuthenticated, IsModeratorOrOwner]
        elif self.action in ['update', 'partial_update']:
            # Обновление курса: модератор или владелец
            permission_classes = [permissions.IsAuthenticated, IsModeratorOrOwner]
        elif self.action == 'destroy':
            # Удаление курса: только владелец (модератор не может удалять)
            permission_classes = [permissions.IsAuthenticated, IsOwner]
        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Фильтруем курсы: если пользователь модератор - показывает все,
        иначе - только свои.
        """
        user = self.request.user

        if not user or not user.is_authenticated:
            return Course.objects.none()

        if user.groups.filter(name='moderators').exists():
            return Course.objects.all()

        return Course.objects.filter(owner=user)

    def perform_create(self, serializer):
        """
        При создании курса автоматически устанавливаем владельца.
        """
        serializer.save(owner=self.request.user)


class LessonListCreateView(generics.ListCreateAPIView):
    """
    Generic-класс для:
    - GET /lessons/ - список уроков
    - POST /lessons/ - создание урока
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['course']
    ordering_fields = ['title']
    ordering = ['title']

    def get_permissions(self):
        """
        Разные права для разных методов.
        """
        if self.request.method == 'POST':
            # Создание урока: только для обычных пользователей (не модераторов)
            permission_classes = [permissions.IsAuthenticated, ~IsModerator]
        else:
            # GET: только для авторизованных
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Фильтруем уроки: модератор видит все, обычный пользователь - только свои.
        """
        user = self.request.user

        if not user or not user.is_authenticated:
            return Lesson.objects.none()

        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()

        return Lesson.objects.filter(owner=user)

    def perform_create(self, serializer):
        """
        При создании урока автоматически устанавливаем владельца.
        """
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Generic-класс для:
    - GET /lessons/{id}/ - просмотр урока
    - PUT /lessons/{id}/ - полное обновление
    - PATCH /lessons/{id}/ - частичное обновление
    - DELETE /lessons/{id}/ - удаление урока
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        """
        Разные права для разных методов.
        """
        if self.request.method == 'DELETE':
            # Удаление: только владелец (модератор не может удалять)
            permission_classes = [permissions.IsAuthenticated, IsOwner]
        elif self.request.method in ['PUT', 'PATCH']:
            # Обновление: модератор или владелец
            permission_classes = [permissions.IsAuthenticated, IsModeratorOrOwner]
        else:
            # GET: модератор или владелец
            permission_classes = [permissions.IsAuthenticated, IsModeratorOrOwner]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Фильтруем уроки для безопасности.
        """
        user = self.request.user

        if not user or not user.is_authenticated:
            return Lesson.objects.none()

        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()

        return Lesson.objects.filter(owner=user)