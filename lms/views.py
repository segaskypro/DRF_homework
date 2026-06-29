from rest_framework import generics, viewsets, serializers
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer



class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для курсов. Автоматически создает все CRUD методы"""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer



class LessonListCreateView(generics.ListCreateAPIView):
    """
    GET: список всех уроков
    POST: создание нового урока с проверкой существования курса
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def perform_create(self, serializer):
        """Проверяем, что курс с указанным ID существует перед сохранением"""
        course_id = self.request.data.get('course')
        if course_id is None:
            raise serializers.ValidationError({"course": "Это поле обязательно"})

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            raise serializers.ValidationError({"course": f"Курс с id={course_id} не найден"})


        serializer.save(course=course)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: получение одного урока
    PUT/PATCH: обновление урока
    DELETE: удаление урока
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def perform_update(self, serializer):
        """При обновлении тоже проверяем, что курс существует (если его передали)"""
        course_id = self.request.data.get('course')
        if course_id is not None:
            try:
                course = Course.objects.get(id=course_id)
            except Course.DoesNotExist:
                raise serializers.ValidationError({"course": f"Курс с id={course_id} не найден"})
            serializer.save(course=course)
        else:
            serializer.save()