import uuid
from decimal import Decimal
from unittest.mock import patch
from django.shortcuts import HttpResponse

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings

from .models import Order, OrderLineItem
from .forms import OrderForm
from products.models import Product
from profiles.models import UserProfile

class OrderModelTestCase(TestCase):
    def setUp(self):
        self.order = Order.objects.create(
            full_name="Test User",
            email="test@example.com",
            phone_number="1234567890",
            country="US",
            town_or_city="Test City",
            street_address1="123 Test St",
        )
        self.product = Product.objects.create(name="Test Product", price=Decimal('10.00'))

    def test_order_number_generation(self):
        self.assertIsNotNone(self.order.order_number)
        self.assertEqual(len(self.order.order_number), 32)

    def test_order_string_method(self):
        self.assertEqual(str(self.order), f"Order {self.order.order_number}")

    def test_order_total_calculation(self):
        OrderLineItem.objects.create(order=self.order, product=self.product, quantity=2)
        self.order.update_total()
        self.assertEqual(self.order.order_total, Decimal('20.00'))

    def test_grand_total_calculation(self):
        OrderLineItem.objects.create(order=self.order, product=self.product, quantity=2)
        self.order.update_total()
        expected_delivery = Decimal('20.00') * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
        expected_grand_total = Decimal('20.00') + expected_delivery
        self.assertEqual(self.order.grand_total, expected_grand_total)

class OrderFormTestCase(TestCase):
    def test_order_form_valid(self):
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
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        self.product = Product.objects.create(name="Test Product", price=Decimal('10.00'))

    @patch('checkout.views.stripe.PaymentIntent.create')
    def test_get_checkout_page(self, mock_payment_intent):
        mock_payment_intent.return_value = {'client_secret': 'test_secret'}
        session = self.client.session
        session['bag'] = {str(self.product.id): 1}
        session.save()
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'checkout/checkout.html')

    @patch('checkout.views.stripe.PaymentIntent.create')
    def test_post_checkout_page_valid(self, mock_payment_intent):
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
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.product = Product.objects.create(name="Test Product", price=Decimal('10.00'))

    @patch('checkout.views.stripe.PaymentIntent.create')
    def test_checkout_saves_to_profile(self, mock_payment_intent):
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
    def setUp(self):
        self.order = Order.objects.create(
            full_name="Test User",
            email="test@example.com",
            phone_number="1234567890",
            country="US",
            town_or_city="Test City",
            street_address1="123 Test St",
        )
        self.product = Product.objects.create(name="Test Product", price=Decimal('10.00'))

    def test_update_on_save(self):
        OrderLineItem.objects.create(order=self.order, product=self.product, quantity=2)
        self.assertEqual(self.order.grand_total, Decimal('20.00') + (Decimal('20.00') * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)))

    def test_update_on_delete(self):
        line_item = OrderLineItem.objects.create(order=self.order, product=self.product, quantity=2)
        line_item.delete()
        self.assertEqual(self.order.grand_total, Decimal('0.00'))

class WebhookTestCase(TestCase):
    @patch('checkout.webhook_handler.StripeWH_Handler.handle_payment_intent_succeeded')
    @patch('stripe.Webhook.construct_event')
    def test_webhook_payment_intent_succeeded(self, mock_construct_event, mock_handler):
        mock_construct_event.return_value = {'type': 'payment_intent.succeeded'}
        mock_handler.return_value = HttpResponse(content='', status=200)

        response = self.client.post(reverse('webhook'), content_type='application/json', HTTP_STRIPE_SIGNATURE='test_signature')
        self.assertEqual(response.status_code, 200)
        mock_handler.assert_called_once()