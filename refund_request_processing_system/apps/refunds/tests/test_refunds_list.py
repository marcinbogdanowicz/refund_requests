from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.refunds.models import RefundRequest


class RefundRequestListViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username="user1", password="pass123")
        cls.user2 = User.objects.create_user(username="user2", password="pass123")
        cls.list_url = reverse("refund_list")
        cls.login_url = reverse("login")

        cls.user1_refund_requests = []
        for i in range(3):
            cls.user1_refund_requests.append(
                RefundRequest.objects.create(
                    user=cls.user1,
                    order_number=f"ORD{i}",
                    order_date="2024-03-10",
                    products=f"Product {i}",
                    reason=f"Reason {i}",
                    status="pending",
                )
            )

        RefundRequest.objects.create(
            user=cls.user2,
            order_number="ORD-U2",
            order_date="2024-03-10",
            products="Product U2",
            reason="Reason U2",
            status="pending",
        )

    def test_login_required(self):
        response = self.client.get(self.list_url)
        expected_url = f"{self.login_url}?next={self.list_url}"
        self.assertRedirects(response, expected_url)

    def test_refund_list_page(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.list_url)
        self.assertTemplateUsed(response, "refunds/list.html")

    @patch("apps.refunds.views.RefundRequestListView.paginate_by", 2)
    def test_pagination(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["refund_requests"]), 2)
        self.assertEqual(response.context["paginator"].num_pages, 2)

        response = self.client.get(f"{self.list_url}?page=2")

        self.assertEqual(len(response.context["refund_requests"]), 1)
        self.assertEqual(response.context["page_obj"].number, 2)

    def test_ordering(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        refund_requests = response.context["refund_requests"]
        self.assertListEqual(
            list(refund_requests), list(reversed(self.user1_refund_requests))
        )

    def test_user_can_only_see_their_own_requests(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        refund_requests = response.context["refund_requests"]
        self.assertEqual(len(refund_requests), 3)
        for request in refund_requests:
            self.assertEqual(request.user, self.user1)

    def test_empty_list_message(self):
        empty_user = User.objects.create_user(username="empty_user", password="pass123")
        self.client.force_login(empty_user)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No refund requests yet.")
