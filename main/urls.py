from django.urls import path

from main.views import YoutubeAnalysis, YoutubeAnalysisTest, Crawling, Test

urlpatterns = [
    path('analysis', YoutubeAnalysis.as_view()),
    path('analysis_test', YoutubeAnalysisTest.as_view()),
    path('crawling', Crawling.as_view()),
    path('test', Test.as_view()),
]