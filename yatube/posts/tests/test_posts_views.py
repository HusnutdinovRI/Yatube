import shutil
import tempfile
import unittest

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.cache import cache

from posts.forms import PostForm
from posts.models import Post, Group, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif')
        cls.user = User.objects.create_user(username='admin')
        cls.user2 = User.objects.create_user(username='admin2')
        cls.user3 = User.objects.create_user(username='admin3')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст ' + '01' * 50,
            group=cls.group,
            image=uploaded)
        cls.post2 = Post.objects.create(
            author=cls.user2,
            text='Текст ' + '01' * 50,
            group=cls.group,
            image=uploaded)
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Текст ' + '+' * 50,)
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):

        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client.force_login(self.user2)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            (reverse('posts:posts',
                     kwargs={'slug': 'test-slug'})): 'posts/group_list.html',
            (reverse('posts:profile',
                     kwargs={'username': 'admin'})): 'posts/profile.html',
            (reverse('posts:post_detail',
                     kwargs={'post_id': '2'})): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            (reverse('posts:post_edit',
                     kwargs={'post_id': '2'})): 'posts/create_post.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_context_in_index_page(self):
        """Удостоверимся, что на главую страницу передаётся список из постов"""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertIsInstance(response.context['page_obj'][0], Post)

    def test_cache_in_index_page(self):
        """Удостоверимся, что на главую страницу передаётся список из постов"""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertContains(response, self.post.text)
        Post.objects.all().delete()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertContains(response, self.post.text)
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotContains(response, self.post.text)

    def test_image_in_index_page(self):
        """Удостоверимся, что на главую страницу передаётся изображение"""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.context['page_obj'][1].image.name,
                         self.post.image.name)

    def test_post_with_group_in_index_page(self):
        """Удостоверимся, что при указании группы пост повляется
        на главной странице"""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(
            response.context['page_obj'][0].group.slug,
            PostPagesTests.group.slug)

    def test_context_in_group_list_page(self):
        """Удостоверимся, что на страницу группы передаётся список из постов
        а также удостоверимся, что при указании группы пост повляется
        на странице выбраной группы"""
        response = self.authorized_client.get(
            reverse('posts:posts', kwargs={'slug': 'test-slug'}))
        self.assertEqual(
            response.context['page_obj'][0].group.slug, self.group.slug)

    def test_image_in_group_list_page(self):
        """Удостоверимся, что на страницу группы передаётся
        пост с изображением"""
        response = self.authorized_client.get(
            reverse('posts:posts', kwargs={'slug': 'test-slug'}))
        self.assertEqual(
            response.context['page_obj'][1].image.name, self.post.image.name)

    @unittest.expectedFailure
    def test_post_with_group_in_wrong_group_list_page(self):
        """Удостоверимся, что пост с указанной группой
        не попал в группу, для которой не был предназначен."""
        response = self.authorized_client.get(
            reverse('posts:posts', kwargs={'slug': 'test-slug-2'}))
        self.assertEqual(
            response.context['page_obj'][1].group.slug,
            PostPagesTests.group.slug)

    def test_context_profile_page(self):
        """Удостоверимся, что на страницу
        профиля передаётся список из постов"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'admin'}))
        self.assertEqual(
            response.context['page_obj'][1].author.username,
            self.user.username)

    def test_context_profile_page(self):
        """Удостоверимся, что на страницу
        профиля передаётся пост с изображением"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'admin'}))
        self.assertEqual(
            response.context['page_obj'][0].image.name, self.post.image.name)

    def test_post_with_group_in_profile_page(self):
        """Удостоверимся, что при указании группы пост повляется
        на странице профиля странице"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'admin'}))
        self.assertEqual(
            response.context['page_obj'][0].group.slug,
            self.group.slug)

    def test_image_in_post_detail_page(self):
        """Удостоверимся, что на страницу поста передаётся пост"""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': 1}))
        self.assertEqual(response.context['posts'].image.name,
                         self.post.image.name)

    def test_comment_in_post_detail_page(self):
        """Удостоверимся, что на страницу поста передаётся пост"""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': 1}))
        self.assertEqual(response.context['comments'][0].text,
                         self.comment.text)

    def test_context_create_post_page(self):
        """Удостоверимся, что на страницу cоздания поста
        передаётся пост форма"""
        response = self.authorized_client.get(
            reverse('posts:post_create'))
        self.assertIsInstance(response.context['form'], PostForm)

    def test_context_edit_post_page(self):
        """Удостоверимся, что на страницу cоздания поста
        передаётся пост форма отфильтрованая по id"""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': '2'}))
        self.assertEqual(response.context['form'].instance.pk, 2)

    def test_follow(self):
        """Удостоверимся, пользователь может подписываться
        на других пользователей"""
        response = self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': 'admin2'}))
        response = self.authorized_client.get(
            reverse('posts:follow_index'))
        self.assertEqual(response.context['page_obj'][0].author, self.user2)
    
    def test_follow(self):
        """Удостоверимся, пользователь может подписываться
        на других пользователей и новая запись появляется в ленте"""
        response = self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': 'admin2'}))
        response = self.authorized_client.get(
            reverse('posts:follow_index'))
        self.assertEqual(response.context['page_obj'][0].author, self.user2)

    @unittest.expectedFailure
    def test_follow_self(self):
        """Удостоверимся, пользователь не может подписываться
        на самого себя"""
        response = self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': 'admin1'}))
        response = self.authorized_client.get(
            reverse('posts:follow_index'))
        self.assertEqual(response.context['page_obj'][0].author, self.user)

    @unittest.expectedFailure
    def test_unfollow(self):
        """Удостоверимся, пользователь может отписываться
        на других пользователей"""
        response = self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': 'admin2'}))
        response = self.authorized_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': 'admin2'}))
        response = self.authorized_client.get(
            reverse('posts:follow_index'))
        self.assertEqual(response.context['page_obj'][0].author, self.user2)

    @unittest.expectedFailure
    def test_unfollow_user_feed(self):
        """Удостоверимся, пользователь может отписываться
        на других пользователей"""
        response = self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': 'admin2'}))
        self.authorized_client.force_login(self.user3)
        response = self.authorized_client.get(
            reverse('posts:follow_index'))
        self.assertEqual(response.context['page_obj'][0].author, self.user2)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='admin')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        for i in range(20):
            cls.post = Post.objects.create(
                author=cls.user,
                text='Текст ' + '01' * 50,
                group=cls.group)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        cache.clear()
        response = self.client.get(reverse('posts:index'))
        """Проверка: количество постов на первой странице равно 10."""
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_some_ten_records(self):
        """Проверка: на второй странице должно быть быть десять постов."""
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_first_page_contains_ten_records_in_group_list(self):
        response = self.client.get(reverse('posts:posts',
                                           kwargs={'slug': 'test-slug'}))
        """Проверка: количество постов на первой странице равно 10."""
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_some_ten_records_in_group_list(self):
        """Проверка: на второй странице должно быть десять постов."""
        response = self.client.get(
            reverse('posts:posts', kwargs={'slug': 'test-slug'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_first_page_contains_ten_records_in_profile(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'admin'}))
        """Проверка: количество постов на первой странице равно 10."""
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_some_ten_records_in_profile(self):
        """Проверка: на второй странице должно быть десять постов."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'admin'}))
        self.assertEqual(len(response.context['page_obj']), 10)
