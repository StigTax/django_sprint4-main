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
        fields = ('first_name', 'last_name', 'username', 'email')


class PostForm(forms.ModelForm):
    """Форма для создания публикаций постов."""

    class Meta:
        model = Post
        exclude = (
            'author',
            'created_at',
            'updated_at'
        )
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
