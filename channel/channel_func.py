from googleapiclient.discovery import build
import my_settings

def channel_choice(video_id_list): # 함수 인자: 채널 video ID 리스트/ ex).['id_1', 'id_2', 'id_3']
    api_key = my_settings.YOUTUBE_API_KEY # youtube API key
    videos_id = video_id_list # 채널 video ID 리스트
    videos_reslut = list() # 최근 video ID 3개의 결과값 리스트
    api_obj = build('youtube', 'v3', developerKey=api_key) # youtube API 주소

    for video_id in videos_id:
        response = api_obj.videos().list(part='snippet, statistics', id = video_id, maxResults=100).execute() # 관련 영상 상세 정보

        if response['items']: # 상세 내용 확인
            video_detail = response['items'][0]['snippet']
            video_count = response['items'][0]['statistics']
            
            published_at = video_detail.get('publishedAt', None) # 영상 업로드 일시(필요하면 쓰세용)
            comment_count = int(video_count.get('commentCount', 0)) # 댓글 수
            print(published_at, comment_count)

            videos_reslut.append(comment_count >=50) # 댓글 50개 이상이면 True, 나머지는 False

    print(videos_reslut)
    return all(videos_reslut) # 리스트 결과값 모두 True일 때, True 리턴