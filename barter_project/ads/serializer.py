from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Ad, ExchangeProposal


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class AdSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)

    class Meta:
        model = Ad
        fields = ['id', 'title', 'description', 'image_url', 'category', 'condition', 'created_at', 'user']


class ExchangeProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeProposal
        fields = ['id', 'ad_sender', 'ad_receiver', 'comment', 'status', 'created_at']
        depth = 1
