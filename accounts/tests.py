from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import UserProfile

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testanalyst',
            email='analyst@scamshield.org',
            password='SecurePassword123!',
            first_name='Alex',
            last_name='Vance'
        )

    def test_user_profile_signal_creation(self):
        """Test that UserProfile is automatically created when User is created."""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertEqual(self.user.profile.role, 'Security Analyst')

    def test_login_successful(self):
        """Test valid user login."""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testanalyst',
            'password': 'SecurePassword123!'
        }, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertEqual(response.context['user'].username, 'testanalyst')

    def test_login_invalid_credentials(self):
        """Test invalid credentials rejection."""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testanalyst',
            'password': 'WrongPassword999'
        })
        self.assertFalse(response.context['user'].is_authenticated)

    def test_protected_dashboard_redirects_anonymous(self):
        """Anonymous user trying to access /dashboard/ should be redirected to login."""
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)

    def test_protected_dashboard_accessible_when_authenticated(self):
        """Logged-in user can access /dashboard/."""
        self.client.login(username='testanalyst', password='SecurePassword123!')
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Security Operations Center')
