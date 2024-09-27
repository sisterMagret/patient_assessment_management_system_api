# from email.headerregistry import Address
# from django.contrib import admin

# from .forms import CustomUserChangeForm, CustomUserCreationForm
# from .models import (Allergy, AuthToken,  EmergencyContact,
#                       Medication, Patient, Practitioner, PractitionerSpecialization, User)



# class UserAdmin(admin.ModelAdmin):
#     add_form = CustomUserCreationForm
#     form = CustomUserChangeForm
#     search_fields = ["first_name", "last_name", "phone_number", "email"]
#     list_display = (
#         "id",
#         "phone_number",
#         "email",
#         "first_name",
#         "last_name",
#         "user_role",
#         "gender",
#         "is_accept_terms_and_condition",
#     )
#     list_per_page = 100


# class EmergencyContactAdmin(admin.ModelAdmin):
#     search_fields = ["name",  "phone_number"]
#     list_display = ["id", "name",  "phone_number"]


# class AllergyAdmin(admin.ModelAdmin):
#     list_display = ("id", "name", "description")


# class AuthTokenAdmin(admin.ModelAdmin):
#     search_fields = ["user__first_name", "user__last_name"]
#     list_display = ("user", "id", "token", "status", "expiry")


# class MedicationAmin(admin.ModelAdmin):
#     list_display = ("name", "id")
#     filter_fields = ("name",)


# class PatientAdmin(admin.ModelAdmin):
#     list_display = ("blood_group", "genotype", "emergency_contact", "nationality")
#     filter_fields = ("blood_group", "genotype", "nationality")


# class AddressAdmin(admin.ModelAdmin):
#     list_display = (
#         "address",
#         "zip_code",
#         "country",
#         "city",
#         "state",   
#         "town",   
#     )


# class PractitionerSpecializationAdmin(admin.ModelAdmin):
#     list_display = (
#         "name",
#         "description",
#         "id"
#     )


# class PractitionerAdmin(admin.ModelAdmin):
#     list_display = (
#         "license_number",
#         "means_of_identification_type",
#         "means_of_identification",
#         "certificate",
#         "updated_at",
#         "is_verified",
#     )


   
# admin.site.register(User, UserAdmin)
# admin.site.register(EmergencyContact, EmergencyContactAdmin)
# admin.site.register(AuthToken, AuthTokenAdmin)
# admin.site.register(Allergy, AllergyAdmin)
# admin.site.register(Medication, MedicationAmin)
# admin.site.register(Patient, PatientAdmin)
# # admin.site.register(Address, AddressAdmin)
# admin.site.register(PractitionerSpecialization, PractitionerSpecializationAdmin)
# admin.site.register(Practitioner, PractitionerAdmin)
