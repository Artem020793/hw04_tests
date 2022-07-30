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

    def test_url_uses_correct_index(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_url_uses_correct_group(self):
        response = self.guest_client.get(f'/group/{self.group.slug}/')
        self.assertEqual(response.status_code, 200)

    def test_url_uses_correct_profile(self):
        response = self.guest_client.get(f'/profile/{self.user}/')
        self.assertEqual(response.status_code, 200)

    def test_url_authorized_post_id(self):
        response = self.guest_client.get(f'/posts/{self.post.id}/')
        self.assertEqual(response.status_code, 200)

    def test_create_url_authorized(self):
        """Проверка доступа для авторизованного 
        пользователя к созданию поста"""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)
        
    def test_create_url_unauthorized(self):
        """Проверка доступа для неавторизованного 
        пользователя к созданию поста"""
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, 302)
        
    def test_edit_url_unauthorized(self):
        """Проверка доступа для неавторизованного пользователя
         к редактированию поста"""
        response = self.guest_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, 302)
        
    def test_edit_url_not_by_author(self):
        """Проверка доступа для не автора к редактированию поста"""
        response = self.authorized_client_2.get(
            f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, 302)
        
    def test_unexisting_url(self):
        """Проверка несуществующей страницы"""
        response = self.guest_client.get('/unexisting/')
        self.assertEqual(response.status_code, 404)
        
    def test_home_url_uses_correct_template(self):
        url_templates_names = {
            reverse('posts:index') : 'posts/index.html',
            reverse('posts:group_list', 
                    kwargs={'slug': self.group.slug}) : 'posts/group_list.html',
            reverse('posts:profile', 
                    kwargs={'username': self.user.username}) : 'posts/profile.html',
            reverse('posts:post_create') : 'posts/create_post.html',
            reverse('posts:post_detail', 
                    kwargs={'post_id': self.post.id}) : 'posts/post_detail.html',
            reverse('posts:post_edit', 
                    kwargs={'post_id': self.post.id}) : 'posts/create_post.html',
        }
        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
                