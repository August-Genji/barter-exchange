from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import UserViewSet, AdViewSet, ExchangeProposalViewSet



router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'ads', AdViewSet, basename='ad')
router.register(r'proposals', ExchangeProposalViewSet, basename='proposal')


urlpatterns = [
    path('', include(router.urls))
]