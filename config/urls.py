from pathlib import Path

from decouple import config as env_loc
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenRefreshView


from apps.users import routes as account_route
from apps.assessment import routes as assessment_route
from config import  settings

schema_view = get_schema_view(
    openapi.Info(
        title="PMS FEAT API",
        default_version="v1",
        description=Path("docs/pms_doc.md").read_text(encoding="utf8"),
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@farmfeat.com"),
        license=openapi.License(name="BSD License"),
        url=f"{env_loc('BASE_BE_URL')}",
    ),
    public=True,
    authentication_classes=(SessionAuthentication, JWTAuthentication),
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("api/v1/identity/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/", include(account_route.router.urls)),
    path("api/v1/", include(assessment_route.router.urls)),
    path(
        "",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

