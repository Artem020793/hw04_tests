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
            title='Тестовое название группы',
            slug='group-slug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст',
            group=cls.group,
        )

    def setUp(self):

        self.authorized_client = Client()
        self.guest_client = Client()
        self.authorized_client.force_login(self.user)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:group_list',
                                              kwargs={'slug':
                                                      self.group.slug}))
        self.assertIn('page_obj', response.context)
        self.assertIn('group', response.context)
        post_test = response.context['page_obj'][0]
        self.assertEqual(post_test, self.post)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        reverse_page = reverse('posts:post_detail',
                               kwargs={'post_id': self.post.id})
        response = (self.authorized_client.get(reverse_page))
        self.assertIn('user_post', response.context)
        self.assertEqual(response.context['user_post'].text,
                         self.post.text)
        self.assertEqual(response.context['user_post'].pub_date,
                         self.post.pub_date)
        self.assertEqual(response.context['user_post'].author,
                         self.post.author)
        self.assertEqual(response.context['user_post'].group.id,
                         self.post.group.id)
        
    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        test_post = response.context['page_obj'][0]
        self.assertEqual(test_post.author, self.post.author)
        self.assertEqual(test_post.text, self.post.text)
        self.assertEqual(test_post.group, self.post.group)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:profile', kwargs={'username': self.user.username}))
        test_post = response.context['page_obj'][0]
        self.assertEqual(test_post.author, self.post.author)
        self.assertEqual(test_post.text, self.post.text)
        self.assertEqual(test_post.group, self.post.group)
        
    def test_post_create_and_edit_page_correct_context_form(self):
        """Шаблон редактирования/создания поста сформирован с правильным контекстом."""
        url_tests = {
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        }
        for url in url_tests:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                form_field_text = response.context['form'].fields['text']
                self.assertIsInstance(form_field_text, forms.fields.CharField)
                form_field_group = response.context['form'].fields['group']
                self.assertIsInstance(form_field_group, forms.fields.ChoiceField)
            
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

        Post.objects.bulk_create([
            Post(text='Тестовый пост',
                 author=cls.user,
                 group=cls.group) for i in range(13)
        ])

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pagination(self):
        tested_urls_paginations = {
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': self.user})
        }
        for url in tested_urls_paginations:
            with self.subTest(url=url):
                response_one_page = self.client.get(url)
                self.assertEqual(
                    len(response_one_page.context['page_obj']), 10)
                response_two_page = self.client.get(url + '?page=2')
                self.assertEqual(
                    len(response_two_page.context['page_obj']), 3)
