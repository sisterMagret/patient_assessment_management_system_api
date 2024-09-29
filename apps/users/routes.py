from rest_framework.routers import DefaultRouter

from apps.users.views import (
    PractitionerViewSet,
    PatientViewSet,
    UserViewSet,
    AuthViewSet,
)

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="api-user")
router.register(r"practitioners", PractitionerViewSet, basename="api-practitioner")
router.register(r"patients", PatientViewSet, basename="api-patient")
router.register(r"auth", AuthViewSet, basename="api-auth")
