from konlpy.tag import Okt
import nltk
import torch
import numpy as np
import tensorflow as tf
import re
from transformers import BertTokenizer, BertTokenizerFast, TFBertForSequenceClassification, BertForSequenceClassification
import multiprocessing
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')


def wordDict(comment_list): # 수정본(한글 댓글 추출)
    okt = Okt()
    all_noun_list = []
    stop_words_list = stopword()
    
    for comment in comment_list:
        comment = re.sub('[^0-9가-힣\s]', '', comment['comment'])

        noun_list = [sent for sent in okt.nouns(comment) if sent not in stop_words_list]
        all_noun_list = all_noun_list + noun_list

    word_dict = wordCount(all_noun_list)
    return word_dict

def stopword(): # 불용어 처리
    korean_stopwords = open('./main/korean_stopwords.txt', 'r', encoding='utf-8')
    stop_words_list = []
    for line in korean_stopwords.readlines():
        stop_words_list.append(line.rstrip()) #공백 제거

    korean_stopwords.close()
    return stop_words_list

# def wordDict(comment_list): # 프로세싱 테스트
#     all_noun_list = []
#     pool = multiprocessing.Pool(processes= 5)
#     all_noun_list = list(pool.map(test, comment_list))
#     pool.close()
#     pool.join()
#     print(all_noun_list)
#     word_dict = wordCount(all_noun_list)
#     return word_dict

# def wordDict(comment_list): #원본
#     okt = Okt()
#     all_noun_list = []

#     for comment in comment_list:
#         language = isEnglishOrKorean(comment['comment']) # 댓글 언어 분석
#         comment = re.sub('[^A-Za-z0-9가-힣\s]', '', comment['comment'])

#         # 언어에 따라 다른 형태소 분석기 사용
#         if language == "korean":
#             noun_list = [sent for sent in okt.nouns(comment) if len(sent) >=2] # 두 글자 이상의 명사 추출
#         else:
#             is_noun = lambda pos: pos[:2] =="NN"
#             tokenized = nltk.word_tokenize(comment)
#             noun_list = [sent for (sent, pos) in nltk.pos_tag(tokenized) if is_noun(pos)]

#         all_noun_list = all_noun_list + noun_list

#     word_dict = wordCount(all_noun_list)
#     return word_dict

# def isEnglishOrKorean(comment): #한/영 댓글 구분
#     k_count = len(re.sub('[^가-힣]', '', comment))
#     e_count = len(re.sub('[^-a-zA-Z]', '', comment))
#     return "korean" if k_count>e_count else "english"

def wordCount(all_noun_list):
    word_count = {}

    for noun in all_noun_list:
        word_count[noun] = word_count.get(noun, 0) + 1

    # # 값이 3 이상인 것 내림차순 정렬
    word_count = {key: value for key, value in word_count.items() if value >= 3}
    word_count = dict(sorted(word_count.items(), key=lambda x: x[1], reverse=True))

    # word_list = word_count[:10]
    # print(word_list)
    return word_count