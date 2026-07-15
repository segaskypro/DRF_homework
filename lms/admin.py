# lms/admin.py

from django.contrib import admin
from .models import Course, Lesson


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'description', 'owner']
    list_filter = ['owner']
    search_fields = ['title', 'description']
    raw_id_fields = ['owner']
    readonly_fields = ['owner']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'course', 'owner']
    list_filter = ['course', 'owner']
    search_fields = ['title', 'description']
    raw_id_fields = ['owner', 'course']
    readonly_fields = ['owner']