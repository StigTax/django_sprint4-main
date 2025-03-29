from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

from .models import Post, Category, Location, Comment

User = get_user_model()


class EditUserForm(UserChangeForm):
    """Форма редактирования профиля."""

    password = None

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']


class PostForm(forms.ModelForm):
    """Форма для создания публикаций постов."""

    class Meta:
        model = Post
        fields = [
            'title', 'text',
            'pub_date', 'category', 'location',
            'is_published', 'image'
        ]
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(
            is_published=True
        )
        self.fields['location'].queryset = Location.objects.filter(
            is_published=True
        )


class CommentForm(forms.ModelForm):
    """Форма для создания комментариев под публикациями."""

    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.post = kwargs.pop('post', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        comment = super().save(commit=False)
        if self.post:
            comment.post = self.post
        if commit:
            comment.save()
        return comment
