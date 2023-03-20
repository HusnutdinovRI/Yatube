from django.contrib.auth import get_user_model
from django.test import TestCase, Client

User = get_user_model()


class PostURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self):
        self.guest_client = Client()

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        response = self.guest_client.get('/unexesting_page/')
        self.assertTemplateUsed(response, 'core/404.html')
