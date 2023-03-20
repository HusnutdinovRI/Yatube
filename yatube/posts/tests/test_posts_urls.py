from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.core.cache import cache
from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user = User.objects.create_user(username='auth2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст ' + '01' * 50,
        )

    def setUp(self):

        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_urls_exists_at_desired_location_guest(self):
        """Проверяем доступность страниц"""
        url_names_guest = {
            '/': HTTPStatus.OK,
            '/group/test-slug/': HTTPStatus.OK,
            '/profile/auth/': HTTPStatus.OK,
            '/posts/1/': HTTPStatus.OK,
            '/posts/<int:post_id>/comment/': HTTPStatus.NOT_FOUND,
        }

        """Проверяем доступность страниц
           неавторизованному клиенту"""
        for url, status in url_names_guest.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_urls_exists_at_desired_location_auth_user(self):

        url_names_authorized_client = {
            '/posts/1/edit/': HTTPStatus.OK,
            '/create/': HTTPStatus.OK,
            '/unexesting_page/': HTTPStatus.NOT_FOUND
        }
        user = User.objects.create_user(username='Romario')
        authorized_client = Client()
        authorized_client.force_login(user)

        """Проверяем доступность страниц
           авторизованному клиенту"""
        for url, status in url_names_authorized_client.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_edit_url_exists_at_desired_location(self):
        """Страница /post/edit доступна автору поста."""
        user = User.objects.create_user(username='Romario')
        authorized_client = Client()
        authorized_client.force_login(user)
        response = authorized_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(template)
                self.assertTemplateUsed(response, url)
