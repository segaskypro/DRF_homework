import stripe
from django.conf import settings

# Настройка Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product(course):
    """
    Создает продукт в Stripe.
    Возвращает ID созданного продукта.
    """
    try:
        product = stripe.Product.create(
            name=course.title,
            description=course.description or '',
            metadata={
                'course_id': course.id,
            }
        )
        return product.id
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка создания продукта в Stripe: {str(e)}")


def create_stripe_price(product_id, amount):
    """
    Создает цену в Stripe.
    Цена передается в копейках (умножаем на 100).
    Возвращает ID созданной цены.
    """
    try:
        # Stripe принимает сумму в минимальной единице валюты (копейки)
        amount_in_cents = int(amount * 100)
        price = stripe.Price.create(
            product=product_id,
            unit_amount=amount_in_cents,
            currency='rub',
        )
        return price.id
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка создания цены в Stripe: {str(e)}")


def create_checkout_session(price_id, course_id, user_id):
    """
    Создает сессию оплаты в Stripe.
    Возвращает ID сессии и URL для оплаты.
    """
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price': price_id,
                    'quantity': 1,
                }
            ],
            mode='payment',
            success_url='http://localhost:8000/api/payments/success/?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://localhost:8000/api/payments/cancel/',
            metadata={
                'course_id': course_id,
                'user_id': user_id,
            }
        )
        return session.id, session.url
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка создания сессии оплаты в Stripe: {str(e)}")


def retrieve_session(session_id):
    """
    Получает данные сессии из Stripe по её ID.
    """
    try:
        return stripe.checkout.Session.retrieve(session_id)
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка получения сессии из Stripe: {str(e)}")