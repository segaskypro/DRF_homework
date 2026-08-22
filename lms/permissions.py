from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """
    Проверка: пользователь состоит в группе 'moderators'.
    """

    def has_permission(self, request, view):
        # Проверяем, что пользователь авторизован
        if not request.user or not request.user.is_authenticated:
            return False

        # Проверяем, состоит ли пользователь в группе moderators
        return request.user.groups.filter(name='moderators').exists()


class IsOwner(permissions.BasePermission):
    """
    Проверка: пользователь является владельцем объекта.
    """

    def has_object_permission(self, request, view, obj):
        # Проверяем, что у объекта есть поле owner
        if not hasattr(obj, 'owner'):
            return False

        # Проверяем, что текущий пользователь - владелец
        return obj.owner == request.user


class IsModeratorOrOwner(permissions.BasePermission):
    """
    Разрешение: доступно либо модератору, либо владельцу объекта.
    """

    def has_object_permission(self, request, view, obj):
        # Если пользователь не авторизован - запрещаем
        if not request.user or not request.user.is_authenticated:
            return False

        # Модератор имеет доступ ко всем объектам
        if request.user.groups.filter(name='moderators').exists():
            return True

        # Обычный пользователь имеет доступ только к своим объектам
        return obj.owner == request.user
