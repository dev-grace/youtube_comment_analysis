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