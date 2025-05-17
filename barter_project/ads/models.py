from django.db import models
from django.contrib.auth.models import User


class Ad(models.Model):
    CONDITION_CHOICES = [
        ('new', 'новый'),
        ('used', 'б/у')
    ]

    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=50)
    image_url = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=50)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ExchangeProposal(models.Model):
    STATUS_CHOICES = [
        ('pendidng', 'ожидает'),
        ('accepted', 'принят'),
        ('declined', 'отклонен')
    ]

    ad_sender = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='sent')
    ad_receiver = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='received')
    comment = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment
