from rest_framework.permissions import BasePermission


class IsVendor(BasePermission):
    """Allows access only to vendors."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_vendor()


class IsCustomer(BasePermission):
    """Allows access to only customers."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_customer()