from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from main.comment_list import commentList, commentListTest
from main.comment_analysis import commentAnalysis
from main.comment_analysis_test import commentAnalysisTest
from main.word_cloud_test import wordDictTest
from googleapiclient.errors import HttpError
from django.http import HttpResponse
from main.models import UserLog
import json
import csv
import time
from main.crawling import crawling
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
            # word_dict, sentence_list = wordDictTest(comment_list)
            word_dict, sentence_list, all_sentence_list = wordDictTest(comment_list) #임시 비교 위한 전체 문장리스트
            word_dict_time = time.time() - start2_time
            print('워드 클라우드 생성: ', word_dict_time)
            result = {}
            start3_time = time.time() # 시간 측정
            result = commentAnalysisTest(word_dict, sentence_list)
            result_time = time.time() - start3_time
            print('키워드 긍정-부정 분석: ', result_time)
            result['time'] = {"댓글 수집": comment_list_time, "워드 클라우드": word_dict_time, "키워드 분석": result_time} # 임시
            result['댓글 개수'] = len(comment_list)
            result['기존 문장 개수'] = len(all_sentence_list) #임시 비교
            result['포함 문장 개수'] = len(sentence_list)
            result['단어 개수'] = len(word_dict)
            return Response(result, status=200)
        except HttpError:   #유튜브 링크 에러
            return Response({'message': 'URL_ERROR'}, status=404)
        except KeyError:
            return Response({'message': 'key wrong'}, status=402)
        except TypeError:
            return Response({'message': 'type wrong'}, status=403)
        except ValidationError:
            return Response({'message': 'VALIDATION_ERROR'}, status=404)

class Crawling(APIView):
    def get(self, request):
        data = crawling()
        response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="results.csv"'},
        )
        response.write(u'\ufeff'.encode('utf-8-sig'))
        writer = csv.writer(response)
        writer.writerow(['영상ID', '영상제목', '조회수', '좋아요수', '댓글수', '채널ID', '채널명', '댓글수/조회수(%)', '좋아요수/조회수(%)'])
        writer.writerows(data)
        
        return response

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
