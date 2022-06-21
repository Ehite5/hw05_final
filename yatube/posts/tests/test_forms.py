import shutil
import tempfile

from django.conf import settings
from posts.models import Post
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile


from ..models import Group, Post, User
from .test_constants import (CREATE_URL, FORM_GROUP_DESCRIPTION,
                             FORM_GROUP_SLUG, FORM_GROUP_TITLE,
                             FORM_POST_TEXT, PROFILE_URL, SMALL_GIF, USERNAME)

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
            title=FORM_GROUP_TITLE,
            slug=FORM_GROUP_SLUG,
            description=FORM_GROUP_DESCRIPTION
        )
        cls.post = Post.objects.create(
            text=FORM_POST_TEXT,
            author=cls.user,
            group=cls.group,
            image=SimpleUploadedFile(
                name='small.gif',
                content=SMALL_GIF,
                content_type='image/gif'
            )
        )
        cls.EDIT_URL = reverse(
            'posts:post_update', kwargs={'post_id': cls.post.id}
        )
        cls.DETAIL_URL = reverse(
            'posts:post_detail', kwargs={'post_id': cls.post.id}
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def tearDown(self):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post_form(self):
        """Проверка появления новой записи в Базе Данных."""

        posts_count = Post.objects.count()
        form_data = {
            'text': FORM_POST_TEXT,
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            CREATE_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            PROFILE_URL,
            msg_prefix='Переадресация не работает'
        )
        self.assertEqual(
            Post.objects.count(),
            posts_count + 1,
            'Нет нового поста'
        )
        self.assertTrue(
            Post.objects.filter(
                text=FORM_POST_TEXT,
                group=form_data['group'],
                author=self.user,
            ).exists()
        )

    def test_edit_post_form(self):
        """Проверка изменения записи в Базе Данных"""

        posts_count = Post.objects.count()
        form_data_new = {
            'text': 'Новый текст',
            'group': self.group.id,
            'image': self.image
        }
        response = self.authorized_client.post(
            self.EDIT_URL,
            data=form_data_new,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data_new['text'],
                group=form_data_new['group'],
                author=self.user,
            ).exists()
        )
        self.assertRedirects(
            response,
            self.DETAIL_URL,
            msg_prefix='Переадресация не работает'
        )
        self.assertEqual(
            Post.objects.count(),
            posts_count,
            'Появился новый пост, такого быть не должно'
        )
