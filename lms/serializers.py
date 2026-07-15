from rest_framework import serializers
from .models import Course, Lesson
from .validators import validate_youtube_url, YouTubeValidator


class CourseSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source='owner.email', read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'preview', 'owner', 'owner_email']
        read_only_fields = ['owner']


class LessonSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)


    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'preview', 'video_url', 'course', 'course_title', 'owner',
                  'owner_email']
        read_only_fields = ['owner']


        validators = [
            YouTubeValidator(field='video_url')
        ]