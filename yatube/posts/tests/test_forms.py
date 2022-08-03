from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Текстовый заголовок',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.test_user = User.objects.create_user(username='test_user')

        cls.post = Post.objects.create(
            text='Текст',
            author=cls.test_user,
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.guest_client = Client()
        self.authorized_client.force_login(self.test_user)

    def test_post(self):
        """Тестирование создания Post"""
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
                             kwargs={'username': self.test_user}))
        self.assertEqual(post_count, count_posts + 1)

    def test_guest_new_post(self):
        """Неавторизоанный не может создавать посты"""
        form_data = {
            'text': 'Пост от неавторизованного пользователя',
        }
        self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertFalse(Post.objects.filter(
            text='Пост от неавторизованного пользователя').exists())

    def test_post_edit_authorized_user(self):
        """Авторизованный пользователь. Редактирование поста."""
        '#Создаем экземпляр поста перед редактированием'
        post = Post.objects.create(
            text='Проверка редактирования.',
            author=self.test_user,
            group=self.group,
        )
        '#Заполняем форму для редактирования'
        form_data = {
            'text': 'Редактирование',
            'group': self.group.id,
        }
        '#Подчитываем количество постов'
        posts_count = Post.objects.count()
        '#Отправляем пост запрос на редактирования поста'
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        '#Объявляем адрес редиректа'
        redirect = reverse(
            'posts:post_detail',
            kwargs={'post_id': post.id})
        '#Проверяем редиректность'
        self.assertRedirects(response, redirect)
        '#Проверяем не создался ли новый пост'
        self.assertEqual(Post.objects.count(), posts_count)
        '#есть ли в списке постов пост с отредактированными данными'
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=self.group.id,
                author=self.test_user
            ).exists()
        )
