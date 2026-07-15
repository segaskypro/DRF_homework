from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Разрешение: пользователь может работать ТОЛЬКО со своим профилем.
    Используется для объектов User.
    """

    def has_object_permission(self, request, view, obj):
        """
        Проверяем, что объект (User) принадлежит текущему пользователю.
        obj - это объект User, который мы пытаемся получить/изменить/удалить.
        """
        return obj == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение: пользователь может читать любой профиль,
    но изменять/удалять может только свой.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешаем GET, HEAD, OPTIONS запросы всем
        if request.method in permissions.SAFE_METHODS:
            return True

        # Для изменения/удаления проверяем, что это владелец
        return obj == request.user