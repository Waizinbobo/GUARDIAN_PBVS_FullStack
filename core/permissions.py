from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsStaffOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or bool(request.user and request.user.is_staff)


class IsOwnerOrStaff(BasePermission):
    def has_object_permission(self, request, view, obj):
        owner = getattr(obj, 'requested_by', None) or getattr(obj, 'reporter', None) or getattr(obj, 'appellant', None)
        return bool(request.user.is_staff or owner == request.user)
