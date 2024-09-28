from uuid import UUID

from django.contrib.auth.models import Group
from django.test import TestCase
from faker import Faker
from rest_framework import status
from rest_framework.test import APIClient

from apps.order.models import WishList
from apps.assessment.models import (Product, ProductCategory,
                                  ProductSpecification, ProductSubCategory,
                                  UnitTypes)
from apps.users.models import FarmerSettings, User
from apps.utils.enums import UnitTypeEnum, UserGroup


class ProductApiTest(TestCase):
    endpoint = "/api/v1/product/"
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
        self.group, _ = Group.objects.get_or_create(name=UserGroup.FARMER)
        self.user.groups.add(self.group)
        self.user.save()
        self.farmer_settings = FarmerSettings.objects.get_or_create(user=self.user)

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

        self.category = ProductCategory.objects.create(name="Livestock", slug="lives_stock")

        self.sub_category = ProductSubCategory.objects.create(
            category=self.category,
            name="Cattle",
            slug="cattle",
        )

        self.unit_type_payload = dict(title="Cow", unit=UnitTypeEnum.PIECE)
        self.unit_type = UnitTypes.objects.create(**self.unit_type_payload)
        self.unit_type.save()

        self.product_payload = dict(
            farmer=self.user,
            name="Cow",
            quantity=10,
            delivery_type="pickup",
            sales_price=23000.00,
            discount_price=225000.00,
            description="a fat brown cow",
            estimated_delivery_duration=1,
            unit_type=self.unit_type,
            estimated_delivery_duration_type="day",
            minimum_order_quantity=1,
            category=self.category,
            sub_category=self.sub_category,
        )

        self.product_payload_2 = dict(
            farmer=self.user,
            name="Pig",
            quantity=10,
            delivery_type="pickup",
            sales_price=230000.00,
            discount_price=225000.00,
            description="a fat pig",
            estimated_delivery_duration=1,
            unit_type=self.unit_type,
            estimated_delivery_duration_type="day",
            minimum_order_quantity=1,
            category=self.category,
            sub_category=self.sub_category,
        )

        self.product = Product.objects.create(**self.product_payload)
        self.product_2 = Product.objects.create(**self.product_payload_2)
        self.product.save()
        self.product_specification_payload = dict(
            product=self.product,
            text=self.faker.text(),
            title="Goats",
        )
        self.product_specification = ProductSpecification.objects.create(
            **self.product_specification_payload
        )

        self.wish_list_payload_instance = {
            "user": self.user,
            "product": self.product,
            "quantity": 23,
        }

        self.wish_list_payload = {
            "product": self.product_2.id,
            "quantity": 23,
        }

        self.wish_list = WishList.objects.create(**self.wish_list_payload_instance)

    def test_farmer_product_list(self):
        """
        test farmer product lists
        """
        res = self.client.get(self.endpoint)
        no_auth_res = self.no_auth_client.get(self.endpoint)
        self.assertEqual(no_auth_res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data)

    def test_product_list_dirctory(self):
        res = self.no_auth_client.get(f"/api/v1/product-directory/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data)

    def test_product_details_dirctory(self):
        res = self.no_auth_client.get(f"/api/v1/product-directory/{self.product.id}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data)
        self.assertEqual(UUID(res.data["data"].get("id")), self.product.id)

    def test_create_product(self):
        payload = dict(
            name="pig",
            quantity=10,
            delivery_type="pickup",
            sales_price=23000.00,
            discount_price=225000.00,
            description=self.faker.text(),
            estimated_delivery_duration=1,
            estimated_delivery_duration_type="day",
            minimum_order_quantity=1,
            category=self.category.id,
            sub_category=self.sub_category.id,
            unit_type=self.unit_type.id,
        )

        res = self.client.post(self.endpoint, payload)
        no_auth_res = self.no_auth_client.post(self.endpoint, payload)
        self.assertEqual(no_auth_res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["data"].get("name"), payload.get("name"))
        self.assertEqual(res.data["data"].get("sales_price"), payload.get("sales_price"))
        self.assertEqual(dict(res.data["data"].get("unit_type")).get("id"), self.unit_type.id)

    def test_add_prod_specification(self):
        """
        Test adding product specification
        """
        payload = {"title": "Pig", "text": self.faker.text()}
        res = self.client.post(f"{self.endpoint}{self.product.id}/specification/", payload)
        no_auth_res = self.no_auth_client.get(
            f"{self.endpoint}{self.product.id}/specification/", payload
        )
        self.assertEqual(no_auth_res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res.data)
        self.assertEqual(res.data["data"].get("title"), payload.get("title"))
        self.assertEqual(res.data["data"].get("text"), payload.get("text"))

    def test_delete_prod_sepec(self):
        """
        Test deleting product specification
        """
        res = self.client.delete(
            f"{self.endpoint}remove_specification/{self.product_specification.id}/"
        )
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_product(self):
        """
        Test updating product
        """
        payload = dict(
            name="pig",
            quantity=10,
            delivery_type="pickup",
            sales_price=23000.00,
            discount_price=225000.00,
            description="a fat pig",
            estimated_delivery_duration=1,
            estimated_delivery_duration_type="day",
            minimum_order_quantity=1,
            category=self.category.id,
            sub_category=self.sub_category.id,
            unit_type=self.unit_type.id,
        )
        payload.update({"name": "goats", "quantity": 50})

        res = self.client.put(f"{self.endpoint}{self.product.id}/", payload)
        no_auth_res = self.no_auth_client.put(f"{self.endpoint}{self.product.id}/", payload)
        self.assertEqual(no_auth_res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data)
        self.assertEqual(res.data["data"].get("name"), payload.get("name"))
        self.assertEqual(res.data["data"].get("quantity"), payload.get("quantity"))

    def test_product_details(self):
        res = self.client.get(f"{self.endpoint}{self.product.id}/")
        no_auth_res = self.no_auth_client.get(f"{self.endpoint}{self.product.id}/")
        self.assertEqual(no_auth_res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data)
        self.assertEqual(UUID(res.data.get("id")), self.product.id)

    def test_delete_product(self):
        res = self.client.delete(f"{self.endpoint}{self.product.id}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_unit_type_list(self):
        res = self.client.get(f"/api/v1/unit-type/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data)
        self.assertGreaterEqual(len(res.data), 1)

    def test_add_unit_type(self):
        """
        Test add unit type
        """
        payload = dict(
            unit=UnitTypeEnum.KG,
            title="Bags of rice",
        )
        res = self.client.post(f"/api/v1/unit-type/", payload)
        res_fail = self.client.post(f"/api/v1/unit-type/", self.unit_type_payload)
        no_auth_res = self.no_auth_client.post(f"/api/v1/unit-type/", payload)
        self.assertEqual(no_auth_res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["data"].get("title"), payload.get("title"))
        self.assertEqual(res.data["data"].get("unit"), payload.get("unit"))
        self.assertEqual(res_fail.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_fail.data.get("message"), "Unity type already exist")

    def test_update_unit_type(self):
        """
        Test update unity type
        """
        payload = dict(
            title="Agric Chicken",
            unit=UnitTypeEnum.PIECE,
        )

        res = self.client.put(f"/api/v1/unit-type/{self.unit_type.id}/", payload)
        print(res.data)
        no_auth_res = self.no_auth_client.put(f"/api/v1/unit-type/{self.unit_type.id}/", payload)
        self.assertEqual(no_auth_res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["data"].get("title"), payload.get("title"))
        self.assertEqual(res.data["data"].get("unit"), payload.get("unit"))

    def test_unity_type_details(self):
        res = self.client.get(f"/api/v1/unit-type/{self.unit_type.id}/")
        no_auth_res = self.no_auth_client.get(
            f"/api/v1/unit-type/{self.unit_type.id}/",
        )
        self.assertEqual(no_auth_res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data)
        self.assertEqual(res.data.get("title"), self.unit_type_payload.get("title"))
        self.assertEqual(res.data.get("unit"), self.unit_type_payload.get("unit"))
        self.assertEqual(res.data.get("id"), self.unit_type.id)

    def test_delete_unit_type(self):
        """
        Test remove unit type
        """
        res = self.client.delete(f"/api/v1/unit-type/{self.unit_type.id}/")
        no_auth_res = self.no_auth_client.delete(f"/api/v1/unit-type/{self.unit_type.id}/")
        self.assertEqual(no_auth_res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_wishlist_list(self):
        res = self.client.get(f"/api/v1/wish-list/")
        no_auth_res = self.no_auth_client.get(f"/api/v1/wish-list/")
        self.assertEqual(no_auth_res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_wishlist(self):
        res = self.client.post(f"/api/v1/wish-list/", self.wish_list_payload)
        res_exist = self.client.post(
            f"/api/v1/wish-list/", self.wish_list_payload
        )  # adding same product id in payload
        no_auth_res = self.no_auth_client.post(f"/api/v1/wish-list/", self.wish_list_payload)
        self.assertEqual(no_auth_res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_exist.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_wish_list(self):
        """
        Test update wish_list
        """
        payload = {
            "product": self.product.id,
            "quantity": 1500,
        }

        res = self.client.put(f"/api/v1/wish-list/{self.wish_list.id}/", payload)
        no_auth_res = self.no_auth_client.put(f"/api/v1/wish-list/{self.wish_list.id}/", payload)
        self.assertEqual(no_auth_res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["data"].get("quantity"), payload.get("quantity"))
        self.assertEqual(res.data["data"].get("id"), self.wish_list.id)

    def test_wish_list_detail(self):
        res = self.client.get(f"/api/v1/wish-list/{self.wish_list.id}/")
        no_auth_res = self.no_auth_client.get(f"/api/v1/wish-list/{self.wish_list.id}/")
        self.assertEqual(no_auth_res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data)
        self.assertEqual(res.data.get("quantity"), self.wish_list_payload_instance.get("quantity"))
        self.assertEqual(res.data.get("id"), self.wish_list.id)

    def test_delete_wish_list(self):
        """
        Test remove wish list
        """
        res = self.client.delete(f"/api/v1/wish-list/{self.wish_list.id}/")
        no_auth_res = self.no_auth_client.delete(f"/api/v1/wish-list/{self.wish_list.id}/")
        self.assertEqual(no_auth_res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
