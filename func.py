import logging
import re
from main.models import IpCount
from analysis.comment_list import commentList
from analysis.comment_analysis import commentAnalysis
from analysis.word_cloud import wordDict
from analysis.models import WordCloud, WordAnalysis, CommentAnalysis
import time


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
        IpCount.objects.create(ip=ip)

def background_func(video_id, userlog):
    #댓글 수집
    comment_detail_list = commentList(video_id)

    #워드 클라우드
    word_dict, comment_info_list = wordDict(
        comment_detail_list)  # 워드 클라우드 포함되는 문장

    word_colut_list = [WordCloud(
        user_log_idx=userlog, word=word, weight=weight) for weight, word in enumerate(word_dict)]
    WordCloud.objects.bulk_create(word_colut_list)

    

    # 문장 분석
    analysis_result = commentAnalysis(word_dict, comment_info_list)

    for key , value in analysis_result['word_analysis'].items():
        word_cloud = WordCloud.objects.get(user_log_idx = userlog.user_log_idx, word = key)
        
        positive_count = value['positive_count']
        negative_count = value['negetive_count']
        positive_proportion = positive_count/(positive_count+ negative_count)*100
        WordAnalysis.objects.create(word_cloud_idx= word_cloud, positive_proportion=positive_proportion, positive_count=positive_count, negative_count=negative_count)
        for positive_comment in value['positive_comment_list']: # 긍정 댓글 저장
            
            profile_img = positive_comment['comment_info']['profile_img']
            nickname = positive_comment['comment_info']['profile_name']
            comment = positive_comment['comment']
            sentence = positive_comment['sentence']
            positive = True
            CommentAnalysis.objects.create(word_cloud_idx= word_cloud, profile_img=profile_img, nickname=nickname, comment=comment, sentence=sentence, positive=positive)

        for negative_comment in value['negative_comment_list']: # 부정 댓글 저장
            
            profile_img = negative_comment['comment_info']['profile_img']
            nickname = negative_comment['comment_info']['profile_name']
            comment = negative_comment['comment']
            sentence = negative_comment['sentence']
            positive = False
            CommentAnalysis.objects.create(word_cloud_idx= word_cloud, profile_img=profile_img, nickname=nickname, comment=comment, sentence=sentence, positive=positive)

def test_check_func(video_id):
    result = {}
    start_time = time.time()  # 시간 측정
    comment_list = commentList(video_id)
    comment_list_time = time.time() - start_time
    print('댓글 리스트 수집: ', comment_list_time)
    result['댓글 개수'] = len(comment_list)
    start2_time = time.time()  # 시간 측정
    # word_dict, sentence_list = wordDictTest(comment_list)
    word_dict, comment_info_list = wordDict(
        comment_list)  # 워드 클라우드 포함되는 문장
    word_dict_time = time.time() - start2_time
    print('워드 클라우드 생성: ', word_dict_time)
    # result['기존 문장 개수'] = len(all_sentence_list)  # 임시 비교
    result['포함 문장 개수'] = len(comment_info_list)
    result['단어 개수'] = len(word_dict)
    start3_time = time.time()  # 시간 측정
    result = commentAnalysis(word_dict, comment_info_list)
    result_time = time.time() - start3_time
    print('키워드 긍정-부정 분석: ', result_time)
    result['time'] = {"댓글 수집": comment_list_time,
                        "워드 클라우드": word_dict_time, "키워드 분석": result_time}
    return result