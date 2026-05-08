from rest_framework.permissions import BasePermission

from apps.accounts.models import User


class IsDirector(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.DIRECTOR


class IsDirectorOrTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [User.Role.DIRECTOR, User.Role.TEACHER]