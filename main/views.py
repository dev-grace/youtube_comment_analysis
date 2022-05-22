from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from main.comment_list import commentList, commentListTest
from main.comment_analysis import commentAnalysis
from main.comment_analysis_test import commentAnalysisTest
from main.word_cloud import wordDict
from googleapiclient.errors import HttpError
from main.models import UserLog
import json
import time
from func import dataCheck, get_client_ip, get_video_url, ip_count


class YoutubeAnalysis(APIView): # 합의 API
    def post(self, request):
        try:
            data = json.loads(request.body)
            dataCheck(data)
            user_ip = get_client_ip(request)
            ip_count(user_ip)
            url = data['target_url']
            video_id = get_video_url(url)
            UserLog.objects.create(ip = user_ip, target_url = url, youtube_id = video_id)

            comment_list = commentList(video_id)
            result = commentAnalysis(comment_list)
            return Response(result, status=200)
        except HttpError:   #유튜브 링크 에러
            return Response({'message': 'URL_ERROR'}, status=404)
        except KeyError:
            return Response({'message': 'key wrong'}, status=402)
        except TypeError:
            return Response({'message': 'type wrong'}, status=403)
        except ValidationError:
            return Response({'message': 'VALIDATION_ERROR'}, status=404)

class YoutubeAnalysisTest(APIView): # 수정 테스트 API
    def post(self, request):
        try:
            data = json.loads(request.body)
            # dataCheck(data)
            # user_ip = get_client_ip(request)
            # ip_count(user_ip)
            url = data['target_url']
            video_id = get_video_url(url)
            # UserLog.objects.create(ip = user_ip, target_url = url, youtube_id = video_id)
            start_time = time.time() # 시간 측정
            comment_list = commentListTest(video_id)
            comment_list_time = time.time() - start_time
            print('댓글 리스트 수집: ', comment_list_time)
            start2_time = time.time() # 시간 측정
            word_dict = wordDict(comment_list)
            word_dict_time = time.time() - start2_time
            print('워드 클라우드 생성: ', word_dict_time)
            start3_time = time.time() # 시간 측정
            result = commentAnalysisTest(comment_list, word_dict)
            result_time = time.time() - start3_time
            print('키워드 긍정-부정 분석: ', result_time)
            result['time'] = [comment_list_time, word_dict_time, result_time]# 임시
            return Response(result, status=200)
        except HttpError:   #유튜브 링크 에러
            return Response({'message': 'URL_ERROR'}, status=404)
        except KeyError:
            return Response({'message': 'key wrong'}, status=402)
        except TypeError:
            return Response({'message': 'type wrong'}, status=403)
        except ValidationError:
            return Response({'message': 'VALIDATION_ERROR'}, status=404)

class Test(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            return Response(data, status=200)
        except KeyError:
            return Response({'message': 'key wrong'}, status=402)
        except TypeError:
            return Response({'message': 'type wrong'}, status=403)
        except ValidationError:
            return Response({'message': 'VALIDATION_ERROR'}, status=404)
