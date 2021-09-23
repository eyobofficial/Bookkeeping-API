"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from shared.schema import CustomOpenAPISchemaGenerator


schema_view = get_schema_view(
   openapi.Info(
      title="Dukka API",
      default_version='v1.0.0',
      description=('RESTful API endpoints for Dukka MVP version 1.0 app.'),
      contact=openapi.Contact(email="hello@dukka.com")
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
   generator_class=CustomOpenAPISchemaGenerator
)


# Schema URLS
urlpatterns = [
    path('', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    url(r'^swagger.json/$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]


urlpatterns += [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('business/', include('business.urls', namespace='business')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('', include('shared.urls', namespace='shared')),
]

# Media Assets
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Update Admin Site Title
admin.site.site_header = admin.site.site_title = settings.PROJECT_NAME
admin.site.enable_nav_sidebar = False
