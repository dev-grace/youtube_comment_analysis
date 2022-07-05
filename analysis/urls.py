from django.urls import path
from analysis.views import Test, YoutubeUrl, WordCloudView, ActiveInfoView, TopWordAnalysisView, WordAnalysisView, CommentAnalysisView

urlpatterns = [
    path('test', Test.as_view()),
    path('youtube_url', YoutubeUrl.as_view()),
    path('word_cloud', WordCloudView.as_view()),
    path('active_info', ActiveInfoView.as_view()),
    path('top_word_analysis', TopWordAnalysisView.as_view()),
    path('word_analysis', WordAnalysisView.as_view()),
    path('comment_analysis', CommentAnalysisView.as_view()),
]