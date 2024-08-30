from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from .models import UserProfile
from .forms import UserProfileForm

class UserProfileModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.profile = self.user.userprofile

    def test_profile_creation(self):
        self.assertIsInstance(self.profile, UserProfile)
        self.assertEqual(str(self.profile), 'testuser')

    def test_profile_update(self):
        self.profile.default_phone_number = '1234567890'
        self.profile.save()
        self.assertEqual(self.profile.default_phone_number, '1234567890')

class UserProfileFormTestCase(TestCase):
    def test_form_valid(self):
        form_data = {
            'default_phone_number': '1234567890',
            'default_street_address1': '123 Test St',
            'default_town_or_city': 'Test City',
            'default_postcode': '12345',
            'default_country': 'US',
        }
        form = UserProfileForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid(self):
        form_data = {
            'default_phone_number': 'invalid_phone',
        }
        form = UserProfileForm(data=form_data)
        self.assertFalse(form.is_valid())

class ProfileViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_profile_view_get(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/profile.html')

    def test_profile_view_post(self):
        post_data = {
            'default_phone_number': '1234567890',
            'default_street_address1': '123 Test St',
            'default_town_or_city': 'Test City',
            'default_postcode': '12345',
            'default_country': 'US',
        }
        response = self.client.post(reverse('profile'), data=post_data)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Profile updated successfully')

class OrderHistoryViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_order_history_view(self):
        response = self.client.get(reverse('order_history'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/order_history.html')

class SignalTestCase(TestCase):
    def test_profile_creation_signal(self):
        user = User.objects.create_user(username='newuser', password='12345')
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_profile_update_signal(self):
        user = User.objects.create_user(username='updateuser', password='12345')
        user.first_name = 'Updated'
        user.save()
        profile = UserProfile.objects.get(user=user)
        self.assertTrue(profile)  # Just checking if the profile still exists after user update