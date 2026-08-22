from django.db import models
from django.conf import settings


class Course(models.Model):
    """Модель курса"""

    title = models.CharField(max_length=200, verbose_name="Название")
    preview = models.ImageField(
        upload_to='courses/previews/',
        blank=True,
        null=True,
        verbose_name="Превью")
    description = models.TextField(
        blank=True, null=True, verbose_name="Описание")

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Цена курса"
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses',
        verbose_name="Владелец",
        null=True,
        blank=True
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата последнего обновления"
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Lesson(models.Model):
    """Модель урока"""

    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(
        blank=True, null=True, verbose_name="Описание")
    preview = models.ImageField(
        upload_to='lessons/previews/',
        blank=True,
        null=True,
        verbose_name="Превью")
    video_url = models.URLField(
        max_length=500, blank=True, null=True, verbose_name="Ссылка на видео")

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name="Курс"
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name="Владелец",
        null=True,
        blank=True
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"


class Subscription(models.Model):
    """Модель подписки на обновления курса"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name="Пользователь"
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name="Курс"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата подписки"
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        # Гарантируем уникальность пары пользователь + курс
        unique_together = ['user', 'course']

    def __str__(self):
        return f"{self.user.email} → {self.course.title}"


class Payment(models.Model):
    """Модель для хранения данных о платежах через Stripe"""

    class StatusChoices(models.TextChoices):
        PENDING = 'pending', 'Ожидание оплаты'
        PAID = 'paid', 'Оплачено'
        FAILED = 'failed', 'Ошибка оплаты'
        CANCELED = 'canceled', 'Отменен'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name="Пользователь"
    )

    course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name="Курс"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма платежа"
    )

    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
        verbose_name="Статус"
    )

    stripe_product_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID продукта в Stripe"
    )

    stripe_price_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID цены в Stripe"
    )

    stripe_session_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID сессии в Stripe"
    )

    payment_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Ссылка на оплату"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    def __str__(self):
        return f"Платеж #{self.id} - {self.user.email} - {self.course.title} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ['-created_at']
