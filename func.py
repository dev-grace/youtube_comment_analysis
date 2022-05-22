import logging
import re
from main.models import IpCount

def dataCheck(data): #프론트에서 넘어오는 데이터 log 확인
    logger = logging.getLogger('django')
    logger.info(str(data))

def get_client_ip(request): # 클라이언트 ip 확인
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_video_url(url):
    url_re = re.compile('^.*(youtu.be\\/|v\\/|e\\/|u\\/\\w+\\/|embed\\/|v=)([^#\\&\\?]*).*')
    # video_id = url_re.match(url).group(2)

    if (url_re.match(url)) is None:
        return None
    else:
        return url_re.match(url).group(2)


def ip_count(ip):
    if IpCount.objects.filter(ip=ip).exists():
        user_ip = IpCount.objects.get(ip=ip)
        ip_count = user_ip.count
        user_ip.count = ip_count + 1
        user_ip.save()
    else:
        IpCount.objects.create(ip = ip)