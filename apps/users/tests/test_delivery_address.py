import json

from django.contrib.auth.models import Group
from django.test import TestCase
from faker import Faker
from rest_framework import status
from rest_framework.test import APIClient

from apps.e_commerce.models import (Product, ProductCategory,
                                    ProductSpecification, ProductSubCategory)
from apps.users.models import DeliveryAddress, User
from apps.utils.enums import UserGroup


class UserApiTest(TestCase):
    endpoint = "/api/v1/account/delivery-address/"
    faker = Faker()

    def setUp(self):
        self.client = APIClient()
        self.no_auth_client = APIClient()
        self.user_payload = dict(
            first_name="John Doc",
            last_name="John Doe AB",
            mobile="08139572200",
            password="$rootpa$$",
            username="john_doe",
        )
        self.user = User.objects.create(**self.user_payload)
        self.user.set_password(self.user_payload.get("password"))
        self.group, _ = Group.objects.get_or_create(name=UserGroup.BUYER)
        self.user.groups.add(self.group)
        self.user.save()

        self.response = self.client.post(
            "/api/v1/auth/login/",
            dict(
                username=self.user_payload.get("mobile"), password=self.user_payload.get("password")
            ),
        )
        self.assertEqual(self.response.status_code, 200)
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + self.response.data["token"]["access"]
        )

        self.payload = dict(
            user=self.user,
            location_name="Jos",
            address=self.faker.address(),
            country=self.faker.country(),
            city="Jos",
            state="plateau",
            phone_number="09012303432",
        )

        self.delivery_address = DeliveryAddress(**self.payload)
        self.delivery_address.save()

    def test_delivery_address_list(self):
        """
        test delivery address lists
        """
        res = self.client.get(self.endpoint)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data)

    def test_create_delivery_address(self):
        payload = dict(
            location_name="Jos",
            address=self.faker.address(),
            country=self.faker.country(),
            city="Jos",
            state="plateau",
            phone_number="09012303432",
        )
        res = self.client.post(self.endpoint, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_update_delivery_address(self):
        """
        Test updating delivery address
        """
        payload = {
            "location_name": "Hill Station Junction",
            "address": "Dawaki Close, franzy round-about",
            "zip_code": "930105",
            "city": "Jos",
            "state": "plateau",
            "phone_number": "07015502837",
        }
        res = self.client.put(f"{self.endpoint}{self.delivery_address.id}/", payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data)
        self.assertEqual(res.data["data"].get("location_name"), payload.get("location_name"))

    def test_delivery_address_details(self):
        res = self.client.get(f"{self.endpoint}{self.delivery_address.id}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data)

    def test_delete_delivery_address(self):
        res = self.client.delete(f"{self.endpoint}{self.delivery_address.id}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
