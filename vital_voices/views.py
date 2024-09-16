from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse, FileResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password, make_password
from .utils import generate_token, verify_token
import json
from .tasks import process_suicide_data, fetch_parallel_coordinates_data, generate_speech
from celery.result import AsyncResult

CORRECT_HASHED_PASSWORD = make_password("tp35fit5120")  # Generate this once and store it securely

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

class GraphData(APIView):
    def get(self, request, format=None):
        try:
            include_expenditure = request.query_params.get('include_expenditure', 'false').lower() == 'true'
            task = process_suicide_data.delay(include_expenditure)
            result = AsyncResult(task.id).get()  # 60 seconds timeout
            return JsonResponse(result, safe=False)
        except AsyncResult.TimeoutError:
            return Response({"error": "Processing is taking longer than expected. Please try again later."},
                            status=status.HTTP_408_REQUEST_TIMEOUT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class SpiderData(APIView):
#     def get(self, request, format=None):
#         try:
#             task = fetch_spider_data.delay()
#             result = AsyncResult(task.id).get(timeout=30)  # 30 seconds timeout
#             return JsonResponse(result, safe=False)
#         except AsyncResult.TimeoutError:
#             return Response({"error": "Processing is taking longer than expected. Please try again later."},
#                             status=status.HTTP_408_REQUEST_TIMEOUT)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class PowerballSimulator_dj(APIView):
#     def get(self, request):
#         max_tickets = int(request.GET.get('max_tickets', 1000))
#         task = simulate_powerball.delay(max_tickets)
#         result = AsyncResult(task.id).get(timeout=30)  # 30 seconds timeout
#         return JsonResponse(result)

class ParallelCoordinates(APIView):
    def get(self, request):
        try:
            task = fetch_parallel_coordinates_data.delay()
            result = AsyncResult(task.id).get()  # 30 seconds timeout
            return JsonResponse(result, safe=False)
        except AsyncResult.TimeoutError:
            return Response({"error": "Processing is taking longer than expected. Please try again later."},
                            status=status.HTTP_408_REQUEST_TIMEOUT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
def elevenlabs_text_to_speech(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        text = data.get('text')
        
        if not text:
            return JsonResponse({'status': 'error', 'message': 'No text provided'}, status=400)

        task = generate_speech.delay(text)
        print(task)
        result = AsyncResult(task.id).get(timeout=60) 
        print(result) # 60 seconds timeout

        response = HttpResponse(result, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="audio_package.zip"'
        return response

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
    except AsyncResult.TimeoutError:
        return JsonResponse({'status': 'error', 'message': 'Speech generation is taking longer than expected. Please try again later.'}, status=408)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
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