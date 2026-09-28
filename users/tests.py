from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


class UserApiTests(APITestCase):
    def test_registration_is_public(self):
        response = self.client.post(
            "/api/users/",
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "StrongPass123!",
                "first_name": "New",
                "last_name": "User",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            User.objects.filter(username="newuser").exists()
        )

    def test_users_endpoint_is_admin_only(self):
        user = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="StrongPass123!",
        )
        self.client.force_authenticate(user)

        response = self.client.get("/api/users/")

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_login_uses_email(self):
        User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="StrongPass123!",
        )

        response = self.client.post(
            "/api/users/login/",
            {
                "email": "USER1@EXAMPLE.COM",
                "password": "StrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
