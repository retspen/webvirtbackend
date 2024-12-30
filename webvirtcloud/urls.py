"""
WebVirtCloud URL Configuration
"""

from django.conf import settings
from django.urls import include, re_path
from django.views.decorators.cache import never_cache

from webvirtcloud.views import IndexView


urlpatterns = [
    re_path(r"api/", include("api.urls")),
    re_path(r"account/", include("account.urls")),
    re_path(r"metadata/", include("metadata.urls")),
    re_path(r"admin/", include("admin.urls")),
]

if settings.DEBUG:
    from drf_yasg import openapi
    from drf_yasg.views import get_schema_view
    from rest_framework.permissions import AllowAny

    schema_view = get_schema_view(
        openapi.Info(
            title="WebVirtCloud",
            default_version="v1",
            description="WebVirtCloud API documentation",
        ),
        public=True,
        permission_classes=(AllowAny,),
        patterns=[
            re_path(r"api/", include("api.urls")),
        ],
    )

    urlpatterns += [
        # Swagger
        re_path(r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
        re_path(r"^swagger/$", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
        re_path(r"^swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-yaml"),
        # Debug Toolbar
        re_path("__debug__/", include("debug_toolbar.urls")),
        re_path("__reload__/", include("django_browser_reload.urls")),
    ]

urlpatterns += [
    re_path(r"^$", never_cache(IndexView.as_view()), name="index"),
    re_path(r"^(?:.*)/?$", never_cache(IndexView.as_view()), name="index"),
]

handler403 = "webvirtcloud.views.app_exception_handler403"
handler404 = "webvirtcloud.views.app_exception_handler404"
handler500 = "webvirtcloud.views.app_exception_handler500"
