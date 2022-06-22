import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from django import forms
from django.conf import settings
from django.core.cache import cache
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from .test_constants import (COMMENT_TEXT, NUMBER_OF_POSTS,
                             NUMBER_OF_TEST_POSTS, SMALL_GIF)

from ..models import Comment, Follow, Group, Post, User
from .test_constants import (CREATE_URL, GROUP_URL,
                             INDEX_URL,
                             PROFILE_URL, USERNAME)


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.no_author = User.objects.create_user(username='NoAuthorUser')
        cls.no_follower = User.objects.create_user(username='NoFollower')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        all_posts = []
        for i in range(NUMBER_OF_TEST_POSTS):
            cls.posts = []
            all_posts.append(
                Post(
                    text=f'Тестовый пост {i}',
                    author=cls.user,
                    group=cls.group,
                    image=SimpleUploadedFile(
                        name='small.gif',
                        content=SMALL_GIF,
                        content_type='image/gif'
                    )
                )
            )
        Post.objects.bulk_create(all_posts)
        cls.posts = list(Post.objects.all())
        cls.EDIT_URL = reverse(
            'posts:post_update', kwargs={'post_id': cls.posts[0].pk}
        )
        cls.DETAIL_URL = reverse(
            'posts:post_detail', kwargs={'post_id': cls.posts[0].pk}
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.no_author)
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_uses_correct_template(self):
        """Используется корректный шаблон"""

        templates_pages_names = {
            INDEX_URL: 'posts/index.html',
            GROUP_URL: 'posts/group_list.html',
            PROFILE_URL: 'posts/profile.html',
            self.DETAIL_URL: 'posts/post_detail.html',
            CREATE_URL: 'posts/create_post.html',
            self.EDIT_URL: 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_first_page_contains_ten_records(self):
        """Проверка паджинатора на первой странице"""

        pages = [
            INDEX_URL,
            PROFILE_URL,
            GROUP_URL,
        ]
        for page in pages:
            response = self.authorized_client.get(page)
            self.assertEqual(
                len(response.context['page_obj']),
                NUMBER_OF_POSTS,
                'Паджинатор работает некорректно'
            )

    def test_last_page_for_paginator(self):
        """Проверка паджинатора на последней странице."""
        pages = [
            INDEX_URL,
            PROFILE_URL,
            GROUP_URL,
        ]
        for page in pages:
            count = 1
            response = self.authorized_client.get(page + '?page=3')
            self.assertEqual(
                len(response.context['page_obj']),
                count,
                'Паджинатор работает некорректно'
            )

    def test_group_list_context(self):
        """Проверка правильного отображения постов на странице группы."""

        response = self.guest_client.get(GROUP_URL)
        last_object = response.context['page_obj'][0]
        text_groups_check = response.context['text_groups']
        group_check = response.context['group']
        text_gr = last_object.text
        author_gr = last_object.author.username
        image_gr = last_object.image
        group_gr = last_object.group.title

        self.assertEqual(text_gr, f'Тестовый пост {NUMBER_OF_TEST_POSTS-1}')
        self.assertEqual(text_groups_check,
                         'Записи сообщества "Тестовая группа"')
        self.assertEqual(str(group_check), 'Тестовая группа')
        self.assertEqual(author_gr, 'TestUser')
        self.assertEqual(group_gr, 'Тестовая группа')
        self.assertIsNotNone(image_gr)

    def test_index_url_context(self):
        """Проверка правильной передачи контекста на главную страницу."""

        response = self.guest_client.get(INDEX_URL)
        last_object = response.context['page_obj'][0]
        text_index = last_object.text
        author_index = last_object.author.username
        group_index = last_object.group.title
        image_index = last_object.image
        text_main_check = response.context['text_main']

        self.assertEqual(text_index, f'Тестовый пост {NUMBER_OF_TEST_POSTS-1}')
        self.assertEqual(author_index, 'TestUser')
        self.assertEqual(group_index, 'Тестовая группа')
        self.assertEqual(text_main_check, 'Последние обновления на сайте')
        self.assertIsNotNone(image_index)

    def test_post_profile_page_show_correct_context(self):
        """Проверка контекста profile"""

        response = self.guest_client.get(PROFILE_URL)
        last_object = response.context['page_obj'][0]
        text_pr = last_object.text
        author_pr = last_object.author.username
        group_pr = last_object.group.title
        post_count = response.context['all_author_posts']
        author_name_check = response.context['author_name']
        image_pr = last_object.image

        self.assertEqual(text_pr, f'Тестовый пост {NUMBER_OF_TEST_POSTS-1}')
        self.assertEqual(author_pr, 'TestUser')
        self.assertEqual(group_pr, 'Тестовая группа')
        self.assertEqual(post_count, NUMBER_OF_TEST_POSTS)
        self.assertEqual(str(author_name_check), 'TestUser')
        self.assertIsNotNone(image_pr)

    def test_post_detail_context(self):
        """Проверка контекста, передаваемого в post_detail."""

        response = self.guest_client.get(self.DETAIL_URL)
        last_object = response.context['post']
        post_count = response.context['all_author_posts']
        title_30_check = response.context['title_30']
        text_det = last_object.text
        author_det = last_object.author.username
        group_det = last_object.group.title
        image_det = last_object.image

        self.assertEqual(text_det, f'Тестовый пост {NUMBER_OF_TEST_POSTS-1}')
        self.assertEqual(author_det, 'TestUser')
        self.assertEqual(group_det, 'Тестовая группа')
        self.assertEqual(post_count, NUMBER_OF_TEST_POSTS)
        self.assertEqual(title_30_check,
                         f'Тестовый пост {NUMBER_OF_TEST_POSTS-1}')
        self.assertIsNotNone(image_det)

    def test_post_edit_form(self):
        """Проверка формы редактирования поста."""

        response = self.authorized_client.get(self.EDIT_URL)
        last_object = response.context['post']
        is_edit = response.context.get('is_edit')
        text_ed = last_object.text
        author_ed = last_object.author.username
        group_ed = last_object.group.title
        self.assertTrue(is_edit)
        self.assertEqual(text_ed, f'Тестовый пост {NUMBER_OF_TEST_POSTS-1}')
        self.assertEqual(author_ed, 'TestUser')
        self.assertEqual(group_ed, 'Тестовая группа')

    def test_post_create_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""

        response = self.authorized_client.get(CREATE_URL)
        is_edit = response.context.get('is_edit')
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
            'image': forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertFalse(is_edit)

    def test_new_post_on_different_pages(self):
        """Появление поста на разных страницах
        """

        new_post = Post.objects.create(
            text='Тестовый пост',
            author=self.user,
            group=self.group,
            image=self.uploaded
        )
        pages = {
            'index': INDEX_URL,
            'group': GROUP_URL,
            'profile': PROFILE_URL,
        }
        for name, template in pages.items():
            with self.subTest(reverse_name=template):
                response = self.guest_client.get(template)
                self.assertEqual(
                    response.context.get('page_obj').object_list[0],
                    new_post,
                    f'Пост {name} отсутвует на других страницах :('
                )

    def test_post_not_add_another_group(self):
        """
        При создании поста с указанием группы,
        этот пост НЕ попал в группу, для которой не был предназначен.
        """

        response = self.authorized_client.get(INDEX_URL)
        post = response.context['page_obj'][0]
        group = post.group
        self.assertEqual(group, self.group)

    def test_new_comment_exists(self):
        """Проверка появления нового комментария на странице."""

        new_post = Post.objects.create(
            text='Тестовый пост',
            author=self.user,
            group=self.group,
            image=self.uploaded
        )
        count_of_comments = Comment.objects.filter(post=new_post).count()
        Comment.objects.create(
            post=new_post,
            text=COMMENT_TEXT,
            author=self.user
        )
        response = self.guest_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': new_post.pk}
        ))
        self.assertEqual(
            response.context['comments'].count(),
            count_of_comments + 1,
            'На странице поста не появился новый комментарий'
        )


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Author')
        cls.post = Post.objects.create(author=cls.author,
                                       text='Тестовый пост')

    def test_posts_cache(self):
        """Записи хранятся в течение 20 секунд (кеширование)"""

        response = self.client.get(INDEX_URL)
        self.assertContains(response, self.post.text)
        Post.objects.get(pk=self.post.pk).delete()
        response = self.client.get(INDEX_URL)
        self.assertContains(response, self.post.text)
        cache.clear()
        response = self.client.get(INDEX_URL)
        self.assertNotContains(response, self.post.text)


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(username='USERNAME1')
        cls.user2 = User.objects.create_user(username='USERNAME2')
        cls.author = User.objects.create_user(username='Author')
        cls.post = Post.objects.create(author=cls.author,
                                       text='Тестовый пост')

    def setUp(self):
        self.follower_client = Client()
        self.follower_client.force_login(self.user1)
        self.unfollower_client = Client()
        self.unfollower_client.force_login(self.user2)

    def test_profile_follow(self):
        """Авторизованный пользователь может подписываться и отписываться"""

        self.follower_client.get(
            reverse('posts:profile_follow', args=(self.author,)))
        self.assertTrue(Follow.objects.filter(
            user=self.user1, author=self.author).exists())
        self.follower_client.get(
            reverse('posts:profile_unfollow', args=(self.author,)))
        self.assertFalse(Follow.objects.filter(
            user=self.user1, author=self.author).exists())

    def test_follow_index_contains_records(self):
        """Новые записи автора появляются только у подписчиков"""

        self.follower_client.get(
            reverse('posts:profile_follow', args=(self.author,)))
        response = self.follower_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 1)
        self.assertEqual(response.context['page_obj'][0].pk,
                         self.post.pk)
        response = self.unfollower_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 0)
