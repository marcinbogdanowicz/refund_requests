from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.refunds.models import RefundRequest


class RefundRequestDetailViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            username='user1', password='pass123'
        )
        cls.user2 = User.objects.create_user(
            username='user2', password='pass123'
        )

        cls.refund = RefundRequest.objects.create(
            user=cls.user1,
            order_number='ORD123',
            order_date='2024-03-10',
            products='Test Product\nLine 2',
            reason='Test Reason\nLine 2',
            status='pending',
            address='Test Street 123',
            postal_code='12345',
            city='Test City',
            country='Test Country',
            iban='DE89370400440532013000',
            iban_verified=True,
            bank_name='Test Bank',
            account_type='personal',
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone_number='+48123456789',
        )

        cls.detail_url = reverse('refund_detail', kwargs={'pk': cls.refund.pk})
        cls.login_url = reverse('login')

    def test_login_required(self):
        response = self.client.get(self.detail_url)
        expected_url = f'{self.login_url}?next={self.detail_url}'
        self.assertRedirects(response, expected_url)

    def test_only_owner_can_view_refund(self):
        self.client.login(username='user1', password='pass123')
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'refunds/detail.html')

        self.client.login(username='user2', password='pass123')
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 404)

    def test_detail_page_shows_correct_data(self):
        self.client.login(username='user1', password='pass123')
        response = self.client.get(self.detail_url)

        self.assertContains(response, f'Refund request no. {self.refund.id}')
        self.assertContains(response, 'ORD123')
        self.assertContains(response, '10/03/2024')
        self.assertContains(response, 'Test Product<br>Line 2')
        self.assertContains(response, 'Test Reason<br>Line 2')
        self.assertContains(response, 'Pending')
        self.assertContains(response, 'Test Street 123')
        self.assertContains(response, '12345')
        self.assertContains(response, 'Test City')
        self.assertContains(response, 'Test Country')
        self.assertContains(response, 'DE89370400440532013000')
        self.assertContains(response, 'Test Bank')
        self.assertContains(response, 'Personal')
        self.assertContains(response, 'John')
        self.assertContains(response, 'Doe')
        self.assertContains(response, 'john@example.com')
        self.assertContains(response, '+48123456789')

    def test_back_to_list_link_provided(self):
        self.client.login(username='user1', password='pass123')
        response = self.client.get(self.detail_url)

        self.assertContains(response, 'Back to list')
        self.assertContains(response, reverse('refund_list'))
