# Generated by Django 3.2.16 on 2025-03-26 18:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0014_remove_comment_updated_at'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='post',
            new_name='post',
        ),
    ]
