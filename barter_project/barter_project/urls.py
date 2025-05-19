from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView



urlpatterns = [
    path('', include('ads.html_urls')),
    path('admin/', admin.site.urls),
    path('api/', include('ads.api_urls')),

    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc-ui'),


]
