from kiwipiepy import Kiwi
import nltk
import torch
import numpy as np
import tensorflow as tf
import re
from transformers import BertTokenizer, BertTokenizerFast, TFBertForSequenceClassification, BertForSequenceClassification
from itertools import islice

# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')


def wordDictTest(comment_list): # 수정본(한글 댓글 추출)
    kiwi = Kiwi()
    stop_words_list = stopword()

    all_noun_list = []
    all_sentence_list = []
    
    for comment in comment_list:
        comment = re.sub('[^0-9가-힣\s]', '', comment['comment'])
        split_into_sents = kiwi.split_into_sents(comment, return_tokens=True)

        for split in split_into_sents:
            all_sentence_list.append(split.text)
            noun_list = [sent.form for sent in split.tokens if (sent.tag == 'NNG' or sent.tag == 'NNP') and sent.form not in stop_words_list]
            all_noun_list = all_noun_list + noun_list

    word_dict = wordCount(all_noun_list)

    sentence_list = [] # 워드 클라우드에 포함된 문장
    for sentence in all_sentence_list:
        if any(keyword in sentence for keyword in word_dict.keys()): # 문장이 워드 클라우드에 포함되는 지 확인
            sentence_list.append(sentence)
        else:
            continue

    return word_dict, sentence_list, all_sentence_list

def stopword(): # 불용어 처리
    korean_stopwords = open('./main/korean_stopwords.txt', 'r', encoding='utf-8')
    stop_words_list = []
    for line in korean_stopwords.readlines():
        stop_words_list.append(line.rstrip()) #공백 제거

    korean_stopwords.close()
    return stop_words_list

def wordCount(all_noun_list):
    word_count = {}

    for noun in all_noun_list:
        word_count[noun] = word_count.get(noun, 0) + 1

    # # 값이 3 이상인 것 내림차순 정렬
    # word_count = {key: value for key, value in word_count.items() if value >= 3}
    word_count = dict(sorted(word_count.items(), key=lambda x: x[1], reverse=True))
    
    if len(word_count) >=30: # max 값 30개
        word_count = dict(islice(word_count.items(), 30))
    return word_count