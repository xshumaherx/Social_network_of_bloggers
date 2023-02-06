from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()
HTML_INDEX = 'posts/index.html'
HTML_GROUP_LIST = 'posts/group_list.html'
HTML_PROFILE = 'posts/profile.html'
HTML_DETAIL = 'posts/post_detail.html'
HTML_EDIT_CREATE = 'posts/create_post.html'
HTML_FOLLOW = 'posts/follow.html'
UNEXISTING_URL = '/unexisting_page'
IMAGE = 'posts/small.gif'


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='user')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текстовый пост',
            image=IMAGE
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_exists_at_desired_location(self):
        """Страница доступна любому пользователю."""
        address_url_names = {
            '/': HTML_INDEX,
            f'/group/{self.group.slug}/': HTML_GROUP_LIST,
            f'/profile/{self.post.author}/': HTML_PROFILE,
            f'/posts/{self.post.pk}/': HTML_DETAIL,
        }

        for address in address_url_names:
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': HTML_GROUP_LIST,
            f'/profile/{self.post.author}/': HTML_PROFILE,
            f'/posts/{self.post.pk}/': HTML_DETAIL,
            f'/posts/{self.post.pk}/edit/': HTML_EDIT_CREATE,
            '/create/': HTML_EDIT_CREATE,
            '/follow/': HTML_FOLLOW,
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_create_url_redirect_anonymous(self):
        """Страница /create/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.client.get('/create/')
        self.assertRedirects(
            response, '/auth/login/?next=/create/')

    def test_edit_url_redirect_anonymous(self):
        """Страница /edit/ неавторизованный
        перенаправит на авторизацию."""
        response = self.client.get(
            f'/posts/{self.post.pk}/edit/')
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.pk}/edit/')

    def test_edit_url_redirect_authorized(self):
        """'Страница /edit/ доступна только автору.'"""
        response = self.authorized_client.get(
            f'/posts/{self.post.pk}/edit/')
        self.assertEqual(
            response.status_code, HTTPStatus.OK)

    def test_unexisting_page_get_404(self):
        """'Несуществующая страница'"""
        response = self.client.get(UNEXISTING_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_follow_author_url_redirect_anonymous(self):
        """При попытке подписаться неавторизованный
        перенаправит на авторизацию."""
        response = self.client.get(
            f'/profile/{self.post.author}/follow/')
        self.assertRedirects(
            response, f'/auth/login/?next=/profile/{self.post.author}/follow/')

    def test_follow_url_redirect_anonymous(self):
        """Страница /follow/ неавторизованный
        перенаправит на авторизацию."""
        response = self.client.get(
            '/follow/')
        self.assertRedirects(
            response, '/auth/login/?next=/follow/')
