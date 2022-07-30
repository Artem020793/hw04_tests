from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Текст',
            slug='group-slug',
            description='Текст',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        self.authorized_client.force_login(PostPagesTests.user)
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': PostPagesTests.group.slug}):
                           'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': PostPagesTests.user}):
                           'posts/profile.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': PostPagesTests.post.id}):
                           'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': PostPagesTests.post.id}):
                           'posts/create_post.html',
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_form_post_create_and_edit_show_correct_context(self):
        """Формы на страницах post_create и post_edit корректны"""
        context = {
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        }
        for reverse_page in context:
            with self.subTest(reverse_page=reverse_page):
                response = self.authorized_client.get(reverse_page)
                form_field = response.context['form'].fields['text']
                self.assertIsInstance(form_field, forms.fields.CharField)
                form_field = response.context['form'].fields['group']
                self.assertIsInstance(form_field, forms.fields.ChoiceField)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:group_list', 
                                                      kwargs={'slug': self.group.slug}))
        first_object = response.context['page_obj'][0]
        post_text = first_object.text
        post_author = first_object.author
        post_pub_date = first_object.pub_date
        post_group_id = first_object.group.id
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_author, self.post.author)
        self.assertEqual(post_pub_date, self.post.pub_date)
        self.assertEqual(post_group_id, self.post.group.id)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        reverse_page = reverse('posts:post_detail',
                               kwargs={'post_id': self.post.id})
        response = (self.authorized_client.get(reverse_page))
        self.assertEqual(response.context['user_post'].text,
                         self.post.text)
        self.assertEqual(response.context['user_post'].pub_date,
                         self.post.pub_date)
        self.assertEqual(response.context['user_post'].author,
                         self.post.author)
        self.assertEqual(response.context['user_post'].group.id,
                         self.post.group.id)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Artem1993',
                                            email='test@mail.ru',
                                            password='test_pass',)
        cls.group = Group.objects.create(
            title=('Заголовок для тестовой группы'),
            slug='test_slug2',
            description='Тестовое описание')

        for i in range(13):
            Post.objects.create(
                text=f'Тестовый пост {i}',
                author=cls.user,
                group=cls.group
            )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_two_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)
