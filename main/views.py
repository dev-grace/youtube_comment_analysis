from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from googleapiclient.errors import HttpError
import json
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from main.crawling import crawling

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

@permission_classes([AllowAny])
class ModelTest(APIView): # 합의 API
    def get(self, request):
        try:
            import tensorflow as tf
            import torch
            from transformers import DistilBertForSequenceClassification
            model_path = './saved_model/model.pb'
            model = DistilBertForSequenceClassification.from_pretrained('./analysis/model')
            # print(model)
            saved_model = torch.save(model.state_dict(), model_path)
            
            model = torch.load('./saved_model/model.pb')
            # print(model)

            # tf.saved_model.save(model.state_dict(), model_path)
            # model = tf.keras.models.load_model('D:/Users/qkrdm/treering/youtube_comment_analysis/saved_model')
            # print(model)
            # model.save('model.h5')
            # 파일로 저장되어 있는 모델을 load 한 뒤, TFLite 모델로 변환
            # model = DistilBertForSequenceClassification.from_pretrained('./analysis/model')
            # print(model)

            # 변수로 저장되어 있는 모델을, TFLite 모델로 변환
            # model_path = 'D:/Users/qkrdm/treering/youtube_comment_analysis/analysis/model'
            # print('시작')
            converter = tf.lite.TFLiteConverter.from_saved_model(model)
            # print('끝')

            # FP16 양자화 설정
            # converter.target_spec.supported_types = [tf.float16]
            # converter.optimizations = [tf.lite.Optimize.DEFAULT]

            # 모델 양자화
            tflite_model = converter.convert()

            # 변환된 모델을 .tflite 파일에 저장
            open("distilkobert.tflite", "wb").write(tflite_model)


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