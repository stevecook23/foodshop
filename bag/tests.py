"""Tests for the bag app views and context processors."""
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from django.conf import settings
from products.models import Product


class BagViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.product = Product.objects.create(
            name='Test Product',
            price=Decimal('10.00')
        )

    def test_view_bag(self):
        response = self.client.get(reverse('view_bag'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bag/bag.html')

    def test_add_to_bag(self):
        response = self.client.post(reverse('add_to_bag', args=[self.product.id]), {
            'quantity': 1,
            'redirect_url': reverse('view_bag')
        })
        self.assertRedirects(response, reverse('view_bag'))
        self.assertEqual(self.client.session['bag'], {str(self.product.id): 1})

    def test_adjust_bag(self):
        # First, add an item to the bag
        self.client.post(reverse('add_to_bag', args=[self.product.id]), {
            'quantity': 2,
            'redirect_url': reverse('view_bag')
        })

        # Now adjust the quantity
        response = self.client.post(reverse('adjust_bag', args=[self.product.id]), {
            'quantity': 1
        })
        self.assertRedirects(response, reverse('view_bag'))
        self.assertEqual(self.client.session['bag'], {str(self.product.id): 1})

    def test_remove_from_bag(self):
        # First, add an item to the bag
        self.client.post(reverse('add_to_bag', args=[self.product.id]), {
            'quantity': 1,
            'redirect_url': reverse('view_bag')
        })

        # Now remove the item
        response = self.client.post(reverse('remove_from_bag', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session['bag'], {})


class BagContextProcessorTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.product = Product.objects.create(
            name='Test Product',
            price=Decimal('10.00')
        )

    def test_bag_contents(self):
        # Add an item to the bag
        self.client.post(reverse('add_to_bag', args=[self.product.id]), {
            'quantity': 2,
            'redirect_url': reverse('view_bag')
        })

        # Get the bag page
        response = self.client.get(reverse('view_bag'))

        # Check the context
        self.assertEqual(response.context['total'], Decimal('20.00'))
        self.assertEqual(response.context['product_count'], 2)
        self.assertEqual(len(response.context['bag_items']), 1)

        # Check delivery calculations
        if Decimal('20.00') < settings.FREE_DELIVERY_THRESHOLD:
            expected_delivery = (Decimal('20.00') * 
                                Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100))
            expected_free_delivery_delta = (settings.FREE_DELIVERY_THRESHOLD - 
                                            Decimal('20.00'))
        else:
            expected_delivery = Decimal('0.00')
            expected_free_delivery_delta = Decimal('0.00')

        self.assertEqual(response.context['delivery'], expected_delivery)
        self.assertEqual(response.context['free_delivery_delta'],
                         expected_free_delivery_delta)
        self.assertEqual(response.context['free_delivery_threshold'],
                         settings.FREE_DELIVERY_THRESHOLD)
        self.assertEqual(response.context['grand_total'],
                         Decimal('20.00') + expected_delivery)
