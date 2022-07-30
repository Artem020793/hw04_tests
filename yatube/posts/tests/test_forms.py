from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from posts.models import Group, Post

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title=('Текстовый заголовок'),
            slug='test_slug',
            description='Тестовое описание'
        )

        cls.post = Post.objects.create(
            text='текст',
            author=cls.user,
            group=cls.group,
        )
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='mob2556')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post(self):
        count_posts = Post.objects.count()
        form_data = {
            'text': 'Данные из формы',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        post_count = Post.objects.count()
        self.assertRedirects(response, reverse('posts:profile',
                            kwargs={'username': self.user}))
        self.assertEqual(post_count, count_posts + 1)

    def test_guest_new_post(self):
        # неавторизоанный не может создавать посты
        form_data = {
            'text': 'Пост от неавторизованного пользователя',
            'group': self.group.id
        }
        self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertFalse(Post.objects.filter(
            text='Пост от неавторизованного пользователя').exists())

    def test_authorized_edit_post(self):
        # авторизованный может редактировать
        form_data = {
            'text': 'Данные из формы',
            'group': self.group.id
        }
        post_2 = Post.objects.get(pk=self.post.id)
        self.client.get(f'/mob2556/{post_2.id}/edit/')
        form_data = {
            'text': 'Измененный текст',
            'group': self.group.id
        }
        response_edit = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={
                        'post_id': post_2.id
                    }),
            data=form_data,
            follow=True,
        )
        post_2 = Post.objects.get(id=self.post.id)
        self.assertEqual(response_edit.status_code, 200)
