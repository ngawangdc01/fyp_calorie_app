# Generated by Django 5.0.7 on 2025-04-23 06:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0005_user_is_visible_in_leaderboard'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeightHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight_kg', models.FloatField()),
                ('recorded_at', models.DateField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-recorded_at'],
                'unique_together': {('user', 'recorded_at')},
            },
        ),
    ]
