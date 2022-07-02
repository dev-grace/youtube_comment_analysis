import pandas
from googleapiclient.discovery import build
from main.models import UserLog
import my_settings

def commentList(video_id): # 테스트
    api_key = my_settings.YOUTUBE_API_KEY  
    comment_list = list()
    api_obj = build('youtube', 'v3', developerKey=api_key)
    response = api_obj.commentThreads().list(part='snippet,replies', videoId=video_id, maxResults=100).execute()

    
    while response:
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comment_list.append({"profile_img": comment["authorProfileImageUrl"], "profile_name": comment['authorDisplayName'], "sentence": [], "sentence_positive": [], "comment": comment['textOriginal'], 
            "comment_idx": 0, "datetime": comment['publishedAt']})
    
            # if item['snippet']['totalReplyCount'] > 0: # 대댓글 분석
            #     for reply_item in item['replies']['comments']:
            #         reply = reply_item['snippet']
            #         comment_list.append([reply['textDisplay'], reply['authorDisplayName'], reply['publishedAt'], reply['likeCount']])
    
        if 'nextPageToken' in response:
            response = api_obj.commentThreads().list(part='snippet,replies', videoId=video_id, pageToken=response['nextPageToken'], maxResults=100).execute()
        else:
            break
    
    # df = pandas.DataFrame(comments) # 엑셀시트 저장
    # df.to_excel('results.xlsx', header=['comment', 'author', 'date', 'num_likes'], index=None)
    return comment_list

def commentListTest(video_id): # 테스트
    api_key = my_settings.YOUTUBE_API_KEY  
    comment_list = list()
    api_obj = build('youtube', 'v3', developerKey=api_key)
    response = api_obj.commentThreads().list(part='snippet,replies', videoId=video_id, maxResults=100).execute()

    
    while response:
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comment_list.append({"profile_img": comment["authorProfileImageUrl"], "nickname": comment['authorDisplayName'], "comment": comment['textOriginal'], "sentence": [],"datetime": comment['publishedAt']})
    
            # if item['snippet']['totalReplyCount'] > 0: # 대댓글 분석
            #     for reply_item in item['replies']['comments']:
            #         reply = reply_item['snippet']
            #         comment_list.append([reply['textDisplay'], reply['authorDisplayName'], reply['publishedAt'], reply['likeCount']])
    
        if 'nextPageToken' in response:
            response = api_obj.commentThreads().list(part='snippet,replies', videoId=video_id, pageToken=response['nextPageToken'], maxResults=100).execute()
        else:
            break
    
    return comment_list