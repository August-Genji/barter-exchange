from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, AdViewSet, ExchangeProposalViewSet,
    AdListView, AdDetailView, AdCreateView, AdUpdateView, AdDeleteView
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'ads', AdViewSet, basename='ad')
router.register(r'proposals', ExchangeProposalViewSet, basename='proposal')

html_urlpatterns = [
    path('', AdListView.as_view(), name='ad_list'),
    path('ad/<int:pk>/', AdDetailView.as_view(), name='ad_detail'),
    path('ad/create/', AdCreateView.as_view(), name='ad_create'),
    path('ad/<int:pk>/edit/', AdUpdateView.as_view(), name='ad_edit'),
    path('ad/<int:pk>/delete/', AdDeleteView.as_view(), name='ad_delete'),
]

urlpatterns = [
    path('api/', include(router.urls)),
    *html_urlpatterns
]
