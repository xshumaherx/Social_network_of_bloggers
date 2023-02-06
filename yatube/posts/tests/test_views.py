from http import HTTPStatus

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Follow, Group, Post

User = get_user_model()
TEMP_NUMB_FIRST_PAGE = 13
TEMP_NUMB_SECOND_PAGE = 3
INDEX = 'posts:index'
GROUP_LIST = 'posts:group_list'
PROFILE = 'posts:profile'
DETAIL = 'posts:post_detail'
EDIT = 'posts:post_edit'
CREATE = 'posts:post_create'
HTML_INDEX = 'posts/index.html'
HTML_GROUP_LIST = 'posts/group_list.html'
HTML_PROFILE = 'posts/profile.html'
HTML_DETAIL = 'posts/post_detail.html'
HTML_EDIT_CREATE = 'posts/create_post.html'


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='user')
        cls.user1 = User.objects.create(username='user1')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            group=cls.group,
            author=cls.user,
            text='Текстовый текст',
            image='Картинка'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """ URL-адрес использует соответствующий шаблон. """
        templates_page_names = {
            reverse(INDEX): HTML_INDEX,
            reverse(GROUP_LIST,
                    kwargs={'slug': self.group.slug}): HTML_GROUP_LIST,
            reverse(PROFILE,
                    kwargs=({'username': self.post.author})): HTML_PROFILE,
            reverse(DETAIL,
                    kwargs=({'post_id': self.post.pk})): HTML_DETAIL,
            reverse(EDIT,
                    kwargs=({'post_id': self.post.pk})): HTML_EDIT_CREATE,
            reverse(CREATE): HTML_EDIT_CREATE
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_uses_correct_template_for_guest(self):
        """ URL-адрес использует соответствующий шаблон для гостей. """
        templates_page_names = {
            reverse(INDEX): HTML_INDEX,
            reverse(GROUP_LIST,
                    kwargs={'slug': self.group.slug}): HTML_GROUP_LIST,
            reverse(PROFILE,
                    kwargs=({'username': self.post.author})): HTML_PROFILE,
            reverse(DETAIL,
                    kwargs=({'post_id': self.post.pk})): HTML_DETAIL,
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_create_page_show_correct_context(self):
        """ Шаблон post_create сформирован с правильным контекстом. """
        response = self.authorized_client.get(reverse(CREATE))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """ Шаблон post_edit сформирован с правильным контекстом. """
        response = self.authorized_client.get(
            reverse(EDIT, kwargs=({'post_id': self.post.pk})))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_list_page_show_correct_context(self):
        """Шаблон post_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(INDEX))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.id, self.post.pk)
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.author, self.user)
        self.assertEqual(first_object.group, self.group)
        self.assertEqual(first_object.group.id, self.group.pk)
        self.assertEqual(first_object.author.id, self.user.pk)
        self.assertEqual(first_object.image, self.post.image)

    def test_follow_unfollow_auth(self):
        """Подписка и отписка авторов"""
        count_subscription = Follow.objects.count()

        self.authorized_client.get(reverse(
            'posts:profile_follow', kwargs={'username': self.user1}
        ))
        self.assertEqual(Follow.objects.count(), count_subscription + 1)

        self.authorized_client.get(reverse(
            'posts:profile_unfollow', kwargs={'username': self.user1})
        )
        self.assertEqual(Follow.objects.count(), count_subscription)
        self.assertFalse(
            Follow.objects.filter(
                user=self.user,
                author=self.user).exists()
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='user')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )

    def setUp(self):
        for i in range(TEMP_NUMB_FIRST_PAGE):
            Post.objects.create(
                text=f'{i}',
                author=self.user,
                group=self.group,
            )

    def test_first_page_contains_ten_records(self):
        pages = [
            reverse(INDEX),
            reverse(GROUP_LIST, kwargs={'slug': self.group.slug}),
            reverse(PROFILE, kwargs=({'username': self.user})),
        ]

        for page in pages:
            with self.subTest(page=page):
                response = self.client.get(page)
        self.assertEqual(
            len(response.context['page_obj']),
            settings.NUMBER_ENTRIES_FOR_PAGE)

    def test_second_page_contains_three_records(self):
        pages = [
            reverse(INDEX),
            reverse(GROUP_LIST, kwargs={'slug': self.group.slug}),
            reverse(PROFILE, kwargs=({'username': self.user})),
        ]

        for page in pages:
            with self.subTest(page=page):
                response = self.client.get(page + '?page=2')
        self.assertEqual(len(response.context['page_obj']),
                         TEMP_NUMB_SECOND_PAGE)
