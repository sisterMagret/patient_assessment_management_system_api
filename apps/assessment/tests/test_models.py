from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from faker import Faker

from apps.assessment.models import (Product, ProductCategory,
                                  ProductSpecification, ProductSubCategory)
from apps.utils.enums import UserGroup

UserModel = get_user_model()


class ProductModelTestCase(TestCase):
    faker = Faker()

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

        self.category = ProductCategory.objects.create(name="Livestock", slug="lives_stock")

        self.sub_category = ProductSubCategory.objects.create(
            category=self.category,
            name="Cattle",
            slug="cattle",
        )

        self.product_payload = dict(
            farmer=self.user,
            name="cow",
            quantity=10,
            delivery_type="pickup",
            sales_price=23000.00,
            discount_price=225000.00,
            description="a fat brown cow",
            estimated_delivery_duration=1,
            estimated_delivery_duration_type="day",
            minimum_order_quantity=1,
            category=self.category,
            sub_category=self.sub_category,
        )
        self.product = Product.objects.create(**self.product_payload)
        self.product_specification_payload = dict(
            product=self.product,
            text=self.faker.text(),
            title="Goats",
        )
        self.product_specification = ProductSpecification.objects.create(
            **self.product_specification_payload
        )

    def test_product_creation(self):
        self.assertTrue(len(Product.objects.all()) == 1)
        self.assertEqual(self.product.farmer, self.user)
        self.assertEqual(Product.objects.get(farmer=self.user).farmer, self.user)
        self.assertEqual(Product.objects.get(farmer=self.user), self.product)
        self.assertGreaterEqual(Product.objects.get(farmer=self.user).minimum_order_quantity, 1)
        self.assertEqual(Product.objects.get(farmer=self.user).category, self.category)
        self.assertEqual(Product.objects.get(farmer=self.user).sub_category, self.sub_category)

    def test_product_specification(self):
        self.assertTrue(len(ProductSpecification.objects.all()) == 1)
        self.assertEqual(self.product_specification.product, self.product)
        self.assertEqual(
            ProductSpecification.objects.get(product=self.product).product, self.product
        )
