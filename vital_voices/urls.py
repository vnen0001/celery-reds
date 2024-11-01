"""
URL configuration for vital_voices_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import (GraphData,ParallelCoordinates,generate_and_download_speech,verify,verifiedtoken,test_redis,vera_response,generate_and_download_speech)

urlpatterns = [
    path('verify/',verify,name='Password'),
    path('verify-token/', verifiedtoken, name='verifiedtoken'),
    path('graph/', GraphData.as_view(),name='GraphData'),
    #  path('spider/', SpiderData.as_view(),name='SpiderData'),
    #  path('powerbal/',PowerballSimulator_dj.as_view(),name='Powerball'),
      path('differentgames/',ParallelCoordinates.as_view(),name='ParallelCoordinates'),
      path('text_to_speech/',generate_and_download_speech,name='elevenlabs_text_to_speech'),
      path('test-redis/', test_redis, name='test_redis'),
      path('veraresponse/',vera_response,name='vera_response'),
      path('generate-and-download-speech/', generate_and_download_speech, name='generate_and_download_speech')

     ]
