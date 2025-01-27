# permissions.py
from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'Admin'

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'Manager'

class IsUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'User'
