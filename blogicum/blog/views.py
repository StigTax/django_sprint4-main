from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.shortcuts import HttpResponseRedirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import Http404
from django.db.models import Count

from blog.forms import EditUserForm, PostForm, CommentForm
from blog.models import Post, Category, Comment

"""
Модуль views.py для блога.

Содержит представления (views) для работы с постами, комментариями,
категориями и профилями пользователей.

Основные классы представлений:

1. PostListView - Список всех опубликованных постов (главная страница)
2. PostDetailView - Детальная страница поста с комментариями
3. CategoryPostListView - Список постов по категориям
4. ProfileView - Профиль пользователя с его постами
5. ProfileEditView - Редактирование профиля

CRUD-операции для постов:
- PostCreateView - Создание поста
- PostUpdateView - Редактирование поста
- PostDeleteView - Удаление поста

CRUD-операции для комментариев:
- CommentCreateView - Создание комментария
- CommentUpdateView - Редактирование комментария
- CommentDeleteView - Удаление комментария

Вспомогательные функции:
- get_base_post_queryset() - Базовый QuerySet для получения
опубликованных постов
  с фильтрацией по дате публикации и статусу категории

Настройки:
- POSTS_PER_PAGE = 10 - Количество постов на странице при пагинации

Миксины:
- LoginRequiredMixin - Проверка аутентификации пользователя
- UserPassesTestMixin - Проверка прав доступа

Особенности:
- Для неаутентифицированных пользователей показываются только
опубликованные посты
- Авторы могут видеть и редактировать свои неопубликованные посты
- Комментарии могут редактировать/удалять только их авторы
- Редактировать профиль может только владелец профиля
- Все QuerySet'ы оптимизированы с помощью select_related и annotate

Шаблоны:
- blog/index.html - Главная страница
- blog/detail.html - Страница поста
- blog/category.html - Посты по категории
- blog/profile.html - Профиль пользователя
- blog/create.html - Создание/редактирование поста
- blog/comment.html - Создание/редактирование комментария
- blog/user.html - Редактирование профиля
"""


POSTS_PER_PAGE = 10


def get_base_post_queryset():
    return Post.objects.select_related(
        'author',
        'category',
        'location'
    ).filter(
        is_published=True,
        pub_date__lte=now(),
        category__is_published=True
    )


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'page_obj'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        username = self.kwargs.get('username')
        if username:
            user = get_object_or_404(User, username=username)
            queryset = Post.objects.filter(author=user).order_by('-pub_date')
        else:
            queryset = get_base_post_queryset().order_by('-pub_date')

        queryset = queryset.annotate(
            comment_count=Count('comments')
        )
        return queryset


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            return queryset.filter(is_published=True)
        return queryset

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        if not post.is_published and post.author != self.request.user:
            print(
                f'Отказ в доступе - is_published: {post.is_published}, '
                f'author: {post.author}, request user: {self.request.user}'
            )
            raise Http404("Этот пост недоступен.")
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        context['comments'] = Comment.objects.filter(
            post__id=self.object.id
        )
        context['form'] = CommentForm(initial={'post': post.id})
        return context


class CategoryPostListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'page_obj'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        category = get_object_or_404(
            Category, slug=self.kwargs['category_slug'], is_published=True
        )
        queryset = get_base_post_queryset().filter(
            category=category).order_by('-pub_date')
        if not (self.request.user.is_authenticated
                or not self.request.user.is_staff):
            queryset = queryset.filter(is_published=True)

        queryset = queryset.annotate(
            comment_count=Count('comments')
        )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category, slug=self.kwargs['category_slug'], is_published=True)
        return context


class ProfileView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        self.profile = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        queryset = Post.objects.filter(
            author=self.profile
        ).order_by('-pub_date')

        if self.request.user != self.profile:
            queryset = queryset.filter(
                is_published=True,
                pub_date__lte=now(),
                category__is_published=True
            )

        return queryset.select_related(
            'author',
            'category',
            'location'
        ).annotate(
            comment_count=Count('comments')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile
        context['is_owner'] = (self.request.user == self.profile)
        context['username'] = self.profile.username
        return context


class ProfileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = EditUserForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )

    def test_func(self):
        user = self.get_object()
        return self.request.user == user


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        self.object = form.save()
        return HttpResponseRedirect(
            reverse_lazy(
                'blog:profile',
                kwargs={'username': self.request.user.username}
            )
        )


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        if form.instance.author != self.request.user:
            return HttpResponseRedirect(
                reverse_lazy(
                    'blog:post_detail',
                    kwargs={'post_id': self.kwargs.get('post_id')}
                )
            )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.object.id}
        )


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        form.instance.post = post
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.object.post.id}
        )


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'post_id'

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.object.post.id}
        )


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={
                'post_id': self.object.post.id
            }
        )
