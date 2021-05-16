from django.test import Client
from django.test import TestCase
from django.urls import reverse


class CategoryView(TestCase):
    def test_category_page_returns_200(self):
        c = Client()
        response = c.get(reverse('budget'))
        self.assertEqual(response.status_code, 200)
