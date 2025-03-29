from django.urls import path
from django.views.generic import TemplateView

"""
Здесь содержатся маршруты приложения pages.

Маршруты:
1. Путь 'about/':
    - Вызывает функцию views.about.
    - Используется для отображения страницы "О сайте".

2. Путь 'rules/':
    - Вызывает функцию views.rules.
    - Используется для отображения страницы "Правила".

"""

app_name = 'pages'

urlpatterns = [
    path('about/', TemplateView.as_view(template_name='pages/about.html'),
         name='about'),
    path('rules/', TemplateView.as_view(template_name='pages/rules.html'),
         name='rules'),
]
