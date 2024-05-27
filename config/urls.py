from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from metrics_category.views import MetricsCategoryView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny
from django.conf.urls.static import static
from django.conf import settings

# API documentation settings
schema_view = get_schema_view(
    openapi.Info(
        title="ERP API",
        default_version="v1",
        description="API для ERP",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[AllowAny],
)

# API routes
router = DefaultRouter()
router.register("metric-category", MetricsCategoryView, basename="metric-category")

# URL patterns
urlpatterns = [
    # Admin
    path("api/admin/", admin.site.urls),
    # Home page
    path("api/home_page/", include("home_page.urls")),
    # API paths
    path("api/account/", include("users.urls")),
    path("api/news/", include("news.urls")),
    path("api/profile/", include("profiles.urls")),
    # path("api/", include("metrics.urls")),
    path("api/", include("periods.urls")),
    path("api/", include("reports.urls")),
    path("api/", include("goals.urls")),
    # API documentation
    path(
        "api/swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "api/redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
