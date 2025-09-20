from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class IsParentOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(request.user, 'employee'):
            return True
        
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.parent.user == request.user

class IsEmployeeOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return hasattr(request.user, 'employee')