from django.test import Client
from django.test import TestCase


class CategoryView(TestCase):
    def test_category_page_returns_200(self):
        c = Client()
        response = c.get('/category/')
        self.assertEqual(response.status_code, 200)
