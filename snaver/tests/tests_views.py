from django.test import TestCase

from django.test import Client


class CategoryView(TestCase):
    def test_category_page_returns_200(self):
        c = Client()
        response = c.get('/category/')
        self.assertEqual(response.status_code, 200)
