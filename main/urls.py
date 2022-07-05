from django.urls import path

from main.views import Crawling

urlpatterns = [
    path('crawling', Crawling.as_view()),
]