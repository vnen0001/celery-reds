from django.contrib import admin
from django.urls import path
from .views import GraphData,SpiderData,PowerballSimulator_dj

urlpatterns = [
    path('graph/', GraphData.as_view(),name='GraphData'),
     path('spider/', SpiderData.as_view(),name='SpiderData'),
     path('powerbal',PowerballSimulator_dj.as_view(),name='Powerball')
]
