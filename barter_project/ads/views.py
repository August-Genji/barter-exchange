from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import filters
from rest_framework import status
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models

from .serializer import AdSerializer, UserSerializer, ExchangeProposalSerializer
from .models import Ad, ExchangeProposal
from .permissions import IsOwnerOrReadOnly, IsSenderOrReadOnly


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


class ExchangeProposalViewSet(ModelViewSet):
    queryset = ExchangeProposal.objects.all()
    serializer_class = ExchangeProposalSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsSenderOrReadOnly]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'ad_sender', 'ad_receiver']
    search_fields = ['comment']

    def get_permissions(self):
        if self.action in ['accept', 'decline', 'my_proposals']:
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(detail=False, methods=['get'], url_path='my')
    def my_proposals(self, request):
        user = request.user
        user_ads = Ad.objects.filter(user=user)
        proposals = ExchangeProposal.objects.filter(models.Q(ad_sender__in=user_ads) |
                                                    models.Q(ad_receiver__in=user_ads)).distinct()

        page = self.paginate_queryset(proposals)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(proposals, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        proposal = self.get_object()
        if proposal.ad_receiver.user != request.user:
            return Response({'detail': 'Вы не можете принят это предложение'}, status=status.HTTP_403_FORBIDDEN)

        proposal.status = 'accepted'
        proposal.save()
        return Response({'status': 'accepted'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        proposal = self.get_object()
        if proposal.ad_receiver.user != request.user:
            return Response({'detail': 'Вы не можете отклонить это предложение'}, status=status.HTTP_403_FORBIDDEN)

        proposal.status = 'declined'
        proposal.save()
        return Response({'status': 'declined'}, status=status.HTTP_200_OK)
