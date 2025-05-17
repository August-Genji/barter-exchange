from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.exceptions import PermissionDenied

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
        read_only_fields = ['user', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ExchangeProposalSerializer(serializers.ModelSerializer):
    ad_sender = AdSerializer(read_only=True)
    ad_sender_id = serializers.PrimaryKeyRelatedField(queryset=Ad.objects.all(), write_only=True, source='ad_sender')
    ad_receiver_id = serializers.PrimaryKeyRelatedField(queryset=Ad.objects.all(), write_only=True, source='ad_receiver')
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ExchangeProposal
        fields = ['id', 'ad_sender', 'ad_sender_id', 'ad_receiver_id',  'comment', 'status', 'created_at', 'status_display']
        read_only_fields = ['status', 'created_at']

    def validate_ad_sender_id(self, value):
        request = self.context['request']
        if value.user != request.user:
            raise PermissionDenied("Можно отправлять предложения только от своих объявлений")
        return value
