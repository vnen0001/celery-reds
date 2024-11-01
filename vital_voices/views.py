from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse, FileResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.hashers import check_password, make_password
from .utils import generate_token, verify_token
import json
from .tasks import process_suicide_data, fetch_parallel_coordinates_data, generate_speech,claude_response
from celery.result import AsyncResult
from django.core.cache import cache
from django_ratelimit.decorators import ratelimit
from django.http import FileResponse, HttpResponseNotFound
from django.core.files.storage import default_storage
import os
import re
import tiktoken
from  dotenv import load_dotenv
load_dotenv('cred.env')

CORRECT_HASHED_PASSWORD = make_password(os.environ.get('PASSWORD'))  # Generate this once and store it securely

@csrf_exempt
def verify(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            received_password = data.get('password')
            if received_password and check_password(received_password, CORRECT_HASHED_PASSWORD):
                return JsonResponse({'status': 'success'}, status=200)
            else:
                return JsonResponse({'status': 'error', 'message': 'Incorrect password'}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def verifiedtoken(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            token = data.get('token')
            if token:
                user_id = verify_token(token)
                if user_id:
                    return JsonResponse({'status': 'success'}, status=200)
            return JsonResponse({'status': 'error', 'message': 'Invalid token'}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

# @ratelimit(key='ip', rate='5/m',block= True)
class GraphData(APIView): 
    def get(self, request, format=None):
      
        include_expenditure = request.query_params.get('include_expenditure', 'false').lower() == 'true'
        cache_key = f'graph_data_{"with" if include_expenditure else "without"}_expenditure'
        result= cache.get(cache_key)
            
        if result is None:
            try:
                task = process_suicide_data.delay(include_expenditure)
                result = AsyncResult(task.id).get(timeout=60)  # 60 seconds timeout
                cache.set(cache_key, result, timeout=None)  # Cache for indefinetely
            except AsyncResult.TimeoutError:
                return Response({"error": "Processing is taking longer than expected. Please try again later."},
                                    status=status.HTTP_408_REQUEST_TIMEOUT)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        return JsonResponse(result, safe=False)

# @ratelimit(key='ip', rate='5/m',block= True)
class ParallelCoordinates(APIView):
    def get(self, request):
        result = cache.get('parallel_coordinates_data')
        if result is None:
            try:
                task = fetch_parallel_coordinates_data.delay()
                result = AsyncResult(task.id).get()  # 30 seconds timeout
                cache.set('parallel_coordinates_data',result,timeout=None)
                return JsonResponse(result, safe=False)
            except AsyncResult.TimeoutError:
                return Response({"error": "Processing is taking longer than expected. Please try again later."},
                                status=status.HTTP_408_REQUEST_TIMEOUT)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return JsonResponse(result,safe=False)

# @csrf_exempt
# @ratelimit(key='ip', rate='5/m',block= True)
# @require_http_methods(["POST"])
# def initiate_speech_generation(request):
#     try:
#         # Load JSON data from the request
#         data = json.loads(request.body.decode('utf-8'))
#         text = data.get('text')

#         if not text:
#             return JsonResponse({'status': 'error', 'message': 'No text provided'}, status=400)

#         # Trigger Celery task asynchronously
#         task = generate_speech.delay(text)

#         # Return task_id to track task progress
#         return JsonResponse({'status': 'success', 'task_id': task.id}, status=202)

#     except json.JSONDecodeError:
#         return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
#     except Exception as e:
#         return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
@csrf_exempt
@require_http_methods(["POST"])
def generate_and_download_speech(request, max_tokens=160):
    if request.method == 'POST':
        # Parse the incoming JSON request data
        data = json.loads(request.body.decode('utf-8'))
        text = data.get('text')
        enc = tiktoken.get_encoding("cl100k_base")

        if not text:
            return HttpResponseNotFound('No text provided')

        # Clean and preprocess the text
        text = re.sub(r'<[^>]+>', '', text)
        text = ' '.join(text.split())

        # Tokenize the text and truncate to the maximum number of tokens
        tokens = enc.encode(text)
        truncated_tokens = tokens[:max_tokens]
        cleaned_text = enc.decode(truncated_tokens)

        # Start the Celery task and wait for the result synchronously
        task = generate_speech.delay(cleaned_text)
        task_result = task.get(timeout=30)  # Wait for up to 30 seconds for the task to complete

        # Check if the task completed successfully and return the audio and viseme data
        if task_result and 'error' not in task_result:
            response = {
                'audio_data': task_result['audio_data'],
                'viseme_data': task_result['viseme_data']
            }
            return JsonResponse(response, status=200)
        else:
            return JsonResponse({'error': 'Failed to generate speech files'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

from django.core.cache import cache

def test_redis(request):
    try:
        # Try to set a value in Redis
        cache.set('test_key', 'test_value', 10)  # Cache for 10 seconds
        
        # Try to get the value back
        value = cache.get('test_key')
        
        if value == 'test_value':
            return JsonResponse({'status': 'success', 'message': 'Redis connection is working'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Failed to retrieve value from Redis'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
@csrf_exempt
@api_view(['POST'])
@ratelimit(key='ip', rate='5/m',block=True)
def vera_response(request):
   try:
        text = request.data.get('text')
        if not text:
            return Response({"error": "No text provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        task = claude_response.delay(text)
        result = AsyncResult(task.id).get()
        
        # Extract only the text content from the result
        content = result.get('content', [])
        text_blocks = [block.get('text', '') for block in content if block.get('type') == 'text']
        extracted_text = ' '.join(text_blocks)
        
        return Response({"response": extracted_text}, status=status.HTTP_200_OK)
   except AsyncResult.TimeoutError:
        return Response({"error": "Processing is taking longer than expected. Please try again later."},
                        status=status.HTTP_408_REQUEST_TIMEOUT)
   except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
