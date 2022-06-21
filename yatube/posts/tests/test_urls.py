from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from yatube.settings import WORKS_WELL

from ..models import Group, Post, User
from .test_constants import (CREATE_URL, GROUP_URL,
                             GROUP_DESCRIPTION, GROUP_SLUG,
                             GROUP_TITLE, FORM_POST_TEXT,
                             INDEX_URL, PROFILE_URL, USERNAME)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.no_author = User.objects.create_user(username='NoAuthorUser')
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION
        )
        cls.post = Post.objects.create(
            text=FORM_POST_TEXT,
            author=cls.user,
            group=cls.group
        )
        cls.EDIT_URL = reverse(
            'posts:post_update', kwargs={'post_id': cls.post.id}
        )
        cls.DETAIL_URL = reverse(
            'posts:post_detail', kwargs={'post_id': cls.post.id}
        )
        cls.COMMENT_URL = reverse(
            'posts:add_comment', kwargs={'post_id': cls.post.id})

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.no_author)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_url_names = {
            INDEX_URL: 'posts/index.html',
            GROUP_URL: 'posts/group_list.html',
            PROFILE_URL: 'posts/profile.html',
            self.DETAIL_URL: 'posts/post_detail.html',
            CREATE_URL: 'posts/create_post.html',
            self.EDIT_URL: 'posts/create_post.html',
        }
        for adress_url, template in templates_url_names.items():
            with self.subTest(adress=adress_url):
                response = self.authorized_client.get(adress_url)
                self.assertTemplateUsed(response, template)

    def test_url_for_all(self):
        """Проверка страниц, которые доступны всем"""

        templates_url = [
            INDEX_URL,
            GROUP_URL,
            PROFILE_URL,
            self.DETAIL_URL,
        ]
        for adress_url in templates_url:
            response = self.guest_client.get(adress_url)
            self.assertEqual(response.status_code, WORKS_WELL)

    def test_pages_are_not_found(self):
        """Проверка на create, edit, comment для автор. и неавтор. пользователя
        """

        response = {
            self.authorized_client.get(CREATE_URL): HTTPStatus.OK,
            self.authorized_client.get(self.EDIT_URL): HTTPStatus.OK,
            self.guest_client.get('not_exist/'): HTTPStatus.NOT_FOUND,
            self.authorized_client.get('not_exist/'): HTTPStatus.NOT_FOUND,
        }
        for response, code in response.items():
            with self.subTest(code=code):
                self.assertEqual(response.status_code, code)

    def test_redirect_edit_not_for_author(self):
        """Перенаправление пользователя, который является неавтором,
           при редактировании
        """
        response = self.authorized_client2.get(self.EDIT_URL)
        self.assertRedirects(response, PROFILE_URL)

    def test_redirect_edit_for_guest(self):
        """Перенаправление пользователя, который незарегистрирован,
           при редактировании или комментировании
        """

        response_edit = self.guest_client.get(self.EDIT_URL)
        response_comment = self.guest_client.get(self.COMMENT_URL)
        self.assertRedirects(response_edit, (
            f'/auth/login/?next=/posts/{PostURLTests.post.pk}/edit/'))
        self.assertRedirects(response_comment, (
            f'/auth/login/?next=/posts/{PostURLTests.post.pk}/comment/'))

    def test_redirect_create_for_guest(self):
        """Перенаправление пользователя, который незарегистрирован,
           при создании поста
        """

        response = self.guest_client.get(CREATE_URL)
        self.assertRedirects(response, ('/auth/login/?next=/create/'))
