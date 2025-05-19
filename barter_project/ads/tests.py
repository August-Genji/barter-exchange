from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Ad, ExchangeProposal


class BarterTests(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='batman', password='1234')
        self.user2 = User.objects.create_user(username='genji', password='5678')

        self.ad1 = Ad.objects.create(
            user=self.user1,
            title="Футболка",
            description="Черная, M",
            category="одежда",
            condition="used"
        )

        self.ad2 = Ad.objects.create(
            user=self.user2,
            title="Книга",
            description="Фантастика",
            category="книги",
            condition="new"
        )

    def authenticate(self, user):
        response = self.client.post('/auth/jwt/create/', {
            'username': user.username,
            'password': '1234' if user == self.user1 else '5678'
        })
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_create_ad(self):
        self.authenticate(self.user1)
        response = self.client.post('/api/ads/', {
            'title': "Кроссовки",
            'description': "Salomon Sense Ride 5",
            'category': "обувь",
            'condition': "new"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_exchange_proposal_success(self):
        self.authenticate(self.user1)
        data = {
            'ad_sender_id': self.ad1.id,
            'ad_receiver_id': self.ad2.id,
            'comment': 'Обменяю стул на стол'
        }
        response = self.client.post('/api/proposals/', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExchangeProposal.objects.count(), 1)
        self.assertEqual(ExchangeProposal.objects.first().comment, 'Обменяю стул на стол')

    def test_create_exchange_proposal_fail_not_owner(self):
        self.authenticate(self.user2)
        response = self.client.post('/api/proposals/', {
            'ad_sender_id': self.ad1.id,
            'ad_receiver_id': self.ad2.id,
            'comment': "Попробую от чужого имени"
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_my_proposals(self):
        ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            comment="Обмен",
        )
        self.authenticate(self.user1)
        response = self.client.get('/api/proposals/my/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_decline_proposal_by_wrong_user(self):
        proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            comment="Хочу обмен"
        )

        self.authenticate(self.user1)
        url = f'/api/proposals/{proposal.id}/decline/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_accept_proposal_by_receiver(self):
        proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            comment="Обмен на книгу"
        )

        self.authenticate(self.user2)  # user2 — владелец ad2, он должен иметь право принять

        url = f'/api/proposals/{proposal.id}/accept/'
        response = self.client.post(url)

        proposal.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(proposal.status, 'accepted')

