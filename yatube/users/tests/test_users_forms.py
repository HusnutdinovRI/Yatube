from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import User


User = get_user_model()


class UserFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='admin')

    def setUp(self):
        # Создаем авторизованый клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_sign_up(self):
        """Проверяем создание пользователя"""
        # Подсчитаем количество записей в Task
        user_count = User.objects.count()
        # Подготавливаем данные для передачи в форму
        form_data = {
            'first_name': 'Вася',
            'last_name': 'Пупкин',
            'username': 'megadestroyer2000',
            'email': 'megadestroyer2000@yandex.ru',
            'password1': '1Qazwsxedc#$',
            'password2': '1Qazwsxedc#$'

        }
        response = self.authorized_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response, reverse('posts:index'))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(User.objects.count(), user_count + 1)
