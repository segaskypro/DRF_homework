from django.contrib import admin
from .models import User, Payment

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone', 'is_staff', 'is_active')
    search_fields = ('email', 'phone')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'payment_date', 'amount', 'payment_method', 'paid_course', 'paid_lesson')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('user__email',)