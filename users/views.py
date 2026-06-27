from rest_framework import viewsets
from .models import User
from .serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для пользователей. Позволяет выполнять CRUD операции."""
    queryset = User.objects.all()
    serializer_class = UserSerializer