from django.contrib import admin
from main.models import DailyUserCount, UserLog, IpCount, DailyUserCount
import sys


@admin.register(UserLog)
class FunnelInfoAdmin(admin.ModelAdmin):
    list_display = [field.name for field in UserLog._meta.fields if field.name != "user_log_idx"]
    list_per_page = sys.maxsize

@admin.register(IpCount)
class FunnelInfoAdmin(admin.ModelAdmin):
    list_display = [field.name for field in IpCount._meta.fields if field.name != "ip_count_idx"]
    list_per_page = sys.maxsize

@admin.register(DailyUserCount)
class FunnelInfoAdmin(admin.ModelAdmin):
    list_display = [field.name for field in DailyUserCount._meta.fields if field.name != "daily_user_count_idx"]
    list_per_page = sys.maxsize