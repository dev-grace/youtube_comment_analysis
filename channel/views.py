from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from googleapiclient.errors import HttpError
import json

from channel.channel_func import channel_choice


class ChannelChoice(APIView): # 합의 API
    def post(self, request):
        try:
            data = json.loads(request.body)
            video_id_list = data['video_id_list']
            result = channel_choice(video_id_list)
            return Response(result, status=200)
        except HttpError:   #유튜브 링크 에러
            return Response({'message': 'URL_ERROR'}, status=404)
        except KeyError:
            return Response({'message': 'key wrong'}, status=402)
        except TypeError:
            return Response({'message': 'type wrong'}, status=403)
        except ValidationError:
            return Response({'message': 'VALIDATION_ERROR'}, status=404)
