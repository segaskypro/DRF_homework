from django.contrib import admin
from .models import Course, Lesson, Payment, Subscription


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'description', 'owner']
    list_filter = ['owner']
    search_fields = ['title', 'description']




@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'course', 'owner']
    list_filter = ['course', 'owner']
    search_fields = ['title', 'description']
    raw_id_fields = ['owner', 'course']



@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'course', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__email', 'course__title']
    raw_id_fields = ['user', 'course']
    readonly_fields = [
        'stripe_product_id',
        'stripe_price_id',
        'stripe_session_id',
        'payment_url',
        'created_at',
        'updated_at'
    ]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'course', 'created_at']
    list_filter = ['user', 'course']
    search_fields = ['user__email', 'course__title']
    raw_id_fields = ['user', 'course']