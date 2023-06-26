from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('titul', 'text', 'group', 'image')
        labels = {
            "titul": ("Ключевое слово"),
            "text": ("Текстовое поле"),
            "group": ("Выберите группу"),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
