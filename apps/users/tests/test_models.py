from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase

from apps.utils.enums import UserGroup

UserModel = get_user_model()


""" Modular Test """
# test user creation is working for all users
class CustomBaseUserTestCase(TestCase):
    """TestCase for CustomBaseUser model"""

    def setUp(self) -> None:
        self.user_payload = dict(
            first_name="John Doc",
            last_name="John Doe AB",
            email="sistermagret@gmail.com",
            mobile="08139572200",
            password="$rootpa$$",
            username="john_doe",
        )
        self.user = UserModel.objects.create(**self.user_payload)
        self.user.set_password(self.user_payload.get("password"))
        self.group, _ = Group.objects.get_or_create(name=UserGroup.FARMER)
        self.user.groups.add(self.group)
        self.user.save()

    def test_user_creation(self):
        self.assertTrue(len(UserModel.objects.all()) == 1)
        self.assertTrue(self.user.newsletter)
        self.assertEqual(
            UserModel.objects.get(email="sistermagret@gmail.com").email, self.user.email
        )
        self.assertEqual(
            UserModel.objects.get(email="sistermagret@gmail.com").mobile, self.user.mobile
        )
