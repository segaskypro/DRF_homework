from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from users.views import UserViewSet, RegisterView
from lms.views import CourseViewSet, LessonListCreateView, LessonRetrieveUpdateDestroyView, SubscriptionView, PaymentViewSet

from django.http import HttpResponse

# Настройка Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="DRF Homework API",
        default_version='v1',
        description="API для управления курсами, уроками и платежами",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'courses', CourseViewSet, basename='course')


def home(request):
    return HttpResponse("Добро пожаловать в LMS!")


urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path('api/register/', RegisterView.as_view(), name='register'),
    path(
        'api/login/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair'),
    path(
        'api/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'),
    path('api/', include(router.urls)),
    path(
        'api/lessons/',
        LessonListCreateView.as_view(),
        name='lesson-list-create'),
    path('api/lessons/<int:pk>/',
         LessonRetrieveUpdateDestroyView.as_view(), name='lesson-detail'),
    path('api/subscribe/', SubscriptionView.as_view(), name='subscription'),
    # Swagger
    path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc',
         cache_timeout=0), name='schema-redoc'),
]
