from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from ..models import Comment, Follow, Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            image='Картинка',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        group = PostModelTest.group
        self.assertEqual(post.text, post.__str__(), 'Тестовый пост')
        self.assertEqual(group.title, group.__str__(), 'Тестовый заголовок')


class CommenModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='user')
        cls.post = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
        )
        cls.author = Post.objects.create()
        cls.text = Post.objects.create(
            text_comm='Текст комментария'
        )


class FollowTests(TestCase):
    def test_no_self_follow(self):
        user = User.objects.create(username='user')
        constraint_name = "check_not_self_follow"
        with self.assertRaisesMessage(IntegrityError, constraint_name):
            Follow.objects.create(user=user, author=user)
