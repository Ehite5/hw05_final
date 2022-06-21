from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст Вашего поста',
            'group': 'Группа',
            'image': 'Картинка к Вашему посту'
        }
        help_texts = {
            'text': 'Текст поста',
            'group': 'Группа, к которой относится пост!',
            'image': 'Картинка к Вашему посту'
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        help_texts = {
            'text': 'Текст Вашего комментария',
        }
