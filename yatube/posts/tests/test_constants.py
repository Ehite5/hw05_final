from django.urls import reverse


INDEX_URL = reverse('posts:index')
FOLLOW_URL = reverse('posts:follow_index')
CREATE_URL = reverse('posts:post_create')
GROUP_URL = reverse('posts:group_list', kwargs={'slug': 'test-slug'})
PROFILE_URL = reverse('posts:profile', kwargs={'username': 'TestUser'})
COMMENT_URL = reverse('posts:add_comment')


USERNAME = 'TestUser'

GROUP_TITLE = 'Тестовая группа'
GROUP_SLUG = 'test-slug'
GROUP_DESCRIPTION = 'Тестовое описание'
POST_TEXT = 'Тестовый пост'

FORM_GROUP_TITLE = 'Тестовая группа для формы'
FORM_GROUP_SLUG = 'test-slug'
FORM_GROUP_DESCRIPTION = 'Тестовое описание'
FORM_POST_TEXT = 'Тестовый пост для проверки формы'

MODEL_USERNAME = 'auth'
MODEL_POST_TEXT = 'Тестовый текст модели'

NUMBER_OF_POSTS = 10
NUMBER_OF_TEST_POSTS = 21
NUMBER_FOR_TESTING_VIEWS = 17

SMALL_GIF = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
             )

COMMENT_TEXT = 'Тестовый комментарий'
