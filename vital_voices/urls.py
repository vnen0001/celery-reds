from django.contrib import admin
from django.urls import path
from .views import GraphData,SpiderData

urlpatterns = [
    path('graph/', GraphData.as_view(),name='GraphData'),
     path('spider/', SpiderData.as_view(),name='SpiderData'),
]
