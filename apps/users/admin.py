from django.contrib import admin
from .forms import CustomUserChangeForm, CustomUserCreationForm  # Ensure these forms are correctly implemented
from .models import (Allergy, AuthToken, EmergencyContact,
                      Medication, Patient, Practitioner, PractitionerSpecialization, User, Address)


class UserAdmin(admin.ModelAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    search_fields = ["first_name", "last_name", "phone_number", "email"]
    list_display = (
        "id",
        "phone_number",
        "email",
        "first_name",
        "last_name",
        "user_role",
        "gender",
        "is_accept_terms_and_condition",
        "is_active",
        "is_verified",
    )
    list_per_page = 100
    list_filter = ("user_role", "gender", "is_active", "date_joined")

class EmergencyContactAdmin(admin.ModelAdmin):
    search_fields = ["name", "phone_number"]
    list_display = ["id", "name", "phone_number"]

class AllergyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")

class AuthTokenAdmin(admin.ModelAdmin):
    search_fields = ["user__first_name", "user__last_name", "token"]
    list_display = ("user", "id", "token", "status", "expiry")

class MedicationAdmin(admin.ModelAdmin):
    list_display = ("name", "id")
    search_fields = ("name",)

class PatientAdmin(admin.ModelAdmin):
    list_display = ("user", "blood_group", "genotype", "emergency_contact", "nationality")
    search_fields = ("user__first_name", "user__last_name", "nationality")
    list_filter = ("blood_group", "genotype")

class AddressAdmin(admin.ModelAdmin):
    list_display = (
        "address",
        "zip_code",
        "country",
        "city",
        "state",   
        "town",   
    )

class PractitionerSpecializationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "id"
    )

class PractitionerAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "license_number",
        "means_of_identification_type",
        "means_of_identification",
        "certificate",
        "updated_at",
    )
    search_fields = ("user__first_name", "user__last_name", "license_number")
  



admin.site.register(User, UserAdmin)
admin.site.register(EmergencyContact, EmergencyContactAdmin)
admin.site.register(AuthToken, AuthTokenAdmin)
admin.site.register(Allergy, AllergyAdmin)
admin.site.register(Medication, MedicationAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(PractitionerSpecialization, PractitionerSpecializationAdmin)
admin.site.register(Practitioner, PractitionerAdmin)
