from django.test import TestCase
from rest_framework.exceptions import ValidationError
from ..models import (
    User,
    Address,
    Patient,
    Medication,
    Allergy,
    EmergencyContact,
)
from ..serializer import (
    AddressSerializer,
    UserSerializer,
    PatientRegistrationSerializer,
    PatientFormSerializer,
)


class AddressSerializerTest(TestCase):
    def setUp(self):
        self.address_data = {
            "country": "USA",
            "state": "California",
            "city": "Los Angeles",
            "address": "123 Sunset Blvd",
        }
        self.invalid_address_data = {
            "country": "",
            "state": "California",
            "city": "Los Angeles",
        }

    def test_valid_address_serializer(self):
        serializer = AddressSerializer(data=self.address_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["country"], "USA")

    def test_invalid_address_serializer(self):
        serializer = AddressSerializer(data=self.invalid_address_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("country", serializer.errors)


class UserSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="john_rukus",
            email="sistermagret@gmail.com",
            first_name="John",
            last_name="Rukus",
        )

    def test_full_name(self):
        serializer = UserSerializer(instance=self.user)
        self.assertEqual(serializer.data["full_name"], "John Rukus")


class PatientRegistrationSerializerTest(TestCase):
    def setUp(self):
        self.data = {
            "first_name": "Uncle",
            "last_name": "Rukus",
            "phone_number": "1234567890",
            "email": "sistermagret007@gmail.com",
            "username": "sistermagret007@gmail.com",
            "password": "password123",
            "is_accept_terms_and_condition": True,
        }

    def test_create_patient(self):
        serializer = PatientRegistrationSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        patient = serializer.save()
        self.assertEqual(patient.username, "sistermagret007@gmail.com")
        self.assertTrue(Patient.objects.filter(user=patient).exists())


class PatientFormSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="uncle_rukus",
            email="sistermagret64@gmail.com",
            first_name="Uncle",
            last_name="Rukus",
        )
        self.patient = Patient.objects.create(user=self.user)
        self.med1 = Medication.objects.create(name="Aspirin")
        self.med2 = Medication.objects.create(name="Ibuprofen")
        self.allergy = Allergy.objects.create(name="Peanuts")

    def test_invalid_medication(self):
        data = {"medications": ["invalid_id"]}
        serializer = PatientFormSerializer(
            instance=self.patient, data=data
        )
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
