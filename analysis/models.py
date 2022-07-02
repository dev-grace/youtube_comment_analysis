from django.db import models

class WordCloud(models.Model):
    word_cloud_idx = models.BigAutoField(primary_key=True)
    user_log_idx = models.ForeignKey(
        'main.UserLog',
        related_name='word_cloud_user_log_idx',
        on_delete=models.RESTRICT,
        db_column='user_log_idx'
    )   #요청식별id
    word = models.CharField(max_length=100) # 단어
    weight = models.IntegerField(default=0) # 단어 개수

    class Meta:
            # managed = False
            db_table = 'word_cloud'


class ActiveInfo(models.Model):
    active_info_idx = models.BigAutoField(primary_key=True)
    user_log_idx = models.ForeignKey(
        'main.UserLog',
        related_name='active_info_user_log_idx',
        on_delete=models.RESTRICT,
        db_column='user_log_idx'
    )   #요청식별id
    active_proportion = models.FloatField(default=0) # 적극적 사용자 비율
    comment_count = models.IntegerField(default=0) #댓글수
    view_count = models.IntegerField(default=0) # 조회수

    class Meta:
            # managed = False
            db_table = 'active_info'


class WordAnalysis(models.Model):
    word_analysis_idx = models.BigAutoField(primary_key=True)
    word_cloud_idx = models.ForeignKey(
        'analysis.WordCloud',
        related_name='word_analysis_word_cloud',
        on_delete=models.RESTRICT,
        db_column='word_cloud_idx'
    )   #요청식별코드
    positive_proportion = models.FloatField(default=0) # 긍정비율
    positive_count = models.IntegerField(default=0) #긍정문장 수
    negative_count = models.IntegerField(default=0) # 부정문장 수

    class Meta:
            # managed = False
            db_table = 'word_analysis'

class CommentAnalysis(models.Model):
    comment_analysis_idx = models.BigAutoField(primary_key=True)
    word_cloud_idx = models.ForeignKey(
        'analysis.WordCloud',
        related_name='comment_analysis_word_cloud',
        on_delete=models.RESTRICT,
        db_column='word_cloud_idx'
    )   #요청식별코드
    profile_img = models.CharField(max_length=300,
                            null=True) #이미지 url
    nickname = models.CharField(max_length=100, null = True) # 닉네임
    comment = models.CharField(max_length=100) # 댓글
    sentence = models.CharField(max_length=1000) # 문장
    positive = models.BooleanField(default = True) # 긍정여부


    class Meta:
            # managed = False
            db_table = 'comment_analysis'
