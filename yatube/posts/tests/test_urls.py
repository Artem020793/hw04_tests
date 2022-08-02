from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post


User = get_user_model()


class PostsURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Artem1993')
        cls.group = Group.objects.create(
            slug='group-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client_2 = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_status_guest(self):
        """Проверка статуса на странице для гостя"""
        templates_status_chek = {
            reverse('posts:index'): 200,
            reverse('posts:group_list', kwargs={'slug': self.group.slug}): 200,
            reverse('posts:profile', kwargs={'username':
                                         self.user.username}): 200,
            reverse('posts:post_detail', kwargs={'post_id':
                                             self.post.id}): 200,
            reverse('posts:post_create'): 302,
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}): 302,
        }
        for url, status in templates_status_chek.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_create_url_authorized(self):
        """Проверка доступа для авторизованного
        пользователя к созданию поста"""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_url_uses_correct_template(self):
        url_templates_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}):
                        'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.user.username}):
                        'posts/profile.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}):
                        'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}):
                        'posts/create_post.html',
        }
        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
