from django.urls import path

from main.views import Crawling, AnalysisStop, ModelTest

urlpatterns = [
    # path('crawling', Crawling.as_view()),
    path('analysis_stop', AnalysisStop.as_view()),
    path('model_test', ModelTest.as_view()),
]