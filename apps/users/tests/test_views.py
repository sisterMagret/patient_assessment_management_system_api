from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from apps.users.models import AuthToken

User = get_user_model()


class AuthViewSetTests(APITestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            first_name="Uncle",
            last_name="Rukus",
            phone_number="1234567890",
            email="sistermagret007@gmail.com",
            username="sistermagret007@gmail.com",
            password="password123",
            is_accept_terms_and_condition=True,
        )

    def test_login_success(self):
        url = reverse(
            "api-auth-login"
        )  # Ensure this matches your route name
        data = {
            "username": "sistermagret007@gmail.com",
            "password": "password123",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            "token", response.data
        )  # Check if tokens are in the response

    def test_login_invalid_credentials(self):
        url = reverse("api-auth-login")
        data = {
            "username": "testuser",
            "password": "wrongpass",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["message"],
            "Invalid credentials. Please provide valid credentials.",
        )

    def test_register_success(self):
        url = reverse(
            "api-auth-register", kwargs={"account_type": "practitioner"}
        )
        data = dict(
            first_name="Uncle",
            last_name="Rukus",
            phone_number="0808090r4",
            email="sistermagret@gmail.com",
            username="sistermagret@gmail.com",
            password="password123",
            is_accept_terms_and_condition=True,
        )
        response = self.client.post(url, data, format="json")
        print(response.data["message"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["message"], "Account created successfully"
        )

    def test_register_invalid_account_type(self):
        url = reverse(
            "api-auth-register", kwargs={"account_type": "invalid_type"}
        )  # Invalid account type
        data = {
            "username": "newuser",
            "password": "newpass",
            "email": "newuser@example.com",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("message", response.data)
