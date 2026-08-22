from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from lms.models import Subscription


@shared_task
def send_course_update_notification(course_id, course_title):
    """
    Задача для отправки уведомлений подписчикам курса о его обновлении
    """
    # Получаем всех подписчиков курса
    subscriptions = Subscription.objects.filter(
        course_id=course_id).select_related('user')

    if not subscriptions.exists():
        return f"Нет подписчиков для курса {course_title}"

    emails = [sub.user.email for sub in subscriptions]

    subject = f"Обновление курса: {course_title}"
    message = f"""
    Здравствуйте!

    Курс "{course_title}" был обновлен. 
    Зайдите на платформу, чтобы ознакомиться с обновлениями.

    С уважением,
    Администрация
    """

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=emails,
            fail_silently=False,
        )
        return f"Письма отправлены {len(emails)} подписчикам курса '{course_title}'"
    except Exception as e:
        return f"Ошибка при отправке писем: {str(e)}"
