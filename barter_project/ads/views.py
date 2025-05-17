from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from django.contrib.auth.models import User
from .models import Ad, ExchangeProposal
from .serializer import AdSerializer, UserSerializer, ExchangeProposalSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .permissions import IsOwnerOrReadOnly, IsSenderOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.exceptions import PermissionDenied


class UserViewSet(ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class AdViewSet(ModelViewSet):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'condition']
    search_fields = ['title', 'description']

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        if response.data['count'] == 0:
            response.data['message'] = 'По вашему запросы ничего не найдено ('
        return response

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ExchangeProposalViewSet(ModelViewSet):
    queryset = ExchangeProposal.objects.all()
    serializer_class = ExchangeProposalSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsSenderOrReadOnly]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'ad_sender', 'ad_receiver']
    search_fields = ['comment']

    def perform_create(self, serializer):
        ad_sender = serializer.validated_data['ad_sender']
        if ad_sender.user != self.request.user:
            raise PermissionDenied("Вы можете отправлять предложения только от своих объявлений")
        serializer.save()