from django.urls import path, include

from . import views

"""
Конфигурация URL для приложения блога.

Определяет шаблоны URL для приложения блога со следующими маршрутами:

Основные маршруты:
- '' (index): Страница со всеми постами
- 'posts/<int:post_id>/': Страница с детальной информацией поста
- 'posts/create/': Страница создания поста
- 'posts/<int:post_id>/edit/': Страница редактирования поста
- 'posts/<int:post_id>/delete/': Страница удаления поста

Маршруты, связанные с комментариями:
- 'posts/<int:post_id>/comment/': страница создания комментария под постом
- 'posts/<int:post_id>/edit_comment/<int:comment_id>/': Страница редактирования
комментария
- 'posts/<int:post_id>/delete_comment/<int:comment_id>/': Страница удаления
комментария

Маршруты категорий и профиля:
- 'category/<slug:category_slug>/': Страница постов в определенной категории
- 'profile/<str:username>/': Страница профиля пользователя
- 'profile/edit/': Страница редактирования профиля пользователя

Все URL-адреса относятся к пространству имён 'blog' (app_name = 'blog').
При поиске обратного URL-адреса следует использовать это пространство имён,
например: 'blog:index'
"""

app_name = 'blog'

post_urlpatterns = [
    path('create/', views.PostCreateView.as_view(), name='create_post'),
    path('<int:post_id>/', views.PostDetailView.as_view(), name='post_detail'),
    path(
        '<int:post_id>/edit/',
        views.PostUpdateView.as_view(),
        name='edit_post'
    ),
    path(
        '<int:post_id>/delete/',
        views.PostDeleteView.as_view(),
        name='delete_post'
    ),
    path(
        '<int:post_id>/comment/',
        views.CommentCreateView.as_view(),
        name='add_comment'
    ),
    path('<int:post_id>/edit_comment/<int:comment_id>/',
         views.CommentUpdateView.as_view(), name='edit_comment'),
    path('<int:post_id>/delete_comment/<int:comment_id>/',
         views.CommentDeleteView.as_view(), name='delete_comment'),
]


urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path(
        'posts/',
        include(post_urlpatterns)
    ),
    path('category/<slug:category_slug>/',
         views.CategoryPostListView.as_view(), name='category_posts'),
    path(
        'profile/<str:username>/',
        views.ProfileView.as_view(),
        name='profile'
    ),
    path(
        'edit/',
        views.ProfileEditView.as_view(),
        name='edit_profile'
    ),
]
