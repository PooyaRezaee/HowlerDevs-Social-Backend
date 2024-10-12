# Generated by Django 5.0.8 on 2024-10-12 16:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Connection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_accept', models.BooleanField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reciver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='connect_recive', to=settings.AUTH_USER_MODEL)),
                ('requester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='connect_request', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Connection',
                'verbose_name_plural': 'Connections',
            },
        ),
    ]