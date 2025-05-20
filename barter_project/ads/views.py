from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models.functions import Lower
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import filters
from rest_framework import status
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from django.db.models import Q

from .serializer import AdSerializer, UserSerializer, ExchangeProposalSerializer
from .models import Ad, ExchangeProposal
from .permissions import IsOwnerOrReadOnly, IsSenderOrReadOnly
from .forms import ExchangeProposalForm


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


class AdListView(ListView):
    model = Ad
    template_name = 'ads/ad_list.html'
    context_object_name = 'ads'

    def get_queryset(self):
        queryset = Ad.objects.all().order_by('-created_at')
        q = self.request.GET.get('q')
        mine = self.request.GET.get('mine')

        if q:
            queryset = queryset.annotate(
                title_lower=Lower('title'),
                description_lower=Lower('description')  # 👈 с маленькой буквы

            ).filter(
                Q(title_lower__icontains=q.lower()) |
                Q(description_lower__icontains=q.lower())
            )

        if mine == '1' and self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)

        return queryset


class AdDetailView(DetailView):
    model = Ad
    template_name = 'ads/ad_detail.html'
    context_object_name = 'ad'


class AdCreateView(LoginRequiredMixin, CreateView):
    model = Ad
    fields = ['title', 'description', 'image_url', 'category', 'condition']
    template_name = 'ads/ad_form.html'
    success_url = reverse_lazy('ad_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class AdUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Ad
    fields = ['title', 'description', 'image_url', 'category', 'condition']
    template_name = 'ads/ad_form.html'
    success_url = reverse_lazy('ad_list')

    def test_func(self):
        ad = self.get_object()
        return self.request.user == ad.user


class AdDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Ad
    template_name = 'ads/ad_confirm_delete.html'
    success_url = reverse_lazy('ad_list')

    def test_func(self):
        ad = self.get_object()
        return self.request.user == ad.user


class CreateExchangeProposalView(LoginRequiredMixin, View):
    def get(self, request, ad_id):
        ad_receiver = get_object_or_404(Ad, id=ad_id)

        # нельзя предложить обмен на своё же объявление
        if ad_receiver.user == request.user:
            messages.error(request, "Нельзя предложить обмен на своё объявление.")
            return redirect('ad_detail', pk=ad_id)

        form = ExchangeProposalForm(user=request.user)
        return render(request, 'ads/create_proposal.html', {'form': form, 'ad_receiver': ad_receiver})

    def post(self, request, ad_id):
        ad_receiver = get_object_or_404(Ad, id=ad_id)
        form = ExchangeProposalForm(request.POST, user=request.user)

        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.ad_receiver = ad_receiver
            proposal.save()
            messages.success(request, "Предложение отправлено!")
            return redirect('ad_detail', pk=ad_id)

        return render(request, 'ads/create_proposal.html', {'form': form, 'ad_receiver': ad_receiver})


class MyExchangeProposalsView(View):
    def get(self, request):
        user_ads = Ad.objects.filter(user=request.user)
        proposals = ExchangeProposal.objects.filter(
            Q(ad_sender__in=user_ads) | Q(ad_receiver__in=user_ads)
        ).order_by('-created_at')

        return render(request, 'ads/my_proposals.html', {
            'proposals': proposals
        })


@require_POST
@login_required
def accept_proposal(request, pk):
    proposal = get_object_or_404(ExchangeProposal, pk=pk)
    if proposal.ad_receiver.user != request.user:
        return HttpResponseForbidden()
    proposal.status = 'accepted'
    proposal.save()
    return redirect('my_proposals')


@require_POST
@login_required
def decline_proposal(request, pk):
    proposal = get_object_or_404(ExchangeProposal, pk=pk)
    if proposal.ad_receiver.user != request.user:
        return HttpResponseForbidden()
    proposal.status = 'declined'
    proposal.save()
    return redirect('my_proposals')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('ad_list')
    else:
        form = UserCreationForm()
    return render(request, 'ads/login.html', {'form': form})
