from django.urls import path
from .views import (
    AdListView, AdDetailView,
    AdCreateView, AdUpdateView, AdDeleteView, CreateExchangeProposalView, MyExchangeProposalsView, accept_proposal,
    decline_proposal
)
from django.contrib.auth import views
from .views import register

urlpatterns = [
    path('', AdListView.as_view(), name='ad_list'),
    path('ad/<int:pk>/', AdDetailView.as_view(), name='ad_detail'),
    path('ad/create/', AdCreateView.as_view(), name='ad_create'),
    path('ad/<int:pk>/edit/', AdUpdateView.as_view(), name='ad_edit'),
    path('ad/<int:pk>/delete/', AdDeleteView.as_view(), name='ad_delete'),
    path('ad/<int:ad_id>/propose/', CreateExchangeProposalView.as_view(), name='create_proposal'),
    path('my-proposals/', MyExchangeProposalsView.as_view(), name='my_proposals'),
    path('proposals/<int:pk>/accept/', accept_proposal, name='accept_proposal'),
    path('proposals/<int:pk>/decline/', decline_proposal, name='decline_proposal'),
]

urlpatterns += [
    path('login/', views.LoginView.as_view(template_name='ads/login.html'), name='login'),
    path('logout/', views.LogoutView.as_view(next_page='ad_list'), name='logout'),
    path('register/', register, name='register'),
]