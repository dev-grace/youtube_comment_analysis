from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from googleapiclient.errors import HttpError
from main.models import UserLog
from rest_framework.decorators import permission_classes
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny
from drf_yasg import openapi
from func import dataCheck
from main.crawling import crawling
import threading

@permission_classes([AllowAny])
class Crawling(APIView): # 합의 API
    def get(self, request):
        try:
            video_info =crawling()
            return Response({'video_info': video_info}, status=200)
        except HttpError as e:   #유튜브 에러
            if "exceeded" in e.reason: # 유튜브 할당량 초과
                return Response({'message': 'QUOTA EXCEEDED'}, status=403)
            else: # 유튜브 링크 에러
                return Response({'message': 'URL_ERROR'}, status=401)
        except KeyError:
            return Response({'message': 'KEY WRONG'}, status=402)
        except TypeError:
            return Response({'message': 'TYPE WRONG'}, status=403)
        except ValidationError:
            return Response({'message': 'VALIDATION_ERROR'}, status=404)


class AnalysisStop(APIView):  # 분석 중지 요청 API
    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter('code', openapi.IN_QUERY, description="string", type=openapi.TYPE_STRING)],  responses={  # can use schema or text
            400: 'Analysis already stopped(이미 분석 정지 요청을 받은 경우)',
            401: 'CODE ERROR(요청식별코드가 잘못되었을 경우)',
            402: 'KEY WRONG',
            403: 'TYPE WRONG',
            404: 'ERROR(예상치 못한 에러)',
            500: 'SERVER ERROR'})
    def get(self, request):
        """
        분석 중지 요청 API
        ---
        # 내용
            code: 요청식별코드
        """
        try:
            data = request.GET.dict()
            dataCheck(data)
            code = data['code']
            result = {}
            result['code'] = code

            if UserLog.objects.filter(code=code).exists():
                user_log = UserLog.objects.get(code=code)
                if user_log.stop_analysis:
                    return Response({'message': 'Analysis already stopped'}, status=400)
                else:

                    ident = int(user_log.thread_ident)
                    thread = threading._active.get(ident)
                    thread_name = thread.name
                    if thread:
                        if thread.name == f'daemon {code}':
                            thread.stop_thread()
                            thread.join()

                    user_log.stop_analysis = True
                    user_log.save()
                        
                    return Response({'message': 'SUCCESS'}, status=200)

            else:
                return Response({'message': 'CODE_ERROR'}, status=401)

        except KeyError:
            return Response({'message': 'KEY WRONG'}, status=402)
        except TypeError:
            return Response({'message': 'TYPE WRONG'}, status=403)
        except: # 예상치 못한 에러
            return Response({'message': 'ERROR'}, status=404)



@permission_classes([AllowAny])
class ModelTest(APIView): # 합의 API
    def get(self, request):
        try:
            import tensorflow as tf
            import torch
            from transformers import TFDistilBertForSequenceClassification
            model_path = './analysis/saved_model'
            model = TFDistilBertForSequenceClassification.from_pretrained('./analysis/model', from_pt = True)

    

            # torch.save(model, model_path)    
            # saved_model = torch.load(model_path)

            tf.saved_model.save(model, model_path)
            # loaded = tf.saved_model.load("./saved_model")
            # loaded.eval()


            converter = tf.lite.TFLiteConverter.from_saved_model(model_path) # path to the SavedModel directory

            # FP16 양자화 설정
            converter.target_spec.supported_types = [tf.float16]
            converter.optimizations = [tf.lite.Optimize.DEFAULT]

            # 컨버터 설정
            converter.experimental_new_converter = True
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS, tf.lite.OpsSet.SELECT_TF_OPS]
            converter.allow_custom_ops=True

            # 모델 양자화
            tflite_model = converter.convert()
            

            # Save the model.
            open("./analysis/saved_model/saved_model.tflite", "wb").write(tflite_model)

            return Response({'message': 'SUCCESS'}, status=200)
        except HttpError as e:   #유튜브 에러
            if "exceeded" in e.reason: # 유튜브 할당량 초과
                return Response({'message': 'QUOTA EXCEEDED'}, status=403)
            else: # 유튜브 링크 에러
                return Response({'message': 'URL_ERROR'}, status=401)
        except KeyError:
            return Response({'message': 'KEY WRONG'}, status=402)
        except TypeError as e:
            print(e)
            return Response({'message': 'TYPE WRONG'}, status=403)
        except ValidationError:
            return Response({'message': 'VALIDATION_ERROR'}, status=404)