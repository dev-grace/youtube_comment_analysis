from re import L
from django.db import models

class UserLog(models.Model):
    user_log_idx = models.BigAutoField(primary_key=True)
    ip = models.CharField(max_length=30,
                            null=True) #요청 ip
    target_url = models.CharField(max_length=300,
                            null=True) #요청 유튜브 url
    youtube_id = models.CharField(max_length=30,
                            null=True) #요청 유튜브 id
    date = models.DateTimeField(auto_now_add=True) # 요청일시

    class Meta:
            # managed = False
            db_table = 'user_log'

class IpCount(models.Model):
    ip_count_idx = models.BigAutoField(primary_key=True)
    ip = models.CharField(max_length=30,
                            null=True) # 요청 ip
    count = models.IntegerField(default=1) # ip 별 요청 수
    created_at = models.DateTimeField(auto_now_add=True) # 최초 요청 일시
    updated_at = models.DateTimeField(auto_now=True) # 최근 요청 일시

    class Meta:
            # managed = False
            db_table = 'ip_count'

class DailyUserCount(models.Model):
    daily_user_count_idx = models.BigAutoField(primary_key=True)
    daily_user_count = models.IntegerField()
    date = models.DateField()

    class Meta:
        # managed = False
        db_table = 'daily_user_count'
