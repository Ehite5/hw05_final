from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post


User = get_user_model()
NUMBER_OF_LETTERS = 15


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост для проверки и исправления ошибок в коде',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""

        group = PostModelTest.group
        post = PostModelTest.post
        expected_items = {
            group: group.title,
            post: post.text[:NUMBER_OF_LETTERS]
        }
        for field, expected in expected_items.items():
            with self.subTest():
                self.assertEqual(
                    str(field),
                    expected,
                    f'Ошибка __str__ у {field}'
                )
