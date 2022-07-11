from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from googleapiclient.errors import HttpError
from analysis.models import WordCloud, ActiveInfo, WordAnalysis, CommentAnalysis
from analysis.serializers import WordCloudSerializer, WordAnalysisSerializer, CommentAnalysisSerializer
from main.models import UserLog, RequestStatus
import secrets
from func import dataCheck, get_client_ip, get_video_url, ip_count, test_check_func, defalut_func, background_func
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
import threading
from time import sleep


# 개선 방안
# 임의 쿼리날릴 수 있는 api 생성( 프로그래스 바 생성)/ db 데이터 기반 진행상황 체크/db 접근제한
@permission_classes([AllowAny])
class Test(APIView):  # 수정 테스트 API
    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter('target_url', openapi.IN_QUERY, description="string", type=openapi.TYPE_STRING)],  responses={  # can use schema or text
            401: 'URL ERROR(URL이 잘못되거나 비공개 영상일 경우)',
            402: 'KEY WRONG',
            403: 'TYPE WRONG',
            404: 'ERROR(예상치 못한 에러)',
            500: 'SERVER ERROR'})
    def get(self, request):
        try:
            data = request.GET.dict()
            target_url = data['target_url']
            video_id = get_video_url(target_url)

            result = test_check_func(video_id)

            return JsonResponse(result, status=200)
        except HttpError:  # 유튜브 링크 에러
            return Response({'message': 'URL ERROR'}, status=401)
        except KeyError:
            return Response({'message': 'KEY WRONG'}, status=402)
        except TypeError:
            return Response({'message': 'TYPE WRONG'}, status=403)
        except: # 예상치 못한 에러
            return Response({'message': 'ERROR'}, status=404)


@permission_classes([AllowAny])
class YoutubeUrl(APIView):  # 수정 테스트 API
    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter('target_url', openapi.IN_QUERY, description="string", type=openapi.TYPE_STRING)],  responses={  # can use schema or text
            400: 'ANALYSIS FAIL(영상 댓글 50개 이하인 경우)',
            401: 'URL ERROR(URL이 잘못되거나 비공개 영상일 경우)',
            402: 'KEY WRONG',
            403: 'TYPE WRONG',
            403: 'QUOTA EXCEEDED(유튜브 할당량 초과)',
            404: 'ERROR(예상치 못한 에러)',
            500: 'SERVER ERROR'})
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

            
            request_status, comment_detail_list, comment_count = defalut_func(video_id, userlog)
            
            if comment_count < 50:
                return Response({'message': 'ANALYSIS FAIL'}, status=400)
            else:
                thread = threading.Thread(target = background_func, args = (userlog, request_status, comment_detail_list))
                thread.start()
                    
                result = {'code': code}

                return JsonResponse(result, status=200)
        except HttpError as e:   #유튜브 에러
            if "exceeded" in e.reason: # 유튜브 할당량 초과
                return Response({'message': 'QUOTA EXCEEDED'}, status=403)
            else: # 유튜브 링크 에러
                return Response({'message': 'URL_ERROR'}, status=401)
        except KeyError:
            return Response({'message': 'KEY WRONG'}, status=402)
        except TypeError:
            return Response({'message': 'TYPE WRONG'}, status=403)
        except: # 예상치 못한 에러
            return Response({'message': 'ERROR'}, status=404)


@permission_classes([AllowAny])
class WordCloudView(APIView):  # 워드 클라우드 API
    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter('code', openapi.IN_QUERY, description="string", type=openapi.TYPE_STRING)],  responses={  # can use schema or text
            401: 'CODE ERROR(code(요청식별코드)가 잘못되었을 경우)',
            402: 'KEY WRONG',
            403: 'TYPE WRONG',
            404: 'ERROR(예상치 못한 에러)',
            500: 'SERVER ERROR'})
    def get(self, request):
        """
        워드 클라우드 API
        ---
        # 내용
            code : 요청식별코드
        """
        try:
            data = request.GET.dict()
            dataCheck(data)
            code = data['code']
            result = {}
            result['code'] = code


            if UserLog.objects.filter(code=code).exists():
                user_log = UserLog.objects.get(code=code)
               
                while True:
                    request_status = RequestStatus.objects.get(user_log_idx= user_log.user_log_idx)
                    if request_status.word_cloud_status:
                        word_cloud_list = WordCloud.objects.filter(user_log_idx= user_log.user_log_idx) # 정렬된 순서
                        serializer = WordCloudSerializer(word_cloud_list, many=True)
                        result['data'] = serializer.data
                        return JsonResponse(result, status=200)
                    sleep(1)

            else:
                return Response({'message': 'CODE ERROR'}, status=401)

        except KeyError:
            return Response({'message': 'KEY WRONG'}, status=402)
        except TypeError:
            return Response({'message': 'TYPE WRONG'}, status=403)
        except: # 예상치 못한 에러
            return Response({'message': 'ERROR'}, status=404)


class ActiveInfoView(APIView):  # 조회수 대비 적극시청자 API
    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter('code', openapi.IN_QUERY, description="string", type=openapi.TYPE_STRING)],  responses={  # can use schema or text
            400: 'ActiveInfo Not Found(적극 시청자 정보가 없을 경우)',
            401: 'CODE ERROR(요청식별코드가 잘못되었을 경우)',
            402: 'KEY WRONG',
            403: 'TYPE WRONG',
            404: 'ERROR(예상치 못한 에러)',
            500: 'SERVER ERROR'})
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
            dataCheck(data)
            code = data['code']
            result = {}
            result['code'] = code

            if UserLog.objects.filter(code=code).exists():
                user_log = UserLog.objects.get(code=code)
               
                while True:
                    request_status = RequestStatus.objects.get(user_log_idx= user_log.user_log_idx)
                    if request_status.active_info_status:
                        if ActiveInfo.objects.filter(user_log_idx= user_log.user_log_idx):
                            active_info = ActiveInfo.objects.get(user_log_idx= user_log.user_log_idx)
                            result['active_num'] = active_info.active_proportion
                            return JsonResponse(result, status=200)
                        else:
                            return Response({'message': 'ActiveInfo Not Found'}, status=400)
                    sleep(1)

            else:
                return Response({'message': 'CODE_ERROR'}, status=401)

        except KeyError:
            return Response({'message': 'KEY WRONG'}, status=402)
        except TypeError:
            return Response({'message': 'TYPE WRONG'}, status=403)
        except: # 예상치 못한 에러
            return Response({'message': 'ERROR'}, status=404)

@permission_classes([AllowAny])
class TopWordAnalysisView(APIView):  # 단어 분석 API

    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter('code', openapi.IN_QUERY, description="string", type=openapi.TYPE_STRING)],  responses={  # can use schema or text
            400: 'WordCloud Not Found(워드클라우드 정보가 없을 경우)',
            401: 'CODE ERROR(요청식별코드가 잘못되었을 경우)',
            402: 'KEY WRONG',
            403: 'TYPE WRONG',
            404: 'ERROR(예상치 못한 에러)',
            500: 'SERVER ERROR'})
    def get(self, request):
        """
        단어 분석 API
        ---
        # 내용
            code : 요청 식별 코드
        """
        try:
            data = request.GET.dict()
            dataCheck(data)
            code = data['code']

            result = {}
            result['code'] = code

            if UserLog.objects.filter(code=code).exists():
                user_log = UserLog.objects.get(code=code)
               
                while True:
                    request_status = RequestStatus.objects.get(user_log_idx= user_log.user_log_idx)
                    if request_status.top_word_analysis_status:
                        if WordCloud.objects.filter(user_log_idx=user_log.user_log_idx).exists():
                            word_cloud_list = WordCloud.objects.filter(user_log_idx=user_log.user_log_idx)
                            if len(WordAnalysis.objects.filter(word_cloud_idx__in= word_cloud_list)) >= 4:
                                word_analysis_list = WordAnalysis.objects.filter(word_cloud_idx__in= word_cloud_list)[:4]
                            else:
                                word_analysis_list = WordAnalysis.objects.filter(word_cloud_idx__in= word_cloud_list)
                            serializer = WordAnalysisSerializer(word_analysis_list, many=True)
                            result['prefer_list'] = serializer.data
                            return JsonResponse(result, status=200)
                        else:
                            return Response({'message': 'WordCloud Not Found'}, status=400)
                    sleep(1)

            else:
                return Response({'message': 'CODE_ERROR'}, status=401)

        except KeyError:
            return Response({'message': 'KEY WRONG'}, status=402)
        except TypeError:
            return Response({'message': 'TYPE WRONG'}, status=403)
        except: # 예상치 못한 에러
            return Response({'message': 'ERROR'}, status=404)


@permission_classes([AllowAny])
class WordAnalysisView(APIView):  # 단어 분석 API
    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter('code', openapi.IN_QUERY, description="string", type=openapi.TYPE_STRING)],  responses={  # can use schema or text
            400: 'WordCloud Not Found(워드클라우드 정보가 없을 경우)',
            401: 'CODE ERROR(요청식별코드가 잘못되었을 경우)',
            402: 'KEY WRONG',
            403: 'TYPE WRONG',
            404: 'ERROR(예상치 못한 에러)',
            500: 'SERVER ERROR'})
    def get(self, request):
        """
        단어 분석 API
        ---
        # 내용
            code : 요청 식별 코드
        """
        try:
            data = request.GET.dict()
            dataCheck(data)
            code = data['code']

            result = {}
            result['code'] = code


            if UserLog.objects.filter(code=code).exists():
                user_log = UserLog.objects.get(code=code)
               
                while True:
                    request_status = RequestStatus.objects.get(user_log_idx= user_log.user_log_idx)
                    if request_status.word_analysis_status:
                        if WordCloud.objects.filter(user_log_idx=user_log.user_log_idx).exists():
                            word_cloud_list = WordCloud.objects.filter(user_log_idx=user_log.user_log_idx)
                            word_analysis_list = WordAnalysis.objects.filter(word_cloud_idx__in= word_cloud_list)
                            serializer = WordAnalysisSerializer(word_analysis_list, many=True)
                            result['prefer_list'] = serializer.data
                            return JsonResponse(result, status=200)
                        else:
                            return Response({'message': 'WordCloud Not Found'}, status=400)
                    sleep(1)

            else:
                return Response({'message': 'CODE_ERROR'}, status=401)

        except KeyError:
            return Response({'message': 'KEY WRONG'}, status=402)
        except TypeError:
            return Response({'message': 'TYPE WRONG'}, status=403)
        except: # 예상치 못한 에러
            return Response({'message': 'ERROR'}, status=404)

@permission_classes([AllowAny])
class CommentAnalysisView(APIView):  # 단어별 댓글 분석 API
    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter('prefer_idx', openapi.IN_QUERY, description="int", type=openapi.TYPE_INTEGER)],  responses={  # can use schema or text
            401: 'PREFER_IDX_ERROR(prefer_idx가 잘못되거나 분석이 끝나지 않은 경우)',
            402: 'KEY WRONG',
            403: 'TYPE WRONG',
            404: 'ERROR(예상치 못한 에러)',
            500: 'SERVER ERROR'})
    def get(self, request):
        """
        단어별 댓글 분석 API
        ---
        # 내용
            prefer_idx : 단어 고유 ID
        """
        try:
            prefer_idx = request.GET.get('prefer_idx', None)
            dataCheck(prefer_idx)

            result = {}

            if WordAnalysis.objects.filter(word_cloud_idx=prefer_idx).exists():
                prefer = WordAnalysis.objects.get(word_cloud_idx=prefer_idx)
                serializer = WordAnalysisSerializer(prefer)
                result['prefer'] = serializer.data
                result['pos_cnt'] = prefer.positive_count
                result['neg_cnt'] = prefer.negative_count
                pos_comment_list = CommentAnalysis.objects.filter(word_cloud_idx=prefer_idx, positive = True)
                neg_comment_list = CommentAnalysis.objects.filter(word_cloud_idx=prefer_idx, positive = False)
                positive_serializer = CommentAnalysisSerializer(pos_comment_list, many=True)
                negative_serializer = CommentAnalysisSerializer(neg_comment_list, many=True)
                result['pos_cmt'] = positive_serializer.data
                result['neg_cmt'] = negative_serializer.data
                return JsonResponse(result, status=200)
    
            else:
                return Response({'message': 'PREFER_IDX_ERROR'}, status=401)
                   
        except KeyError:
            return Response({'message': 'KEY WRONG'}, status=402)
        except TypeError:
            return Response({'message': 'TYPE WRONG'}, status=403)
        except: # 예상치 못한 에러
            return Response({'message': 'ERROR'}, status=404)
