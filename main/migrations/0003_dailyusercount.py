# Generated by Django 3.2.8 on 2022-05-01 02:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_ipcount'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyUserCount',
            fields=[
                ('daily_user_count_idx', models.BigAutoField(primary_key=True, serialize=False)),
                ('daily_user_count', models.IntegerField()),
                ('date', models.DateField()),
            ],
            options={
                'db_table': 'daily_user_count',
            },
        ),
    ]
