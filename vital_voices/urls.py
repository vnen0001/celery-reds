from django.contrib import admin
from django.urls import path
from .views import GraphData,SpiderData,PowerballSimulator_dj,ParallelCoordinates,verify

urlpatterns = [
    path('verify/',verify,name='Password'),
    path('graph/', GraphData.as_view(),name='GraphData'),
     path('spider/', SpiderData.as_view(),name='SpiderData'),
     path('powerbal/',PowerballSimulator_dj.as_view(),name='Powerball'),
      path('differentgames/',ParallelCoordinates.as_view(),name='ParallelCoordinates')
     ]