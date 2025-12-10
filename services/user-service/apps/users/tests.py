from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


class UserModelTest(TestCase):
    """Тесты модели User"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_user_creation(self):
        """Тест создания пользователя"""
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(self.user.check_password('testpass123'))
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')

    def test_user_str(self):
        """Тест строкового представления - использует email"""
        self.assertEqual(str(self.user), 'test@example.com')

    def test_user_email_unique(self):
        """Тест уникальности email"""
        with self.assertRaises(Exception):
            User.objects.create_user(
                email='test@example.com',
                username='anotheruser',
                password='pass123'
            )


class UserProfileModelTest(TestCase):
    """Тесты модели UserProfile"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            phone='+1234567890',
            address='123 Test St'
        )

    def test_profile_creation(self):
        """Тест создания профиля"""
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.phone, '+1234567890')
        self.assertEqual(self.profile.address, '123 Test St')

    def test_profile_str(self):
        """Тест строкового представления профиля"""
        self.assertEqual(str(self.profile), f"Profile of {self.user.email}")

