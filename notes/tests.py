from django.test import TestCase
from django.urls import reverse

class SEOViewsTestCase(TestCase):
    def test_sitemap_view(self):
        response = self.client.get(reverse('sitemap'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/xml', response['Content-Type'])
        self.assertContains(response, '<loc>')
        self.assertContains(response, '/login/')
        self.assertContains(response, '/register/')

    def test_robots_txt_view(self):
        response = self.client.get(reverse('robots_txt'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain')
        self.assertIn('User-agent: *', response.content.decode('utf-8'))
        self.assertIn('Disallow: /dashboard/', response.content.decode('utf-8'))
        self.assertIn('sitemap.xml', response.content.decode('utf-8'))
