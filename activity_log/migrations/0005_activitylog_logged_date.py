# Generated by Django 5.0.7 on 2025-04-21 06:34

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activity_log', '0004_activitylog_weight_kg'),
    ]

    operations = [
        migrations.AddField(
            model_name='activitylog',
            name='logged_date',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
