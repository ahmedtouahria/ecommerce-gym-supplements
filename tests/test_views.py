import subprocess
from django.urls import reverse
from django.test import TestCase , Client

'''=============== Testing views ==============='''
class TestViews(TestCase):
    def setUp(self) :
        self.client=Client()
        self.index_url=reverse('index')
        self.products_url=reverse('products')
    def test_index_GET(self):
        client= Client()
        response = client.get(self.index_url)
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,"pages/home.html")
    def test_products_GET(self):
        client= Client()
        response = client.get(self.products_url)
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,"pages/products.html")
