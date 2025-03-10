# Generated by Django 5.1.1 on 2024-11-22 15:25

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('idevelop', '0004_remove_student_following_student_friends_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CollabBox',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text_value', models.TextField(blank=True, null=True, verbose_name='Collaboration Text')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('allowed_editors', models.ManyToManyField(blank=True, related_name='editable_collab_boxes', to=settings.AUTH_USER_MODEL)),
                ('allowed_viewers', models.ManyToManyField(blank=True, related_name='viewable_collab_boxes', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_collab_boxes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
