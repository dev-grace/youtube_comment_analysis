from kiwipiepy import Kiwi
from itertools import islice


# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')


def wordDict(comment_detail_list): # 수정본(한글 댓글 추출)
    kiwi = Kiwi()
    stop_words_list = stopword()

    all_noun_list = []
    
    for comment_detail in comment_detail_list:
        comment = comment_detail['comment']
        sentence_list = comment_detail['sentence']
        # comment = re.sub('[^0-9가-힣\s]', '', comment_detail['comment'])
        split_into_sents = kiwi.split_into_sents(comment, return_tokens=True)

        for split in split_into_sents:
            sentence_list.append(split.text)

            noun_list = [sent.form for sent in split.tokens if (sent.tag == 'NNG' or sent.tag == 'NNP') and sent.form not in stop_words_list]
            all_noun_list = all_noun_list + noun_list

    word_dict = wordCount(all_noun_list)

    for comment_detail in comment_detail_list:
        sentence_list = comment_detail['sentence']
        for sentence in sentence_list:
            if any(keyword in sentence for keyword in word_dict.keys()): # 문장이 워드 클라우드에 포함되는 지 확인
                continue
            else:
                sentence_list.remove(sentence)

        if len(sentence_list) == 0:
            comment_detail_list.remove(comment_detail)

    # for word, weight in word_dict:
    #     code = UserLog.objects.get(code=code).code
    #     WordCloud.objects.create(code=code, word = word, weight=weight)

    return word_dict, comment_detail_list

def stopword(): # 불용어 처리
    korean_stopwords = open('./analysis/korean_stopwords.txt', 'r', encoding='utf-8')
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