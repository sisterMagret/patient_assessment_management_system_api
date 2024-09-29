import logging
import uuid

from django.conf import settings
from django.contrib.auth.models import Group
from apps.utils.enums import (
    BloodGroupType,
    GenderType,
    Genotype,
    UserGroup,
    UserType,
    ValidIDType,
)
from rest_framework import serializers
from .models import (
    Address,
    Allergy,
    PractitionerSpecialization,
    User,
    EmergencyContact,
    Medication,
    Patient,
    Practitioner,
)
from apps.utils.constant import DATETIME_FORMAT, DATE_FORMAT


logger = logging.getLogger("user")


def generate_uuid(model, column):
    """
    Generate a unique UUID for a specified column in a model.
    """
    unique = str(uuid.uuid4())
    kwargs = {column: unique}
    qs_exists = model.objects.filter(**kwargs).exists()
    if qs_exists:
        return generate_uuid(model, column)
    return unique


class AddressSerializer(serializers.ModelSerializer):
    """
    Serializer for the Address model.
    """

    country = serializers.CharField(
        required=True, help_text="Country of residence"
    )
    state = serializers.CharField(
        required=True, help_text="State or region of residence"
    )
    city = serializers.CharField(
        required=True, help_text="City of residence"
    )
    zip_code = serializers.CharField(
        required=False, help_text="Postal code of the address"
    )
    town = serializers.CharField(
        required=False, help_text="Town within the city or region"
    )
    address = serializers.CharField(
        required=True, help_text="Full street address"
    )

    class Meta:
        model = Address
        fields = [
            "id",
            "country",
            "state",
            "city",
            "zip_code",
            "town",
            "address",
        ]
        read_only_fields = ["id"]

    def update(self, instance, validated_data):
        """Update Address instance fields."""

        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model, including nested address and avatar logic.
    """

    date_joined = serializers.DateTimeField(
        format=DATETIME_FORMAT, read_only=True
    )
    group = serializers.CharField(
        read_only=True, help_text="User group based on their role"
    )
    full_name = serializers.SerializerMethodField(
        "get_name", help_text="User's full name"
    )
    # avatar = serializers.SerializerMethodField(
    #     "get_avatar", help_text="User's avatar URL"
    # )
    address = AddressSerializer(read_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "phone_number",
            "address",
            "gender",
            # "avatar",
            "is_accept_terms_and_condition",
            "date_of_birth",
            "group",
            "date_joined",
            "is_active",
            "age",
            "full_name",
            "is_verified",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "id": {"read_only": True},
        }

    @staticmethod
    def get_avatar(obj):
        """
        Retrieve the full URL of the user's avatar.
        """
        if obj.avatar:
            return f"{settings.BASE_BE_URL}{obj.avatar.url}"
        return None

    @staticmethod
    def get_name(obj):
        """
        Retrieve the full name.
        """
        if obj.get_full_name():
            return obj.get_full_name()
        return None


class UserMiniSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for basic User information.
    """

    class Meta:
        model = User
        fields = ["username", "email", "id"]


class OauthCodeSerializer(serializers.Serializer):
    """
    Serializer for handling OAuth authorization codes.
    """

    code = serializers.CharField(
        required=True, help_text="OAuth authorization code"
    )


class UserFormSerializer(serializers.Serializer):
    """
    Form serializer for updating basic user information.
    """

    first_name = serializers.CharField(
        required=False, help_text="First name of the user"
    )
    last_name = serializers.CharField(
        required=False, help_text="Last name of the user"
    )
    username = serializers.CharField(
        required=False, help_text="Username of the user"
    )
    phone_number = serializers.CharField(
        required=False, help_text="Phone number of the user"
    )
    email = serializers.CharField(
        required=False, help_text="Email address of the user"
    )
    address = AddressSerializer(
        required=False, help_text="User's address information"
    )
    gender = serializers.ChoiceField(
        choices=GenderType.choices(), required=False
    )
    date_of_birth = serializers.DateField(
        format=DATE_FORMAT, required=False
    )

    def validate(self, attrs):
        if "address" in attrs:
            attrs["address"], _ = Address.objects.get_or_create(
                **attrs["address"]
            )
        return attrs

    def update(self, instance, validated_data):
        """Update User instance fields."""
        address_data = validated_data.pop("address", None)
        print()
        for k, v in validated_data.items():
            setattr(instance, k, v)
        if address_data:
            instance.address = address_data
        instance.save()
        return instance


class PatientRegistrationSerializer(serializers.Serializer):
    """
    Serializer for registering a new patient.
    """

    first_name = serializers.CharField(
        required=True, help_text="First name of the patient"
    )
    last_name = serializers.CharField(
        required=True, help_text="Last name of the patient"
    )
    phone_number = serializers.CharField(
        required=True, help_text="Phone number of the patient"
    )
    email = serializers.EmailField(
        required=False, help_text="Email address of the patient"
    )
    username = serializers.CharField(
        required=False, help_text="Username for patient login"
    )
    password = serializers.CharField(
        required=True,
        min_length=8,
        write_only=True,
        help_text="Password for patient login",
    )
    is_accept_terms_and_condition = serializers.BooleanField(
        required=True, help_text="Acceptance of terms and conditions"
    )

    def create(self, validated_data):
        """Create a new User (as a Patient) and assign them to the 'USER' group."""
        username = validated_data.pop("username") or generate_uuid(
            User, "username"
        )

        instance = User.objects.create(
            username=username, user_role=UserType.USER, **validated_data
        )
        instance.set_password(validated_data.get("password"))
        instance.save()

        group, _ = Group.objects.get_or_create(name=UserGroup.USER)
        Patient.objects.create(user=instance)
        instance.groups.add(group)
        return instance


class EmergencyContactSerializer(serializers.ModelSerializer):
    """
    Serializer for Emergency Contact information.
    """

    name = serializers.CharField(
        required=True, help_text="Name of the emergency contact"
    )
    phone_number = serializers.CharField(
        required=True, help_text="Phone number of the emergency contact"
    )

    class Meta:
        model = EmergencyContact
        fields = ["id", "name", "phone_number"]
        read_only_fields = ["id"]


class MedicationSerializer(serializers.ModelSerializer):
    """
    Serializer for medication data.
    """

    name = serializers.CharField(
        required=True, help_text="Name of the medication"
    )

    class Meta:
        model = Medication
        fields = ["id", "name"]
        read_only_fields = ["id"]


class AllergySerializer(serializers.ModelSerializer):
    """
    Serializer for allergy information.
    """

    name = serializers.CharField(required=True, help_text="Allergy name")
    description = serializers.CharField(
        required=False, help_text="Allergy description"
    )

    class Meta:
        model = Allergy
        fields = ["id", "name", "description"]
        read_only_fields = ["id"]


class PractitionerSpecializationSerializer(serializers.ModelSerializer):
    """
    Serializer for practitioner specialization data.
    """

    name = serializers.CharField(
        required=True, help_text="Specialization name"
    )
    description = serializers.CharField(
        required=False, help_text="Description of the specialization"
    )

    class Meta:
        model = PractitionerSpecialization
        fields = ["id", "name", "description"]
        read_only_fields = ["id"]


class PatientSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying a patient's full information.
    """

    user = UserSerializer(
        read_only=True, help_text="Basic user information"
    )
    emergency_contact = EmergencyContactSerializer(
        read_only=True, help_text="Emergency contact details"
    )
    medications = MedicationSerializer(
        read_only=True, many=True, help_text="List of medications"
    )
    allergies = AllergySerializer(
        read_only=True, many=True, help_text="List of allergies"
    )

    class Meta:
        model = Patient
        fields = [
            "id",
            "user",
            "blood_group",
            "allergies",
            "medications",
            "emergency_contact",
            "nationality",
        ]
        read_only_fields = ["id"]


class PatientFormSerializer(serializers.Serializer):
    emergency_contact = serializers.CharField(
        required=False, help_text="ID of emergency contact"
    )
    medications = serializers.ListSerializer(
        child=serializers.CharField(required=False),
        required=False,
        help_text="IDs of medications",
    )
    allergies = serializers.ListSerializer(
        child=serializers.CharField(required=False),
        required=False,
        help_text="IDs of allergies",
    )

    blood_group = serializers.ChoiceField(
        choices=BloodGroupType.choices(), required=False
    )
    genotype = serializers.ChoiceField(
        choices=Genotype.choices(), required=False
    )
    nationality = serializers.CharField(required=False)

    def update(self, instance, validated_data):
        payload = {
            "blood_group": validated_data.get("blood_group"),
            "genotype": validated_data.get("genotype"),
            "nationality": validated_data.get("nationality"),
            "emergency_contact": validated_data.get("emergency_contact"),
        }
        self.update_patient_fields(instance, payload)

        if validated_data.get("medications") is not None:
            self.update_related_fields(
                instance,
                validated_data,
                "medications",
                instance.medications,
            )

        if validated_data.get("allergies") is not None:
            self.update_related_fields(
                instance, validated_data, "allergies", instance.allergies
            )

        instance.save()
        return instance

    def update_patient_fields(self, instance, validated_data):
        """Update simple fields of the patient instance."""

        Patient.objects.filter(id=instance.id).update(**validated_data)
        instance.refresh_from_db()

    def update_related_fields(
        self, instance, validated_data, field_name, related_manager
    ):
        """Update many-to-many related fields."""
        related_ids = validated_data.pop(field_name, None)

        if related_ids is not None:
            if related_ids:
                current_related_ids = set(
                    related_manager.values_list("id", flat=True)
                )
                new_related_ids = set(related_ids)

                # Remove relationships that are no longer valid
                to_remove = current_related_ids - new_related_ids
                if to_remove:
                    for pr in related_manager.filter(id__in=to_remove):
                        related_manager.remove(pr)

                # Add new relationships
                related_manager.set(new_related_ids)
            else:
                related_manager.clear()

    def validate(self, attrs):
        """
        Validates and checks for the existence of IDs for medications, allergies,
        medical_conditions, and emergency_contact fields in the attrs dictionary.
        """
        attrs["medications"] = self.validate_related_ids(
            attrs.get("medications"), Medication, "medication"
        )
        attrs["allergies"] = self.validate_related_ids(
            attrs.get("allergies"), Allergy, "allergy"
        )

        # Validate 'emergency_contact'
        if emergency_contact_id := attrs.get("emergency_contact"):
            if not EmergencyContact.objects.filter(
                pk=emergency_contact_id
            ).exists():
                raise serializers.ValidationError(
                    "Invalid emergency contact ID."
                )
            attrs["emergency_contact"] = EmergencyContact.objects.get(
                pk=emergency_contact_id
            )

        return attrs

    def validate_related_ids(self, ids, model, field_name):
        """Validate that IDs exist in the database for a given model."""
        if ids and isinstance(ids, list):
            valid_ids = set(
                model.objects.filter(id__in=ids).values_list(
                    "id", flat=True
                )
            )
            if len(valid_ids) != len(ids):
                raise serializers.ValidationError(
                    f"One or more {field_name} IDs are invalid."
                )
            return valid_ids
        return set()


class PractitionerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    specializations = PractitionerSpecializationSerializer(
        read_only=True, many=True
    )

    class Meta:
        model = Practitioner
        fields = [
            "id",
            "user",
            "license_number",
            "specializations",
            "means_of_identification_type",
            "means_of_identification",
            "certificate",
            "updated_at",
        ]


class PractitionerMiniSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    specializations = PractitionerSpecializationSerializer(
        read_only=True, many=True
    )

    class Meta:
        model = Practitioner
        fields = ["id", "specializations", "user"]


class PractitionerDocumentUploadSerializer(serializers.Serializer):
    means_of_identification_type = serializers.ChoiceField(
        choices=ValidIDType.choices(), required=False
    )
    means_of_identification = serializers.FileField(required=False)
    certificate = serializers.FileField(
        required=False, help_text="Practitioner certificate."
    )

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class PractitionerFormSerializer(serializers.Serializer):
    license_number = serializers.CharField(required=False)
    specializations = serializers.ListSerializer(
        child=serializers.CharField(required=False),
        required=False,
        help_text="IDs of specializations",
    )

    def update(self, instance, validated_data):
        specializations = validated_data.pop("specializations", None)

        for k, v in validated_data.items():
            setattr(instance, k, v)

        if specializations is not None:
            instance.specializations.set(
                specializations if specializations else []
            )

        instance.save()
        return instance

    def validate(self, attrs):
        specializations = attrs.get("specializations")
        if specializations and isinstance(specializations, list):
            specialization_ids = set(specializations)
            if not (0 < len(specialization_ids) <= 2):
                raise serializers.ValidationError(
                    "You must select between 1 and 2 specializations."
                )
            valid_specs = PractitionerSpecialization.objects.filter(
                id__in=specialization_ids
            ).values_list("id", flat=True)
            if len(valid_specs) != len(specialization_ids):
                raise serializers.ValidationError(
                    "One or more selected specializations do not exist."
                )
            attrs["specializations"] = valid_specs

        return attrs


class PractitionerRegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)
    email = serializers.EmailField(required=False)
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=True, min_length=8)
    is_accept_terms_and_condition = serializers.BooleanField(required=True)

    def create(self, validated_data):
        username = validated_data.pop("username") or generate_uuid(
            User, "username"
        )
        user_data = {
            "username": username,
            "user_role": UserType.PRACTITIONER,
            "first_name": validated_data["first_name"],
            "last_name": validated_data["last_name"],
            "phone_number": validated_data["phone_number"],
            "email": validated_data.get("email", ""),
            "is_accept_terms_and_condition": validated_data[
                "is_accept_terms_and_condition"
            ],
        }

        user_instance = User.objects.create(**user_data)
        user_instance.set_password(validated_data["password"])
        user_instance.save()

        group, _ = Group.objects.get_or_create(name=UserGroup.PRACTITIONER)
        Practitioner.objects.create(user=user_instance)
        user_instance.groups.add(group)
        user_instance.save()

        return user_instance

    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance
