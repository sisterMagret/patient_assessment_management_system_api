from functools import wraps

from rest_framework import status
from rest_framework.response import Response

from apps.utils.enums import UserGroup


def practitioner_access_only():
    """
    Grant permission to practitioners alone
    """

    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):

            if not request.user.groups.filter(
                name=UserGroup.PRACTITIONER
            ).exists():
                return Response(
                    {
                        "status": status.HTTP_403_FORBIDDEN,
                        "message": "You currently do not have access to this resource",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            response = func(request, *args, **kwargs)
            return response

        return wrapper

    return decorator


def patient_access_only():
    """
    Grant permission to patient alone
    """

    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):

            if not request.user.groups.filter(
                name=UserGroup.USER
            ).exists():
                return Response(
                    {
                        "status": status.HTTP_403_FORBIDDEN,
                        "message": "You currently do not have access to this resource",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            response = func(request, *args, **kwargs)
            return response

        return wrapper

    return decorator


def staff_user_access_only():
    """
    Grant permission to super and staff users only
    """

    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_superuser or not request.user.is_staff:
                return Response(
                    {
                        "status": status.HTTP_403_FORBIDDEN,
                        "message": "You currently do not have access to this resource",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            response = func(request, *args, **kwargs)
            return response

        return wrapper

    return decorator
