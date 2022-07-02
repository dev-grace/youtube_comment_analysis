from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from main.comment_list import commentList, commentListTest
from main.comment_analysis import commentAnalysis
from main.comment_analysis_test import commentAnalysisTest
from main.word_cloud_test import wordDict, wordDictTest
from googleapiclient.errors import HttpError
from django.http import HttpResponse
from main.models import UserLog
from analysis.models import WordCloud
import json
import secrets
import time
from main.crawling import crawling
from func import dataCheck, get_client_ip, get_video_url, ip_count
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import JsonResponse


@permission_classes([AllowAny])
class Test(APIView):  # 수정 테스트 API
    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter('target_url', openapi.IN_QUERY, description="string", type=openapi.TYPE_STRING)],  responses={  # can use schema or text
            400: 'this is a test description.',
            500: 'this is a test description.'})
    def get(self, request):
        try:
            data = request.GET.dict()
            result = {}
            target_url = data['target_url']
            # dataCheck(data)
            # user_ip = get_client_ip(request)
            # ip_count(user_ip)
            video_id = get_video_url(target_url)
            # UserLog.objects.create(ip = user_ip, target_url = url, youtube_id = video_id)
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
            result = commentAnalysisTest(word_dict, comment_info_list)
            result_time = time.time() - start3_time
            print('키워드 긍정-부정 분석: ', result_time)
            result['time'] = {"댓글 수집": comment_list_time,
                              "워드 클라우드": word_dict_time, "키워드 분석": result_time}  # 임시
            return JsonResponse(result, status=200)
        except HttpError:  # 유튜브 링크 에러
            return Response({'message': 'URL_ERROR'}, status=404)
        except KeyError:
            return Response({'message': 'key wrong'}, status=402)
        except TypeError:
            return Response({'message': 'type wrong'}, status=403)
        except ValidationError:
            return Response({'message': 'VALIDATION_ERROR'}, status=404)


@permission_classes([AllowAny])
class YoutubeUrl(APIView):  # 수정 테스트 API
    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter('target_url', openapi.IN_QUERY, description="string", type=openapi.TYPE_STRING)],  responses={  # can use schema or text
            400: 'this is a test description.',
            500: 'this is a test description.'})
    def get(self, request):
        """
        URL 전송 API
        ---
        # 내용
            target_url : 유튜브 주소
        # 반환
            code: 요청식별코드
        """
        try:
            data = request.GET.dict()
            dataCheck(data)
            user_ip = get_client_ip(request)
            ip_count(user_ip)

            target_url = data['target_url']

            video_id = get_video_url(target_url)

            while True:
                code = str(secrets.token_hex(10))
                if not UserLog.objects.filter(code=code).exists():
                    break

            userlog = UserLog.objects.create(code=code, ip=user_ip,
                                             target_url=target_url, youtube_id=video_id)

            #댓글 수집
            comment_detail_list = commentList(video_id)

            #워드 클라우드
            word_dict, comment_info_list = wordDict(
                comment_detail_list)  # 워드 클라우드 포함되는 문장

            word_colut_list = [WordCloud(
                user_log_idx=userlog, word=word, weight=weight) for weight, word in enumerate(word_dict)]
            WordCloud.objects.bulk_create(word_colut_list)

           

            # 문장 분석
            analysis_result = commentAnalysisTest(word_dict, comment_info_list)
            print(analysis_result)

            result = {'code': code}

            return JsonResponse(result, status=200)
        except HttpError:  # 유튜브 링크 에러
            return Response({'message': 'URL_ERROR'}, status=404)
        except KeyError:
            return Response({'message': 'key wrong'}, status=402)
        except TypeError:
            return Response({'message': 'type wrong'}, status=403)
        except ValidationError:
            return Response({'message': 'VALIDATION_ERROR'}, status=404)


@permission_classes([AllowAny])
class WordCloudView(APIView):  # 워드 클라우드 API
    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter('code', openapi.IN_QUERY, description="string", type=openapi.TYPE_STRING)],  responses={  # can use schema or text
            400: 'this is a test description.',
            500: 'this is a test description.'})
    def get(self, request):
        """
        워드 클라우드 API
        ---
        # 내용
            code : 요청식별코드
        """
        try:
            data = request.GET.dict()
            code = data['code']
            # comment_list = commentListTest('aPoGBJrZryI')
            # word_dict, sentence_list, all_sentence_list = wordDictTest(code, comment_list) #임시 비교 위한 전체 문장리스트

            result = {}
            result['code'] = '0473904e48aaa9ab3959'
            result['data'] = [
                {
                    'weight': 164,
                    'text': '삐루'
                },
                {
                    'weight': 130,
                    'text': '영상'
                },
                {
                    'weight': 125,
                    'text': '수빈'
                },
                {
                    'weight': 82,
                    'text': '가족'
                },
                {
                    'weight': 77,
                    'text': '행복'
                },
                {
                    'weight': 47,
                    'text': '언니'
                },
                {
                    'weight': 42,
                    'text': '오늘'
                },
                {
                    'weight': 39,
                    'text': '사랑'
                },
                {
                    'weight': 37,
                    'text': '응원'
                },
                {
                    'weight': 37,
                    'text': '건강'
                },
                {
                    'weight': 32,
                    'text': '감사'
                },
                {
                    'weight': 28,
                    'text': '뼈'
                },
                {
                    'weight': 27,
                    'text': '할머니'
                },
                {
                    'weight': 24,
                    'text': '용'
                },
                {
                    'weight': 23,
                    'text': '집'
                },
                {
                    'weight': 22,
                    'text': '엄마'
                },
                {
                    'weight': 22,
                    'text': '사람'
                },
                {
                    'weight': 21,
                    'text': '모습'
                },
                {
                    'weight': 20,
                    'text': '모자'
                },
                {
                    'weight': 20,
                    'text': '덤홀덤'
                },
                {
                    'weight': 20,
                    'text': '기분'
                },
                {
                    'weight': 20,
                    'text': '마음'
                },
                {
                    'weight': 19,
                    'text': '전'
                },
                {
                    'weight': 18,
                    'text': '손목'
                },
                {
                    'weight': 18,
                    'text': '어머님'
                },
                {
                    'weight': 17,
                    'text': '힐링'
                },
                {
                    'weight': 17,
                    'text': '하루'
                },
                {
                    'weight': 16,
                    'text': '발음'
                },
                {
                    'weight': 15,
                    'text': '신경'
                },
                {
                    'weight': 15,
                    'text': '조심'
                },
            ]

            return JsonResponse(result, status=200)
        except HttpError:  # 유튜브 링크 에러
            return Response({'message': 'URL_ERROR'}, status=404)
        except KeyError:
            return Response({'message': 'key wrong'}, status=402)
        except TypeError:
            return Response({'message': 'type wrong'}, status=403)
        except ValidationError:
            return Response({'message': 'VALIDATION_ERROR'}, status=404)


class ActiveInfoView(APIView):  # 조회수 대비 적극시청자 API
    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter('code', openapi.IN_QUERY, description="string", type=openapi.TYPE_STRING)],  responses={  # can use schema or text
            400: 'this is a test description.',
            500: 'this is a test description.'})
    def get(self, request):
        """
        조회수 대비 적극시청자 API
        ---
        # 내용
            code: 요청식별코드
        # 반환
            active_num : 적극 시청자 비율(float)
        """
        try:
            data = request.GET.dict()
            code = data['code']
            # comment_list = commentListTest('aPoGBJrZryI')
            # word_dict, sentence_list, all_sentence_list = wordDictTest(code, comment_list) #임시 비교 위한 전체 문장리스트

            comment_count = 574
            view_count = 287894

            result = {}
            result['code'] = '0473904e48aaa9ab3959'
            result['active_num'] = comment_count/view_count

            return JsonResponse(result, status=200)
        except HttpError:  # 유튜브 링크 에러
            return Response({'message': 'URL_ERROR'}, status=404)
        except KeyError:
            return Response({'message': 'key wrong'}, status=402)
        except TypeError:
            return Response({'message': 'type wrong'}, status=403)
        except ValidationError:
            return Response({'message': 'VALIDATION_ERROR'}, status=404)


@permission_classes([AllowAny])
class WordAnalysisView(APIView):  # 단어 분석 API

    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter('code', openapi.IN_QUERY, description="string", type=openapi.TYPE_STRING)],  responses={  # can use schema or text
            400: 'this is a test description.',
            500: 'this is a test description.'})
    def get(self, request):
        """
        단어 분석 API
        ---
        # 내용
            code : 요청 식별 코드
        """
        try:
            data = request.GET.dict()
            code = data['code']
            # comment_list = commentListTest('aPoGBJrZryI')
            # word_dict, sentence_list, all_sentence_list = wordDictTest(code, comment_list) #임시 비교 위한 전체 문장리스트

            result = {}
            result['code'] = '0473904e48aaa9ab3959'
            result['prefer_list'] = [
                {
                    'prefer_idx': 1,
                    'text': '삐루',
                    'val': 0.80
                },
                {
                    'prefer_idx': 2,
                    'text': '영상',
                    'val': 0.30
                },
                {
                    'prefer_idx': 3,
                    'text': '수빈',
                    'val': 0.67
                },
                {
                    'prefer_idx': 4,
                    'text': '가족',
                    'val': 0.70
                },
                {
                    'prefer_idx': 5,
                    'text': '행복',
                    'val': 0.73
                },
                {
                    'prefer_idx': 6,
                    'text': '언니',
                    'val': 0.55
                },
                {
                    'prefer_idx': 7,
                    'text': '오늘',
                    'val': 0.52
                },
                {
                    'prefer_idx': 8,
                    'text': '사랑',
                    'val': 0.30
                },
                {
                    'prefer_idx': 9,
                    'text': '응원',
                    'val': 0.90
                },
                {
                    'prefer_idx': 10,
                    'text': '건강',
                    'val': 0.53
                },
                {
                    'prefer_idx': 11,
                    'text': '감사',
                    'val': 0.40
                },
                {
                    'prefer_idx': 12,
                    'text': '뼈',
                    'val': 0.28
                },
                {
                    'prefer_idx': 13,
                    'text': '할머니',
                    'val': 0.90
                },
                {
                    'prefer_idx': 14,
                    'text': '용',
                    'val': 0.10
                }
            ]
            return JsonResponse(result, status=200)
        except HttpError:  # 유튜브 링크 에러
            return Response({'message': 'URL_ERROR'}, status=404)
        except KeyError:
            return Response({'message': 'key wrong'}, status=402)
        except TypeError:
            return Response({'message': 'type wrong'}, status=403)
        except ValidationError:
            return Response({'message': 'VALIDATION_ERROR'}, status=404)


@permission_classes([AllowAny])
class CommentAnalysisView(APIView):  # 단어별 댓글 분석 API
    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter('prefer_idx', openapi.IN_QUERY, description="int", type=openapi.TYPE_INTEGER)],  responses={  # can use schema or text
            400: 'this is a test description.',
            500: 'this is a test description.'})
    def get(self, request):
        """
        단어별 댓글 분석 API
        ---
        # 내용
            prefer_idx : 단어 고유 ID
        """
        try:
            prefer_idx = request.GET.get('prefer_idx', None)
            # comment_list = commentListTest('aPoGBJrZryI')
            # word_dict, sentence_list, all_sentence_list = wordDictTest(code, comment_list) #임시 비교 위한 전체 문장리스트

            result = {}
            result['prefer'] = {}
            result['prefer']['prefer_idx'] = prefer_idx
            result['prefer']['text'] = '행복'
            result['prefer']['val'] = 0.73
            result['pos_cnt'] = 4
            result['neg_cnt'] = 2
            result['pos_cmt'] = [
                {
                    'cmt_idx': 1,
                    'profile_img': 'https://kr.object.ncloudstorage.com/mazzi/public_data/util/logo.png',
                    'comment': '패스룸 고양이샴푸  삐루 사용해도 되요',
                    'nickname': '닉네임1',
                    'sentence': '패스룸 고양이샴푸  삐루 사용해도 되요',
                },
                {
                    'cmt_idx': 2,
                    'profile_img': 'https://kr.object.ncloudstorage.com/mazzi/public_data/util/logo.png',
                    'comment': '삐루 너무 귀엽다',
                    'nickname': '닉네임2',
                    'sentence': '삐루 너무 귀엽다~! 삐루빼로님도 꼭 루게릭병을 극복하는 모습을 멋지게 보여줬으면 좋겠습니다',
                },
                {
                    'cmt_idx': 3,
                    'profile_img': 'https://kr.object.ncloudstorage.com/mazzi/public_data/util/logo.png',
                    'comment': '삐루는 날이갈수록 귀여워지네요',
                    'nickname': '닉네임3',
                    'sentence': '삐루는 날이갈수록 귀여워지네요 아 삐루 삐진 거 귀여워서 또 보러 왓거든여  영상 다시보는데 간식먹자 하니깐 삐진 와중에 귀 잠깐 쫑끗 하는 거 넘나 욱겨요 귀는 어쩔 수가 없나봐여',
                },
                {
                    'cmt_idx': 4,
                    'profile_img': 'https://kr.object.ncloudstorage.com/mazzi/public_data/util/logo.png',
                    'comment': '삐루 마지막에 \n화분이되고싶은가봉가',
                    'nickname': '닉네임4',
                    'sentence': '삐루 마지막에 \n화분이되고싶은가봉가',
                },
            ]
            result['neg_cmt'] = [
                {
                    'cmt_idx': 5,
                    'profile_img': 'https://kr.object.ncloudstorage.com/mazzi/public_data/util/logo.png',
                    'comment': '삐루 너무귀엽다고',
                    'nickname': '닉네임5',
                    'sentence': '삐루 너무귀엽다고',
                },
                {
                    'cmt_idx': 6,
                    'profile_img': 'https://kr.object.ncloudstorage.com/mazzi/public_data/util/logo.png',
                    'comment': '신경쓰이는 재질 박삐루',
                    'nickname': '닉네임6',
                    'sentence': '신경쓰이는 재질 박삐루 종종 멍때리다보면 저도 모르게 삐루삐루삐루이러고 있어여',
                },
            ]

            return JsonResponse(result, status=200)
        except HttpError:  # 유튜브 링크 에러
            return Response({'message': 'URL_ERROR'}, status=404)
        except KeyError:
            return Response({'message': 'key wrong'}, status=402)
        except TypeError:
            return Response({'message': 'type wrong'}, status=403)
        except ValidationError:
            return Response({'message': 'VALIDATION_ERROR'}, status=404)
