# Generated by Django 5.0.8 on 2024-10-25 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('connect', '0002_rename_reciver_connection_receiver_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='connection',
            name='is_accept',
            field=models.BooleanField(db_index=True),
        ),
    ]
