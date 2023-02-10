import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.forms import PostForm

from ..models import Comment, Group, Post

User = get_user_model()

EDIT = 'posts:post_edit'
CREATE = 'posts:post_create'
CREATE_COMMENT = 'posts:add_comment'
UNIQUE = 'Уникальный текст'
EDIT_TEXT = 'Измененный текст'
COMMENT_TEXT = 'Комментария'
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
SMAIL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x01\x00'
    b'\x01\x00\x00\x00\x00\x21\xf9\x04'
    b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
    b'\x00\x00\x01\x00\x01\x00\x00\x02'
    b'\x02\x4c\x01\x00\x3b'
)
IMAGE = 'posts/small.gif'


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='admin')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='text-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текстовый текст',
            image=IMAGE,
        )
        cls.new_text = 'Новый текст'
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()

        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMAIL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': UNIQUE,
            'group': self.group.pk,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse(CREATE),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            Post.objects.filter(
                text=UNIQUE,
                group=self.group.pk,
                image=IMAGE).exists()
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_post_edit(self):
        test_post = self.post
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMAIL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': EDIT_TEXT,
            'group': self.group.pk,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse(EDIT, kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotEqual(test_post.text, EDIT_TEXT)
        self.assertTrue(
            Post.objects.filter(
                id=self.post.pk,
                text=EDIT_TEXT,
                group=self.group.pk,).exists()
        )

    def test_create_comment(self):
        count_comm = Comment.objects.count()
        form_data = {
            'text': COMMENT_TEXT,
        }
        response = self.authorized_client.post(
            reverse(CREATE_COMMENT, kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), count_comm + 1)
        self.assertTrue(
            Comment.objects.filter(
                text=COMMENT_TEXT,
                post=self.post,
                author=self.user).exists()
        )
        self.assertContains(response, f'<p>{COMMENT_TEXT}</p>', html=True)
