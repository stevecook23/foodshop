from django.test import TestCase, Client
from django.urls import reverse, resolve
from home.views import home

class HomePageTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page_status_code(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_home_page_uses_correct_template(self):
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home/index.html')

    def test_home_page_contains_correct_html(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, '<html')
        self.assertContains(response, '</html>')

    def test_home_page_does_not_contain_incorrect_html(self):
        response = self.client.get(reverse('home'))
        self.assertNotContains(
            response, 'Hi there! I should not be on the page.')

class HomeUrlTests(TestCase):
    def test_home_url_resolves_home_view(self):
        view = resolve('/')
        self.assertEqual(view.func, home)