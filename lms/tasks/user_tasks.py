from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from users.models import User


@shared_task
def deactivate_inactive_users():
    """
    Задача для блокировки пользователей, которые не заходили более месяца
    """
    month_ago = timezone.now() - timedelta(days=30)

    # Находим пользователей, у которых last_login меньше месяца назад или null
    inactive_users = User.objects.filter(
        is_active=True,
        last_login__lt=month_ago
    )

    count = inactive_users.count()

    if count > 0:
        # Блокируем пользователей батчем
        inactive_users.update(is_active=False)

    return f"Заблокировано {count} пользователей"