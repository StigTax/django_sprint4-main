from django.contrib.auth.mixins import LoginRequiredMixin
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


def get_post_queryset(apply_filters=False, annotate_comments=False):
    queryset = Post.objects.select_related(
        'author',
        'category',
        'location'
    )

    if apply_filters:
        queryset = queryset.filter(
            is_published=True,
            pub_date__lte=now(),
            category__is_published=True
        )

    if annotate_comments:
        queryset = queryset.annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')

    return queryset


class PostListView(ListView):
    template_name = 'blog/index.html'
    context_object_name = 'page_obj'
    paginate_by = POSTS_PER_PAGE
    queryset = get_post_queryset(
        apply_filters=True,
        annotate_comments=True
    ).order_by('-pub_date')


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return get_post_queryset().select_related(
            'author',
            'category',
            'location'
        )

    def get_object(self, queryset=None):
        post = get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs['post_id']
        )
        if (post.author != self.request.user
            and (not post.is_published
                 or not post.category.is_published
                 or post.pub_date > now())):
            raise Http404('Этот пост недоступен.')
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = (
            Comment.objects
            .filter(post_id=self.object.id)
            .select_related('author')
            .order_by('created_at')
        )
        context['form'] = CommentForm()
        return context


class CategoryPostListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'page_obj'
    paginate_by = POSTS_PER_PAGE

    def get_category(self):
        return get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )

    def get_queryset(self):
        category = self.get_category()
        queryset = get_post_queryset(
            apply_filters=True,
            annotate_comments=True
        ).filter(
            category=category
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context


class ProfileView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_profile_user(self):
        return get_object_or_404(
            User,
            username=self.kwargs['username']
        )

    def get_queryset(self):
        profile_user = self.get_profile_user()
        if self.request.user == profile_user:
            queryset = get_post_queryset(
                apply_filters=False,
                annotate_comments=True
            )
        else:
            queryset = get_post_queryset(
                apply_filters=True,
                annotate_comments=True
            )
        return queryset.filter(author=profile_user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_profile_user()
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
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


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        if post.author != request.user:
            return HttpResponseRedirect(
                reverse_lazy(
                    'blog:post_detail',
                    kwargs={'post_id': self.kwargs['post_id']}
                )
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        if post.author != request.user:
            return HttpResponseRedirect(
                reverse_lazy(
                    'blog:post_detail',
                    kwargs={'post_id': self.kwargs['post_id']}
                )
            )
        return super().dispatch(request, *args, **kwargs)

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
        form.instance.post = get_object_or_404(
            Post,
            id=self.kwargs['post_id']
        )
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        return get_object_or_404(
            Comment.objects.filter(
                post_id=self.kwargs['post_id']
            ),
            pk=self.kwargs['comment_id']
        )

    def form_valid(self, form):
        form.instance.post = get_object_or_404(Post, id=self.kwargs['post_id'])
        form.instance.author = self.request.user
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != request.user:
            return HttpResponseRedirect(
                reverse_lazy(
                    'blog:post_detail',
                    kwargs={'post_id': self.kwargs['post_id']}
                )
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        return get_object_or_404(
            Comment.objects.filter(
                post_id=self.kwargs['post_id']
            ),
            pk=self.kwargs['comment_id']
        )

    def dispatch(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != request.user:
            return HttpResponseRedirect(
                reverse_lazy(
                    'blog:post_detail',
                    kwargs={'post_id': self.kwargs['post_id']}
                )
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )
