import os
import uuid
import tempfile
import io
import zipfile
import subprocess
from celery import shared_task,chain
from django.db import connections
import azure.cognitiveservices.speech as speechsdk
from django.conf import settings
import logging
from dotenv import load_dotenv
from django.core.cache import cache
import logging
import anthropic

load_dotenv('vital_voices_project/cred.env')

logger = logging.getLogger(__name__)

anthropic_client = anthropic.Anthropic(
     api_key= os.environ.get('CLAUDE_KEY')
)

prompt = """You are an AI assistant specialized in providing factual, balanced information about gambling and offering tips for responsible gambling and addiction prevention.
 Your responses should be informative, non-judgmental, and focused on harm reduction.
   Follow these guidelines:\n\nProvide accurate, research-based information about gambling, including its risks and potential consequences.\nEmphasize responsible gambling practices and strategies for maintaining control.
   \nOffer practical tips and techniques for preventing gambling addiction.
   \nWhen discussing addiction, be compassionate and encourage seeking professional help.
   \nAvoid glorifying gambling or downplaying its risks.\nDon't provide specific gambling strategies or tips for winning.
   \nInclude statistics and facts from reputable sources within Australia when relevant.
   \nSuggest alternatives to gambling for entertainment or stress relief.
   \nExplain common cognitive biases and misconceptions related to gambling.
   \nProvide information about self-exclusion programs and other resources for those struggling with gambling.
   \nDiscuss the importance of financial literacy and budgeting in relation to gambling.
   \nBe prepared to explain different types of gambling and their associated risks.
   \nOffer age-appropriate information if the user specifies they are educating young people.
   \nEncourage open communication about gambling within families and communities.
   \nProvide information about the legal aspects of gambling, including age restrictions and regulations.
   \n\nRemember to maintain a balanced, educational tone throughout your responses. 
   Your goal is to inform and promote responsible decision-making, not to preach or moralize.
     The answer should be short and concise and should not exceed more than 150 tokens and you should moderate any foul language and conversation should not go off topic"""

@shared_task()
def process_suicide_data(include_expenditure):
    cache_key = f'suicide_data_{"with" if include_expenditure else "without"}_expenditure'
    
    # Try to get the data from cache
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result
    query = """
    SELECT s.Gender, s.Year, SUM(s.Suicide_Number) AS total
    {expenditure_join}
    FROM dbo.suicide_number_data s
    {expenditure_clause}
    GROUP BY s.Gender, s.Year {group_by_expenditure}
    ORDER BY s.Year, s.Gender
    """
    
    expenditure_join = ", t.Aust AS total_expenditure" if include_expenditure else ""
    expenditure_clause = """
    LEFT JOIN (
        SELECT LEFT(Financial_Year, 4) AS Year, Aust
        FROM DBO.Total_expenditure
    ) t ON s.Year = t.Year
    """ if include_expenditure else ""
    group_by_expenditure = ", t.Aust" if include_expenditure else ""

    query = query.format(
        expenditure_join=expenditure_join,
        expenditure_clause=expenditure_clause,
        group_by_expenditure=group_by_expenditure
    )
    logger.info(query)
    with connections['default'].cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    logger.info(rows)
    years = sorted(set(row[1] for row in rows))
    result = []

    for year in years:
        year_data = {'year': str(year), 'Male': 0, 'Female': 0}
        if include_expenditure:
            year_data['total_expenditure'] = 'N/A'
        
        for row in rows:
            if row[1] == year:
                gender, _, suicide_number, *rest = row
                year_data[gender] = suicide_number
                if include_expenditure and rest:
                    year_data['total_expenditure'] = rest[0] if rest[0] is not None else 'N/A'
        
        result.append(year_data)
    cache.set(cache_key, result, timeout=None)
    
    return result

@shared_task
def fetch_parallel_coordinates_data():
     
    cache_key = 'parallel_coordinates_data'
    
    # Try to get the data from cache
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data
    
    with connections['default'].cursor() as cursor:
        cursor.execute("select * from [dbo].[Different_games_expenditure]")
        rows = cursor.fetchall()
        data = []
        for row in rows:
             data.append({
                 'Year': row[0],
                 'Casino': row[1],
                 'Gaming_machine': row[2],
                 'Interactive_gaming': row[3],
                 'Keno': row[4],
                 'Lotteries': row[5],
                 'Minor_gaming': row[6],
                 'Wagering': row[7],
                'Total': row[8]
            })
    cache.set(cache_key, data, timeout=None)

def create_temp_files():
    temp_dir = tempfile.gettempdir()
    return {
        'wav': os.path.join(temp_dir, f"{uuid.uuid4()}.wav"),
        'json': os.path.join(temp_dir, f"{uuid.uuid4()}.json")
    }

@shared_task
def generate_speech(text):
    file_paths = create_temp_files()

    try:
        azure_ai_key = str(os.environ.get("AZURE_AI_KEY"))
        azure_region = str(os.environ.get("AZURE_AI_REGION"))
        if not azure_ai_key or not azure_region:
            logger.error("Azure credentials not found in environment variables")
            return {"error": "Azure credentials not found"}

        # Set up Azure Speech SDK configuration
        speech_config = speechsdk.SpeechConfig(subscription=azure_ai_key, region=azure_region)
        speech_config.speech_synthesis_voice_name = "en-US-AriaNeural"
        audio_config = speechsdk.audio.AudioOutputConfig(filename=file_paths['wav'])
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        # List to store viseme data
        viseme_data = []

        # Callback to handle viseme events
        def viseme_callback(evt):
            viseme_data.append({
                "audio_offset": evt.audio_offset,
                "viseme_id": evt.viseme_id
            })
            logger.info(f'Viseme event received: Viseme ID = {evt.viseme_id}, Audio Offset = {evt.audio_offset}')

        # Connect the viseme callback to the synthesizer
        synthesizer.viseme_received.connect(viseme_callback)

        # Perform the text-to-speech conversion
        result = synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            logger.info(f"Speech synthesized successfully for text: [{text}]")
            
            # Read the audio file data
            with open(file_paths['wav'], 'rb') as audio_file:
                audio_data = audio_file.read()

            # Return the audio data and viseme data as JSON
            response = {
                'audio_data': audio_data.decode('latin1'),  # Encoding for JSON compatibility
                'viseme_data': viseme_data
            }

            return response

        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            logger.error(f"Speech synthesis canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                logger.error(f"Error details: {cancellation_details.error_details}")
            return {"error": "Speech synthesis was canceled"}
    except Exception as e:
        logger.exception(f"Error in synthesize_speech_with_visemes_task: {str(e)}")
        return {"error": str(e)}
    finally:
        # Clean up temporary files
        for file_path in file_paths.values():
            if os.path.exists(file_path):
                os.remove(file_path)
    return data


@shared_task()
def claude_response(request_text):
    response = anthropic_client.messages.create(
          model = 'claude-3-sonnet-20240229',
          max_tokens=150,
          temperature = 0,
          system = prompt,
          messages =[{
               "role":'user',
               "content":request_text

          }]
     )
    serialized_response = {
        'id': response.id,
        'content': [
            {
                'text': content.text if hasattr(content, 'text') else str(content),
                'type': content.type if hasattr(content, 'type') else 'text'
            } for content in response.content
        ],
        'model': response.model,
        'role': response.role,
        'stop_reason': response.stop_reason,
        'stop_sequence': response.stop_sequence,
        'type': response.type,
        'usage': {
            'input_tokens': response.usage.input_tokens,
            'output_tokens': response.usage.output_tokens
        }
    }
    
    return serialized_response
