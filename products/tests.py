"""Tests for the products app."""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Category, Product
from .forms import ProductForm


class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Test Category",
            friendly_name="Test Friendly Name"
        )

    def test_category_str(self):
        self.assertEqual(str(self.category), "Test Category")

    def test_get_friendly_name(self):
        self.assertEqual(
            self.category.get_friendly_name(),
            "Test Friendly Name"
        )


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            price=9.99,
            rating=4.5,
            sku="TEST123"
        )
        self.product.categories.add(self.category)

    def test_product_str(self):
        self.assertEqual(str(self.product), "Test Product")


class ProductFormTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Test Category",
            friendly_name="Test Friendly Name"
        )

    def test_product_form_valid(self):
        form_data = {
            'name': 'Test Product',
            'description': 'Test Description',
            'price': 9.99,
            'categories': [self.category.id],
        }
        form = ProductForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_product_form_invalid(self):
        form_data = {
            'name': '',  # Name is required
            'description': 'Test Description',
            'price': 9.99,
        }
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())


class ProductViewsTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            price=9.99,
            rating=4.5,
            sku="TEST123"
        )
        self.product.categories.add(self.category)
        self.user = User.objects.create_superuser(
            username='testadmin',
            password='testpass123',
            email='admin@example.com'
        )

    def test_all_products_view(self):
        response = self.client.get(reverse('products'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/products.html')
        self.assertContains(response, "Test Product")

    def test_product_detail_view(self):
        response = self.client.get(
            reverse('product_detail', args=[self.product.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_detail.html')
        self.assertContains(response, "Test Product")

    def test_add_product_view(self):
        self.client.login(username='testadmin', password='testpass123')
        response = self.client.get(reverse('add_product'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/add_product.html')

    def test_edit_product_view(self):
        self.client.login(username='testadmin', password='testpass123')
        response = self.client.get(
            reverse('edit_product', args=[self.product.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/edit_product.html')

    def test_delete_product_view(self):
        self.client.login(username='testadmin', password='testpass123')
        response = self.client.post(
            reverse('delete_product', args=[self.product.id])
        )
        self.assertRedirects(response, reverse('products'))
        self.assertFalse(
            Product.objects.filter(id=self.product.id).exists()
        )