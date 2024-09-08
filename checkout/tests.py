"""This module contains tests for the checkout application."""
from decimal import Decimal
from unittest.mock import patch
from django.shortcuts import HttpResponse

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings

from profiles.models import UserProfile
from products.models import Product
from .forms import OrderForm
from .models import Order, OrderLineItem


class OrderModelTestCase(TestCase):
    """Test case for the Order model."""

    def setUp(self):
        """Set up test data for Order model tests."""
        self.order = Order.objects.create(
            full_name="Test User",
            email="test@example.com",
            phone_number="1234567890",
            country="US",
            town_or_city="Test City",
            street_address1="123 Test St",
        )
        self.product = Product.objects.create(
            name="Test Product",
            price=Decimal('10.00')
        )

    def test_order_number_generation(self):
        """Test that order numbers are generated correctly."""
        self.assertIsNotNone(self.order.order_number)
        self.assertEqual(len(self.order.order_number), 32)

    def test_order_string_method(self):
        """Test the string representation of the Order model."""
        self.assertEqual(
            str(self.order),
            f"Order {self.order.order_number}"
        )

    def test_order_total_calculation(self):
        """Test the calculation of order total."""
        OrderLineItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2
        )
        self.order.update_total()
        self.assertEqual(self.order.order_total, Decimal('20.00'))

    def test_grand_total_calculation(self):
        """Test the calculation of grand total including delivery."""
        OrderLineItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2
        )
        self.order.update_total()
        expected_delivery = (Decimal('20.00') *
                             Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100))
        expected_grand_total = Decimal('20.00') + expected_delivery
        self.assertEqual(self.order.grand_total, expected_grand_total)


class OrderFormTestCase(TestCase):
    """Test case for the Order form."""

    def test_order_form_valid(self):
        """Test that the order form is valid with correct data."""
        form_data = {
            'full_name': 'Test User',
            'email': 'test@example.com',
            'phone_number': '1234567890',
            'country': 'US',
            'town_or_city': 'Test City',
            'street_address1': '123 Test St',
            'street_address2': '',
            'postcode': '12345',
            'county': '',
        }
        form = OrderForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_order_form_invalid(self):
        """Test that the order form is invalid with incorrect data."""
        form_data = {
            'full_name': '',
            'email': 'invalid_email',
            'phone_number': '1234567890',
            'country': 'US',
            'town_or_city': 'Test City',
            'street_address1': '123 Test St',
        }
        form = OrderForm(data=form_data)
        self.assertFalse(form.is_valid())


class CheckoutViewTestCase(TestCase):
    """Test case for the checkout view."""

    def setUp(self):
        """Set up test data for checkout view tests."""
        self.client = Client()
        self.user = User.objects.create_user(
            'testuser', 'test@example.com', 'testpassword'
        )
        self.product = Product.objects.create(
            name="Test Product",
            price=Decimal('10.00')
        )

    @patch('checkout.views.stripe.PaymentIntent.create')
    def test_get_checkout_page(self, mock_payment_intent):
        """Test GET request to checkout page."""
        mock_payment_intent.return_value = {'client_secret': 'test_secret'}
        session = self.client.session
        session['bag'] = {str(self.product.id): 1}
        session.save()
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'checkout/checkout.html')

    @patch('checkout.views.stripe.PaymentIntent.create')
    def test_post_checkout_page_valid(self, mock_payment_intent):
        """Test POST request to checkout page with valid data."""
        mock_payment_intent.return_value = {'client_secret': 'test_secret'}
        session = self.client.session
        session['bag'] = {str(self.product.id): 1}
        session.save()
        form_data = {
            'full_name': 'Test User',
            'email': 'test@example.com',
            'phone_number': '1234567890',
            'country': 'US',
            'town_or_city': 'Test City',
            'street_address1': '123 Test St',
            'client_secret': 'test_secret',
        }
        response = self.client.post(reverse('checkout'), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Order.objects.exists())
        

class CheckoutProfileIntegrationTestCase(TestCase):
    """Test case for checkout and profile integration."""

    def setUp(self):
        """Set up test data for checkout and profile integration tests."""
        self.client = Client()
        self.user = User.objects.create_user(
            'testuser', 'test@example.com', 'testpassword'
        )
        self.client.login(username='testuser', password='testpassword')
        self.product = Product.objects.create(
            name="Test Product",
            price=Decimal('10.00')
        )

    @patch('checkout.views.stripe.PaymentIntent.create')
    def test_checkout_saves_to_profile(self, mock_payment_intent):
        """Test that checkout information is saved to user profile."""
        mock_payment_intent.return_value = {'client_secret': 'test_secret'}
        session = self.client.session
        session['bag'] = {str(self.product.id): 1}
        session.save()
        form_data = {
            'full_name': 'Test User',
            'email': 'test@example.com',
            'phone_number': '1234567890',
            'country': 'US',
            'town_or_city': 'Test City',
            'street_address1': '123 Test St',
            'client_secret': 'test_secret',
            'save_info': True,
        }
        response = self.client.post(reverse('checkout'), data=form_data)
        self.assertEqual(response.status_code, 302)
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.default_phone_number, '1234567890')
        self.assertEqual(profile.default_town_or_city, 'Test City')
        self.assertEqual(profile.default_street_address1, '123 Test St')

    def test_checkout_uses_profile_info(self):
        """Test that checkout pre-fills with profile information."""
        profile = self.user.userprofile
        profile.default_phone_number = '0987654321'
        profile.default_country = 'US'
        profile.default_town_or_city = 'Profile City'
        profile.default_street_address1 = '456 Profile St'
        profile.save()

        session = self.client.session
        session['bag'] = {str(self.product.id): 1}
        session.save()

        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '0987654321')
        self.assertContains(response, 'Profile City')
        self.assertContains(response, '456 Profile St')


class SignalsTestCase(TestCase):
    """Test case for model signals."""

    def setUp(self):
        """Set up test data for signal tests."""
        self.order = Order.objects.create(
            full_name="Test User",
            email="test@example.com",
            phone_number="1234567890",
            country="US",
            town_or_city="Test City",
            street_address1="123 Test St",
        )
        self.product = Product.objects.create(
            name="Test Product",
            price=Decimal('10.00')
        )

    def test_update_on_save(self):
        """Test that order total updates on save."""
        OrderLineItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2
        )
        expected_total = (
            Decimal('20.00') +
            (Decimal('20.00') * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100))
        )
        self.assertEqual(self.order.grand_total, expected_total)

    def test_update_on_delete(self):
        """Test that order total updates on delete."""
        line_item = OrderLineItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2
        )
        line_item.delete()
        self.assertEqual(self.order.grand_total, Decimal('0.00'))


class WebhookTestCase(TestCase):
    """Test case for webhook handling."""

    @patch('checkout.webhook_handler.StripeWH_Handler.handle_payment_intent_succeeded')
    @patch('stripe.Webhook.construct_event')
    def test_webhook_payment_intent_succeeded(self, mock_construct_event, mock_handler):
        """Test handling of successful payment intent webhook."""
        mock_construct_event.return_value = {'type': 'payment_intent.succeeded'}
        mock_handler.return_value = HttpResponse(content='', status=200)

        response = self.client.post(
            reverse('webhook'),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_signature'
        )
        self.assertEqual(response.status_code, 200)
        mock_handler.assert_called_once()
