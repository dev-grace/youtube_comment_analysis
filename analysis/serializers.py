from rest_framework import serializers
from analysis.models import WordCloud, WordAnalysis, CommentAnalysis

class WordCloudSerializer(serializers.ModelSerializer):
    text= serializers.ReadOnlyField()
    
    class Meta:
        model = WordCloud
        fields = ['text', 'weight']

class WordAnalysisSerializer(serializers.ModelSerializer):
    prefer_idx = serializers.ReadOnlyField()
    text= serializers.ReadOnlyField()
    val = serializers.ReadOnlyField()
    
    class Meta:
        model = WordAnalysis
        fields = ['prefer_idx', 'text', 'val']

class CommentAnalysisSerializer(serializers.ModelSerializer):
    cmt_idx = serializers.ReadOnlyField()
    
    class Meta:
        model = CommentAnalysis
        fields = ['cmt_idx', 'profile_img', 'comment', 'nickname', 'sentence']