from rest_framework import viewsets, generics, permissions
from .models import Course, Lesson, Payment
from .serializers import CourseSerializer, LessonSerializer, PaymentSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для курсов. Автоматически создает все CRUD методы"""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer



class LessonListCreateView(generics.ListCreateAPIView):
    """Получение списка уроков и создание нового"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Получение, обновление и удаление одного урока"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet для управления платежами"""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Пользователь видит только свои платежи"""
        user = self.request.user
        if user.is_superuser:
            return Payment.objects.all()
        return Payment.objects.filter(user=user)

    def perform_create(self, serializer):
        """При создании платежа автоматически подставляется текущий пользователь"""
        serializer.save(user=self.request.user)