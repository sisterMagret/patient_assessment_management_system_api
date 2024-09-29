from datetime import date

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.core.exceptions import ValidationError

from apps.utils.abstracts import AbstractUUID
from apps.utils.country.countries import country_codes
from apps.utils.enums import (
    AuthTokenEnum,
    AuthTokenStatusEnum,
    BloodGroupType,
    GenderType,
    UserType,
    Genotype,
    ValidIDType,
)


class Address(AbstractUUID):
    country = models.CharField(
        max_length=30, choices=country_codes, null=True, blank=True
    )
    state = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    zip_code = models.CharField(max_length=20, null=True, blank=True)
    town = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(default="", null=True, blank=True)

    def __str__(self):
        return self.address


class User(AbstractUser, AbstractUUID):
    """
    Custom User Model
    """

    user_role = models.PositiveSmallIntegerField(
        default=UserType.USER, choices=UserType.choices()
    )
    phone_number = models.CharField(
        max_length=20, unique=True, null=True, blank=True
    )
    email = models.EmailField(max_length=255, null=True, blank=True)
    address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        related_name="user_address",
        null=True,
        blank=True,
    )
    gender = models.CharField(
        choices=GenderType.choices(), max_length=255, null=True, blank=True
    )
    avatar = models.ImageField(upload_to="profile", null=True, blank=True)
    is_accept_terms_and_condition = models.BooleanField(
        default=False, blank=True
    )
    first_login = models.BooleanField(default=True, null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    is_verified = models.BooleanField(default=False)

    #
    class Meta:
        db_table = "users"
        ordering = ("-date_joined",)

    def __str__(self):
        return f"{self.phone_number} {self.get_full_name()} {self.id} {self.group()}"

    def group(self):
        """Returns the first group name that the user belongs to."""
        return self.groups.first().name if self.groups.exists() else "user"

    @property
    def age(self):
        """Calculates the user's age based on their date of birth."""
        if self.date_of_birth:
            today = date.today()
            return (
                today.year
                - self.date_of_birth.year
                - (
                    (today.month, today.day)
                    < (self.date_of_birth.month, self.date_of_birth.day)
                )
            )
        return None


class EmergencyContact(AbstractUUID):
    """Stores the emergency contact details of a patient."""

    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name} ({self.phone_number})"


class Allergy(AbstractUUID):
    """Model to represent an allergy."""

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "allergy"

    def __str__(self):
        return self.name


class Medication(AbstractUUID):
    """Model to represent medication."""

    name = models.CharField(max_length=255)

    class Meta:
        db_table = "medication"

    def __str__(self):
        return self.name


class Patient(AbstractUUID):
    """Stores patient-specific information, linked to the User model."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="patient_user",
        null=True,
        blank=True,
    )
    blood_group = models.CharField(
        max_length=3,
        choices=BloodGroupType.choices(),
        null=True,
        blank=True,
    )
    genotype = models.CharField(
        max_length=3, choices=Genotype.choices(), null=True, blank=True
    )
    allergies = models.ManyToManyField(
        Allergy, blank=True, related_name="allergies"
    )
    medications = models.ManyToManyField(Medication, blank=True)
    emergency_contact = models.ForeignKey(
        EmergencyContact,
        null=True,
        related_name="emergency_contact",
        blank=True,
        on_delete=models.SET_NULL,
    )
    nationality = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = "patient"
        ordering = ("user__date_joined",)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.id}"

    def clean(self):
        """Validates that the linked user is of type 'Patient'."""
        if self.user and self.user.user_role != UserType.PATIENT:
            raise ValidationError("The linked user must be a patient.")


class PractitionerSpecialization(AbstractUUID):
    """Model representing a practitioner specialization."""

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Practitioner(AbstractUUID):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="practitioner"
    )
    license_number = models.CharField(
        max_length=100, unique=True, null=True, blank=True
    )
    specializations = models.ManyToManyField(
        PractitionerSpecialization,
        related_name="practitioner_specializations",
    )
    # mode of identification
    means_of_identification_type = models.CharField(
        max_length=50, choices=ValidIDType.choices(), null=True, blank=True
    )
    means_of_identification = models.FileField(
        upload_to="documents/uploaded_ids", null=True, blank=True
    )
    certificate = models.FileField(
        upload_to="documents/certificates", null=True, blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "clinician"
        ordering = ("-user__date_joined",)

    def __str__(self):
        subcategory = f" - {self.subcategory}" if self.subcategory else ""
        return f"{self.user.get_full_name()} - {self.category}{subcategory} at {self.organization.name}"


class AuthToken(AbstractUUID):
    """Authentication Token Model."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="user_token_value",
    )
    type = models.PositiveSmallIntegerField(
        choices=AuthTokenEnum.choices(), default=AuthTokenEnum.VERIFICATION
    )
    token = models.CharField(max_length=255, null=True, blank=True)
    status = models.PositiveSmallIntegerField(
        choices=AuthTokenStatusEnum.choices(),
        default=AuthTokenStatusEnum.PENDING,
        editable=False,
    )
    expiry = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(
        auto_now_add=True, editable=False, null=True, blank=True
    )
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        db_table = "auth_token"
        ordering = ("-created_at",)
        verbose_name = "Token"

    def __str__(self):
        return f"{self.user.get_full_name()} {self.type}"
