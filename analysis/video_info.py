from googleapiclient.discovery import build
import my_settings

def videoInfo(video_id):
    api_key = my_settings.YOUTUBE_API_KEY
    api_obj = build('youtube', 'v3', developerKey=api_key)
    view_count = 0
    comment_count = 0

    video_id_response = api_obj.videos().list(part='statistics', id = video_id).execute() # 관련 영상 상세 정보

    if video_id_response['items']: # 상세 내용이 있으면
        video_count = video_id_response['items'][0]['statistics']

        view_count = int(video_count.get('viewCount', 1)) # 조회수: division by zero 막기 위해 없을 시, 1로 설정
        # like_count = int(video_count.get('likeCount', 0)) # 좋아요수
        comment_count = int(video_count.get('commentCount', 0)) # 댓글수

    
    return view_count, comment_count