# Generated by Django 3.2.8 on 2022-07-05 11:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DailyUserCount',
            fields=[
                ('daily_user_count_idx', models.BigAutoField(primary_key=True, serialize=False)),
                ('daily_user_count', models.IntegerField(default=0)),
                ('date', models.DateField(auto_now_add=True)),
            ],
            options={
                'db_table': 'daily_user_count',
            },
        ),
        migrations.CreateModel(
            name='IpCount',
            fields=[
                ('ip_count_idx', models.BigAutoField(primary_key=True, serialize=False)),
                ('ip', models.CharField(max_length=30)),
                ('count', models.IntegerField(default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'ip_count',
            },
        ),
        migrations.CreateModel(
            name='UserLog',
            fields=[
                ('user_log_idx', models.BigAutoField(primary_key=True, serialize=False)),
                ('code', models.CharField(default='', max_length=20, unique=True)),
                ('ip', models.CharField(max_length=30, null=True)),
                ('target_url', models.CharField(max_length=300)),
                ('youtube_id', models.CharField(max_length=30, null=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'user_log',
            },
        ),
        migrations.CreateModel(
            name='RequestStatus',
            fields=[
                ('request_status_idx', models.BigAutoField(primary_key=True, serialize=False)),
                ('active_info_status', models.BooleanField(default=False)),
                ('word_cloud_status', models.BooleanField(default=False)),
                ('top_word_analysis_status', models.BooleanField(default=False)),
                ('word_analysis_status', models.BooleanField(default=False)),
                ('user_log_idx', models.ForeignKey(db_column='user_log_idx', on_delete=django.db.models.deletion.RESTRICT, related_name='request_status_user_log_idx', to='main.userlog')),
            ],
            options={
                'db_table': 'request_status',
            },
        ),
    ]
