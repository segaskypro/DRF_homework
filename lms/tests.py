from django.test import TestCase
from django.contrib.auth.models import Group
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from users.models import User
from .models import Course, Lesson, Subscription


class LessonTests(TestCase):
    """Тесты для уроков"""

    def setUp(self):
        """Подготовка данных перед каждым тестом"""
        # Создаем пользователей
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='123456'
        )
        self.moderator = User.objects.create_user(
            email='moderator@example.com',
            password='123456'
        )

        # Создаем группу модераторов
        self.moderator_group, _ = Group.objects.get_or_create(
            name='moderators')
        self.moderator.groups.add(self.moderator_group)

        # Создаем курс
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.user
        )

        # Создаем урок
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            description='Test Lesson Description',
            video_url='https://www.youtube.com/watch?v=abc123',
            course=self.course,
            owner=self.user
        )

        # Создаем клиенты
        self.client = APIClient()
        self.user_client = APIClient()
        self.user_client.force_authenticate(user=self.user)

        self.moderator_client = APIClient()
        self.moderator_client.force_authenticate(user=self.moderator)

    def test_create_lesson_success(self):
        """Тест успешного создания урока"""
        url = '/api/lessons/'
        data = {
            'title': 'New Lesson',
            'description': 'New Description',
            'video_url': 'https://www.youtube.com/watch?v=xyz789',
            'course': self.course.id
        }
        response = self.user_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)
        self.assertEqual(response.data['owner'], self.user.id)

    def test_create_lesson_invalid_youtube(self):
        """Тест создания урока с невалидной ссылкой (не YouTube)"""
        url = '/api/lessons/'
        data = {
            'title': 'Invalid Lesson',
            'description': 'Invalid Description',
            'video_url': 'https://rutube.ru/video/123',
            'course': self.course.id
        }
        response = self.user_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('video_url', response.data)

    def test_create_lesson_moderator_forbidden(self):
        """Тест: модератор не может создать урок"""
        url = '/api/lessons/'
        data = {
            'title': 'Moderator Lesson',
            'description': 'Moderator Description',
            'video_url': 'https://www.youtube.com/watch?v=abc123',
            'course': self.course.id
        }
        response = self.moderator_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_lessons_user(self):
        """Тест: пользователь видит только свои уроки"""
        url = '/api/lessons/'
        response = self.user_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['owner'], self.user.id)

    def test_list_lessons_moderator(self):
        """Тест: модератор видит все уроки"""
        url = '/api/lessons/'
        response = self.moderator_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Модератор видит все уроки (созданный пользователем)
        self.assertEqual(len(response.data['results']), 1)

    def test_update_lesson_owner(self):
        """Тест: владелец может обновить урок"""
        url = f'/api/lessons/{self.lesson.id}/'
        data = {'title': 'Updated Lesson Title'}
        response = self.user_client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Updated Lesson Title')

    def test_update_lesson_moderator(self):
        """Тест: модератор может обновить любой урок"""
        url = f'/api/lessons/{self.lesson.id}/'
        data = {'title': 'Updated by Moderator'}
        response = self.moderator_client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Updated by Moderator')

    def test_delete_lesson_owner(self):
        """Тест: владелец может удалить урок"""
        url = f'/api/lessons/{self.lesson.id}/'
        response = self.user_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_delete_lesson_moderator_forbidden(self):
        """Тест: модератор не может удалить урок"""
        url = f'/api/lessons/{self.lesson.id}/'
        response = self.moderator_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SubscriptionTests(TestCase):
    """Тесты для подписок"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='123456'
        )
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.user
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_subscribe_success(self):
        """Тест успешной подписки"""
        url = '/api/subscribe/'
        data = {'course_id': self.course.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка добавлена')
        self.assertTrue(response.data['is_subscribed'])
        self.assertEqual(Subscription.objects.count(), 1)

    def test_unsubscribe_success(self):
        """Тест успешной отписки"""
        # Сначала подписываемся
        Subscription.objects.create(user=self.user, course=self.course)

        url = '/api/subscribe/'
        data = {'course_id': self.course.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка удалена')
        self.assertFalse(response.data['is_subscribed'])
        self.assertEqual(Subscription.objects.count(), 0)

    def test_subscribe_invalid_course(self):
        """Тест подписки на несуществующий курс"""
        url = '/api/subscribe/'
        data = {'course_id': 999}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_subscribe_missing_course_id(self):
        """Тест подписки без указания course_id"""
        url = '/api/subscribe/'
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
