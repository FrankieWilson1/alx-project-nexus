from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only owners of an object to edit
    or delete it.
    """
    def has_object_permission(self, request, view, obj):
        # Read-only permission allowed for any request only
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permisson are allowed to the owner of the object
        return obj.user == request.user
