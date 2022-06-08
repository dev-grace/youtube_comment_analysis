import pandas
from googleapiclient.discovery import build
import my_settings



def crawling():
    api_key = my_settings.YOUTUBE_API_KEY
    video_info = list()
    api_obj = build('youtube', 'v3', developerKey=api_key)

    random_id_list = ['mkRg_Yen9Wk','mY_3qwCd2gY', '95stSAizysE', 'xR2bheVpvaA', 'Kz8v7P1FAWM', 'MTscc8CfcZQ','fYncvJJfo-s', 'slSoLG18-gc', '7PGMNM9wKrA', 'DtFhWbWObC8'] # 임의 영상 리스트(일상(브이로그), 반려동물, 경제, 연예, 예능, 먹방, 자연, 음악, 예술, 스포츠)

    for random_id in random_id_list:
        response = api_obj.search().list(part='id', type = 'video', relatedToVideoId = random_id, maxResults=100).execute() #해당 영상 관련 영상 리스트
        # cnt =0
        # while response:
        #     cnt+=1
        item_len = len(response['items'])
        for i in range(item_len):
            video_id = response['items'][i]['id']['videoId'] # 영상ID
            video_id_response = api_obj.videos().list(part='snippet, statistics', id = video_id, maxResults=100).execute() # 관련 영상 상세 정보

            if video_id_response['items']: # 상세 내용이 있으면
                video_detail = video_id_response['items'][0]['snippet']
                video_count = video_id_response['items'][0]['statistics']

                title = video_detail['title'] # 영상제목
                view_count = int(video_count.get('viewCount', 1)) # 조회수: division by zero 막기 위해 없을 시, 1로 설정
                like_count = int(video_count.get('likeCount', 0)) # 좋아요수
                comment_count = int(video_count.get('commentCount', 0)) # 댓글수
                channel_id =  video_detail['channelId'] #채널ID
                channel_title = video_detail['channelTitle'] #채널명

                video_info.append([video_id, title, view_count, like_count, comment_count, channel_id, channel_title, comment_count/view_count*100, like_count/view_count*100])
            
            # if 'nextPageToken' in response:
            #     if cnt >=1:
            #         break
            #     response = api_obj.search().list(part='id', type = 'video', relatedToVideoId = random_id, pageToken=response['nextPageToken'], maxResults=100).execute()
            # else:
            #     break
    
    return video_info

# df = pandas.DataFrame(video_info) # 엑셀시트 저장
# df.to_csv('results.csv', header=['영상ID', '영상제목', '조회수', '좋아요수', '댓글수', '채널ID', '채널명', '댓글수/조회수(%)', '좋아요수/조회수(%)'], index=None, encoding='utf-8-sig')
  