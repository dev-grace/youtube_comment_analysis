import torch
import numpy as np
import tensorflow as tf
from transformers import DistilBertForSequenceClassification
from main.tokenization_kobert import KoBertTokenizer
from keras.preprocessing.sequence import pad_sequences
import multiprocessing

# 모델 설정
device = torch.device('cpu') # gpu -> core gpu server -> ec2 gpu
model = DistilBertForSequenceClassification.from_pretrained('./main/model')
tokenizer =  KoBertTokenizer.from_pretrained('monologg/kobert', do_lower_case=False)


def analysis_func(comment_info):
    sentence_list = comment_info['sentence']
    sentence_positive_list = comment_info['sentence_positive']

    for sentence in sentence_list:
        logits = test_sentences([sentence])
        positive = int(np.argmax(logits))
        sentence_positive = {'sentence': sentence, 'positive': positive}
        sentence_positive_list.append(sentence_positive)
    
    return comment_info

#     {'word_cloud: : {},
# 'word_analysis':
# 'key': {
# 'positive': true, false, 
# 'positive_count': 10, 
# 'negetive_count': 20
# 'positive_comment_list': []
# 'negative_comment_list': []
# }, 
# }
def commentAnalysisTest(word_dict, comment_info_list): # 원본
    # 평가모드로 변경
    global model
    model.eval()

    word_analysis = {}
    set_word_list = word_dict.keys()
    for word in set_word_list: # 초기화 작업
        word_analysis[word] = {
            'positive': 0,
            'positive_proportion': 0,
            'positive_count': 0,
            'negetive_count':0,
            'positive_comment_list': [],
            'negative_comment_list':[]
            }
            
    # 멀티 프로세싱
    pool = multiprocessing.Pool(processes= 2)
    sentence_positive_list = list(pool.map(analysis_func, comment_info_list))
    pool.close()
    pool.join()


    for sentence_positive in sentence_positive_list:
        sentence_list = sentence_positive['sentence_positive']
        for sentence_item in sentence_list:
            sentence = sentence_item['sentence']
            positive = sentence_item['positive']
            if positive == 1: # 댓글이 긍정-부정인지 확인
                for word in word_dict.keys(): # 포함되는 키워드 확인
                    if word in sentence:
                        word_analysis[word]['positive_count'] += 1
                        word_analysis[word]['positive_comment_list'].append(sentence)
            else:
                for word in word_dict.keys():
                    if word in sentence:
                        word_analysis[word]['negetive_count'] += 1
                        word_analysis[word]['negative_comment_list'].append(sentence)
        
            
    for value in word_analysis.values():
        if value['positive_count'] > value['negetive_count']:
            value['positive'] = 1
        elif value['positive_count'] < value['negetive_count']:
            value['positive'] = -1

    result = {}
    result['word_cloud'] = word_dict
    result['word_analysis'] = word_analysis
    

    return result

# 입력 데이터 변환
def convert_input_data(sentences):
    global tokenizer

    # BERT의 토크나이저로 문장을 토큰으로 분리
    tokenized_texts = [tokenizer.tokenize(sent) for sent in sentences]

    # 입력 토큰의 최대 시퀀스 길이
    MAX_LEN = 128

    # 토큰을 숫자 인덱스로 변환
    input_ids = [tokenizer.convert_tokens_to_ids(x) for x in tokenized_texts]
    
    # 문장을 MAX_LEN 길이에 맞게 자르고, 모자란 부분을 패딩 0으로 채움
    input_ids = pad_sequences(input_ids, maxlen=MAX_LEN, dtype="long", truncating="post", padding="post")

    # 어텐션 마스크 초기화
    attention_masks = []

    # 어텐션 마스크를 패딩이 아니면 1, 패딩이면 0으로 설정
    # 패딩 부분은 BERT 모델에서 어텐션을 수행하지 않아 속도 향상
    for seq in input_ids:
        seq_mask = [float(i>0) for i in seq]
        attention_masks.append(seq_mask)

    # 데이터를 파이토치의 텐서로 변환
    inputs = torch.tensor(input_ids)
    masks = torch.tensor(attention_masks)

    return inputs, masks

# 문장 테스트
def test_sentences(sentences):
    global model, device
    # 문장을 입력 데이터로 변환
    inputs, masks = convert_input_data(sentences)

    # 데이터를 GPU에 넣음
    b_input_ids = inputs.to(device)
    b_input_mask = masks.to(device)
            
    # 그래디언트 계산 안함
    with torch.no_grad():     
        # Forward 수행
        outputs = model(b_input_ids, 
                        attention_mask=b_input_mask)
    # 로스 구함
    logits = outputs[0]

    # # CPU로 데이터 이동
    # logits = logits.detach().cpu().numpy()

    return logits