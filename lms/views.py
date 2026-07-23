from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from .models import Course, Lesson, Subscription, Payment
from .serializers import CourseSerializer, LessonSerializer, PaymentSerializer
from .permissions import IsModerator, IsOwner, IsModeratorOrOwner
from .paginators import CoursePaginator, LessonPaginator
from .tasks import send_course_update_notification
from rest_framework.decorators import action
from .services.stripe_service import (
    create_stripe_product,
    create_stripe_price,
    create_checkout_session,
    retrieve_session
)

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CoursePaginator
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['title']
    ordering_fields = ['title']
    ordering = ['title']

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated, ~IsModerator]
        elif self.action == 'list':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['retrieve']:
            permission_classes = [permissions.IsAuthenticated, IsModeratorOrOwner]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [permissions.IsAuthenticated, IsModeratorOrOwner]
        elif self.action == 'destroy':
            permission_classes = [permissions.IsAuthenticated, IsOwner]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Course.objects.none()
        if user.groups.filter(name='moderators').exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = LessonPaginator
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['course']
    ordering_fields = ['title']
    ordering = ['title']

    def get_permissions(self):
        if self.request.method == 'POST':
            permission_classes = [permissions.IsAuthenticated, ~IsModerator]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Lesson.objects.none()
        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            permission_classes = [permissions.IsAuthenticated, IsOwner]
        elif self.request.method in ['PUT', 'PATCH']:
            permission_classes = [permissions.IsAuthenticated, IsModeratorOrOwner]
        else:
            permission_classes = [permissions.IsAuthenticated, IsModeratorOrOwner]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Lesson.objects.none()
        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class SubscriptionView(APIView):
    """
    Эндпоинт для управления подпиской на курс.
    POST /api/subscribe/ - добавить/удалить подписку
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user

        course_id = request.data.get('course_id')
        if not course_id:
            return Response(
                {"error": "Необходимо указать course_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        course = get_object_or_404(Course, id=course_id)

        subscription = Subscription.objects.filter(
            user=user,
            course=course
        )

        if subscription.exists():
            subscription.delete()
            message = 'Подписка удалена'
            is_subscribed = False
        else:
            Subscription.objects.create(
                user=user,
                course=course
            )
            message = 'Подписка добавлена'
            is_subscribed = True

        return Response({
            "message": message,
            "is_subscribed": is_subscribed
        })


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @action(detail=False, methods=['post'], url_path='create-payment')
    def create_payment(self, request):
        user = request.user
        course_id = request.data.get('course_id')

        if not course_id:
            return Response(
                {'error': 'Не указан ID курса'},
                status=status.HTTP_400_BAD_REQUEST
            )

        course = get_object_or_404(Course, id=course_id)

        if Payment.objects.filter(user=user, course=course, status='paid').exists():
            return Response(
                {'error': 'Курс уже оплачен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            product_id = create_stripe_product(course)
            price_id = create_stripe_price(product_id, float(course.price))
            session_id, payment_url = create_checkout_session(
                price_id=price_id,
                course_id=course.id,
                user_id=user.id
            )

            payment = Payment.objects.create(
                user=user,
                course=course,
                amount=course.price,
                status=Payment.StatusChoices.PENDING,
                stripe_product_id=product_id,
                stripe_price_id=price_id,
                stripe_session_id=session_id,
                payment_url=payment_url
            )

            return Response({
                'payment_id': payment.id,
                'payment_url': payment_url,
                'status': payment.status,
                'message': 'Платеж создан. Перейдите по ссылке для оплаты.'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'], url_path='check-status')
    def check_status(self, request, pk=None):
        payment = self.get_object()
        try:
            session = retrieve_session(payment.stripe_session_id)
            if session.payment_status == 'paid':
                payment.status = Payment.StatusChoices.PAID
            elif session.payment_status == 'unpaid':
                payment.status = Payment.StatusChoices.PENDING
            payment.save()
            return Response({
                'status': payment.status,
                'paid': payment.status == Payment.StatusChoices.PAID
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )