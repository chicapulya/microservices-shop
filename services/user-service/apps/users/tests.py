from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import UserProfile

User = get_user_model()


class UserModelTest(TestCase):
    """Test User model"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_user_creation(self):
        """Test creating a user"""
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(self.user.check_password('testpass123'))

    def test_user_str(self):
        """Test user string representation"""
        self.assertEqual(str(self.user), 'testuser')


class UserProfileModelTest(TestCase):
    """Test UserProfile model"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            phone='+1234567890',
            address='123 Test St'
        )

    def test_profile_creation(self):
        """Test creating a user profile"""
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.phone, '+1234567890')

    def test_profile_str(self):
        """Test profile string representation"""
        self.assertEqual(str(self.profile), f"Profile of {self.user.email}")


class UserAPITest(APITestCase):
    """Test User API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_user_list_unauthenticated(self):
        """Test that unauthenticated users cannot list users"""
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_registration(self):
        """Test user registration"""
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)

    def test_user_login(self):
        """Test user login"""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post('/api/auth/login/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post('/api/auth/login/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

