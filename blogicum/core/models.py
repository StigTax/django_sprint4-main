from django.db import models


class PublishedMode(models.Model):
    """
    Абстрактная модель.

    Добавляет флаг is_published.
    """

    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )

    class Meta:
        abstract = True


class CreateMode(models.Model):
    """
    Абстрактная модель.

    Выводит информацию о дате и времени добавления поста.
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        abstract = True
