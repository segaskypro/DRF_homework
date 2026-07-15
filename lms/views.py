from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from .models import Course, Lesson, Subscription
from .serializers import CourseSerializer, LessonSerializer
from .permissions import IsModerator, IsOwner, IsModeratorOrOwner
from .paginators import CoursePaginator, LessonPaginator

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['title']
    ordering_fields = ['title']
    ordering = ['title']

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated, ~IsModerator]
        elif self.action == 'list':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['retrieve']:
            permission_classes = [permissions.IsAuthenticated, IsModeratorOrOwner]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [permissions.IsAuthenticated, IsModeratorOrOwner]
        elif self.action == 'destroy':
            permission_classes = [permissions.IsAuthenticated, IsOwner]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Course.objects.none()
        if user.groups.filter(name='moderators').exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = LessonPaginator
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['course']
    ordering_fields = ['title']
    ordering = ['title']

    def get_permissions(self):
        if self.request.method == 'POST':
            permission_classes = [permissions.IsAuthenticated, ~IsModerator]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Lesson.objects.none()
        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            permission_classes = [permissions.IsAuthenticated, IsOwner]
        elif self.request.method in ['PUT', 'PATCH']:
            permission_classes = [permissions.IsAuthenticated, IsModeratorOrOwner]
        else:
            permission_classes = [permissions.IsAuthenticated, IsModeratorOrOwner]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Lesson.objects.none()
        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class SubscriptionView(APIView):
    """
    Эндпоинт для управления подпиской на курс.
    POST /api/subscribe/ - добавить/удалить подписку
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user

        course_id = request.data.get('course_id')
        if not course_id:
            return Response(
                {"error": "Необходимо указать course_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        course = get_object_or_404(Course, id=course_id)

        subscription = Subscription.objects.filter(
            user=user,
            course=course
        )

        if subscription.exists():
            subscription.delete()
            message = 'Подписка удалена'
            is_subscribed = False
        else:
            Subscription.objects.create(
                user=user,
                course=course
            )
            message = 'Подписка добавлена'
            is_subscribed = True

        return Response({
            "message": message,
            "is_subscribed": is_subscribed
        })