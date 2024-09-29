from django.db.models import Q

from apps.users.models import User


class CustomAuthBackend(object):
    def authenticate(self, request, username=None, password=None):
        try:
            user = User.objects.get(
                Q(email=username)
                | Q(phone_number=username)
                | Q(username=username)
            )

            if user.check_password(password):
                return user
            return None
        except User.DoesNotExist:
            return None
        except Exception as ex:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
