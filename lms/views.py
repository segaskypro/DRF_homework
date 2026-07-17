from rest_framework import viewsets, generics, permissions
from .models import Course, Lesson, Payment
from .serializers import CourseSerializer, LessonSerializer, PaymentSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .services.stripe_service import retrieve_session
from .services.stripe_service import (
    create_stripe_product,
    create_stripe_price,
    create_checkout_session
)


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для курсов. Автоматически создает все CRUD методы"""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer



class LessonListCreateView(generics.ListCreateAPIView):
    """Получение списка уроков и создание нового"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Получение, обновление и удаление одного урока"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet для управления платежами"""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Пользователь видит только свои платежи"""
        user = self.request.user
        if user.is_superuser:
            return Payment.objects.all()
        return Payment.objects.filter(user=user)

    def perform_create(self, serializer):
        """При создании платежа автоматически подставляется текущий пользователь"""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def create_payment(self, request):
        """Создание платежа через Stripe"""
        user = request.user
        course_id = request.data.get('course_id')

        if not course_id:
            return Response(
                {'error': 'Не указан ID курса'},
                status=status.HTTP_400_BAD_REQUEST
            )

        course = get_object_or_404(Course, id=course_id)

        # Проверка цены
        if not course.price or course.price <= 0:
            return Response(
                {'error': 'Курс бесплатный или цена не указана'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверка, не оплачен ли уже курс
        existing_payment = Payment.objects.filter(
            user=user,
            course=course,
            status=Payment.StatusChoices.PAID
        ).exists()

        if existing_payment:
            return Response(
                {'error': 'Курс уже оплачен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 1. Создаём продукт в Stripe
            product_id = create_stripe_product(course)

            # 2. Создаём цену в Stripe
            price_id = create_stripe_price(product_id, float(course.price))

            # 3. Создаём сессию оплаты
            session_id, payment_url = create_checkout_session(
                price_id,
                course.id,
                user.id
            )

            # 4. Сохраняем платёж в базе
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
                'status': payment.status
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Проверка статуса платежа"""
        payment = get_object_or_404(Payment, id=pk, user=request.user)

        try:
            session = retrieve_session(payment.stripe_session_id)

            if session.payment_status == 'paid':
                payment.status = Payment.StatusChoices.PAID
                payment.save()
            elif session.payment_status == 'unpaid':
                payment.status = Payment.StatusChoices.PENDING
                payment.save()

            return Response({
                'id': payment.id,
                'status': payment.status,
                'amount': payment.amount,
                'course': payment.course.title,
                'paid': session.payment_status == 'paid',
                'payment_url': payment.payment_url
            })

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def success(self, request):
        """Callback успешной оплаты"""
        session_id = request.query_params.get('session_id')
        if session_id:
            try:
                payment = Payment.objects.get(stripe_session_id=session_id)
                payment.status = Payment.StatusChoices.PAID
                payment.save()
                return Response({'message': 'Оплата прошла успешно!'})
            except Payment.DoesNotExist:
                return Response(
                    {'error': 'Платеж не найден'},
                    status=status.HTTP_404_NOT_FOUND
                )
        return Response(
            {'error': 'Не указан ID сессии'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['get'])
    def cancel(self, request):
        """Callback отмены оплаты"""
        return Response({'message': 'Оплата отменена'})