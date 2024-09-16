# from celery import shared_task
# from django.db import connections
# # from elevenlabs import VoiceSettings
# # from elevenlabs.client import ElevenLabs
# import subprocess
# import os
# import uuid
# import tempfile
# import base64
# import io
# import zipfile
# import openai
# import azure.cognitiveservices.speech as speechsdk
# # from .powerball import simulate_and_return_lists

# @shared_task
# def process_suicide_data(include_expenditure):
#     with connections['default'].cursor() as cursor:
#         if include_expenditure:
#             cursor.execute("""
#                 SELECT s.Gender, s.Year, SUM(s.Suicide_Number) AS total, t.Aust AS total_expenditure
#                 FROM dbo.suicide_number_data s
#                 LEFT JOIN (
#                     SELECT LEFT(Financial_Year, 4) AS Year, Aust
#                     FROM DBO.Total_expenditure
#                 ) t ON s.Year = t.Year
#                 GROUP BY s.Gender, s.Year, t.Aust
#                 ORDER BY s.Year, s.Gender
#             """)
#         else:
#             cursor.execute("""
#                 SELECT Gender, Year, SUM(Suicide_Number) AS total
#                 FROM dbo.suicide_number_data
#                 GROUP BY Gender, Year
#                 ORDER BY Year, Gender
#             """)
#         rows = cursor.fetchall()

#     result = []
#     years = set()
#     for row in rows:
#         year = row[1]  # Assuming Year is the second column
#         years.add(year)
    
#     for year in sorted(years):
#         year_data = {
#             'year': str(year),
#             'Male': 0,
#             'Female': 0
#         }
#         if include_expenditure:
#             year_data['total_expenditure'] = 'N/A'
        
#         for row in rows:
#             if row[1] == year:
#                 gender = row[0]
#                 suicide_number = row[2]
#                 year_data[gender] = suicide_number
#                 if include_expenditure and len(row) > 3:
#                     year_data['total_expenditure'] = row[3] if row[3] is not None else 'N/A'
        
#         result.append(year_data)
    
#     return result

# @shared_task
# def fetch_spider_data():
#     with connections['default'].cursor() as cursor:
#         cursor.execute("""
#             -- SQL Query to get top 5 mechanisms for male and female across all years
#             SELECT 
#                 Sex,
#                 Agegroup,
#                 SUM(Values_) as total_count
#             FROM 
#                [dbo].[NewTable]
#             WHERE 
#                 Sex IN ('Males', 'Females')
#                 AND Agegroup != 'Total'
#             GROUP BY 
#                 Sex, Agegroup
#             HAVING 
#                 Sex = 'Males' AND Agegroup IN (
#                     SELECT TOP 5 Agegroup
#                     FROM [dbo].[NewTable]
#                     WHERE Sex = 'Males' AND Agegroup != 'Total'
#                     GROUP BY Agegroup
#                     ORDER BY SUM(Values_) DESC
#                 )
#                 OR
#                 Sex = 'Females' AND Agegroup IN (
#                     SELECT TOP 5 Agegroup
#                     FROM [dbo].[NewTable]
#                     WHERE Sex = 'Females' AND Agegroup != 'Total'
#                     GROUP BY Agegroup
#                     ORDER BY SUM(Values_) DESC
#                 )
#             ORDER BY 
#                 Sex, total_count DESC
#         """)
#         rows = cursor.fetchall()
#         data = []
#         for row in rows:
#             data.append({
#                 'Sex': row[0],
#                 'Agegroup': row[1],
#                 'total_count': row[2]
#             })
#     return data

# # @shared_task
# # def simulate_powerball(max_tickets):
# #     tickets, losses, avg = simulate_and_return_lists(max_tickets)
# #     return {'tickets': tickets, 'losses': losses}

# @shared_task
# def fetch_parallel_coordinates_data():
#     with connections['default'].cursor() as cursor:
#         cursor.execute("select * from [dbo].[Different_games_expenditure]")
#         rows = cursor.fetchall()
#         data = []
#         for row in rows:
#             data.append({
#                 'Year': row[0],
#                 'Casino': row[1],
#                 'Gaming_machine': row[2],
#                 'Interactive_gaming': row[3],
#                 'Keno': row[4],
#                 'Lotteries': row[5],
#                 'Minor_gaming': row[6],
#                 'Wagering': row[7],
#                 'Total': row[8]
#             })
#     return data

# @shared_task
# def generate_speech(text):
#     temp_dir = tempfile.gettempdir()
#     wav_path = ogg_path = json_path = None
#     try:
#         # Generate unique filenames
#         wav_filename = f"{uuid.uuid4()}.wav"
#         json_filename = f"{uuid.uuid4()}.json"
#         ogg_filename = f"{uuid.uuid4()}.ogg"
#         wav_path = os.path.join(temp_dir, wav_filename)
#         ogg_path = os.path.join(temp_dir, ogg_filename)
#         json_path = os.path.join(temp_dir, json_filename)

#         # Azure Text-to-Speech configuration
#         region = os.environ.get('AZURE_REGION')
#         key = os.environ.get('AZURE_AI_KEY')
#         speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
#         speech_config.speech_synthesis_voice_name = "en-US-AndrewMultilingualNeural"

#         # Create a speech synthesizer using a file as audio output
#         file_config = speechsdk.audio.AudioOutputConfig(filename=wav_path)
#         speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=file_config)

#         # Synthesize the text
#         result = speech_synthesizer.speak_text_async(text).get()

#         # Check result
#         if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
#             print(f"Speech synthesized to [{wav_path}]")
#         elif result.reason == speechsdk.ResultReason.Canceled:
#             cancellation_details = result.cancellation_details
#             print(f"Speech synthesis canceled: {cancellation_details.reason}")
#             if cancellation_details.reason == speechsdk.CancellationReason.Error:
#                 print(f"Error details: {cancellation_details.error_details}")
#             return None  # Return None if synthesis failed

#         # Convert WAV to OGG
#         subprocess.run(['ffmpeg', '-i', wav_path, '-c:a', 'libvorbis', '-q:a', '4', ogg_path], check=True)

#         # Generate lip sync data
#         subprocess.run(['Rhubarb-Lip-Sync-1.13.0-macOS/rhubarb', '-f', 'json', ogg_path, '-o', json_path], check=True)

#         # Create ZIP file in memory
#         zip_buffer = io.BytesIO()
#         with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
#             zip_file.write(wav_path, wav_filename)
#             zip_file.write(json_path, json_filename)
#             zip_file.write(ogg_path, ogg_filename)
#         zip_buffer.seek(0)
#         return zip_buffer.getvalue()

#     finally:
#         # Clean up temporary files
#         for path in [wav_path, ogg_path, json_path]:
#             if path and os.path.exists(path):
#                 os.remove(path)

import os
import uuid
import tempfile
import io
import zipfile
import subprocess
from celery import shared_task
from django.db import connections
import azure.cognitiveservices.speech as speechsdk
from django.conf import settings
import logging
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

@shared_task
def process_suicide_data(include_expenditure):
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

    with connections['default'].cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

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
    
    return result



@shared_task
def fetch_parallel_coordinates_data():
    query = "SELECT * FROM [dbo].[Different_games_expenditure]"
    with connections['default'].cursor() as cursor:
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

@shared_task
def generate_speech(text):
    temp_dir = tempfile.gettempdir()
    file_paths = {
        'wav': os.path.join(temp_dir, f"{uuid.uuid4()}.wav"),
        'json': os.path.join(temp_dir, f"{uuid.uuid4()}.json"),
        'ogg': os.path.join(temp_dir, f"{uuid.uuid4()}.ogg")
    }

    try:
        azure_ai_key = os.getenv('AZURE_AI_KEY')
        azure_region = os.getenv('AZURE_REGION')
        if not azure_ai_key or not azure_region:
            logger.error("Azure credentials not found in environment variables")
            return None
        speech_config = speechsdk.SpeechConfig(
            subscription=azure_ai_key,
            region=azure_region
        )
        
    
        speech_config.speech_synthesis_voice_name = "en-US-AndrewMultilingualNeural"
        file_config = speechsdk.audio.AudioOutputConfig(filename=file_paths['wav'])
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=file_config)

        result = speech_synthesizer.speak_text_async(text).get()
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            logger.info("Speech synthesized for text [{}]".format(text))
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            logger.error("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                logger.error(f"Error details: {cancellation_details.error_details}")
            return None
        
        # Checking if the file is empty or not
        if not os.path.exists(file_paths['wav']) or os.path.getsize(file_paths['wav']) == 0:
            logger.error(f"WAV file is missing or empty: {file_paths['wav']}")
            return None
        

        # Convert WAV to OGG
        try:
            ffmpeg_command = ['ffmpeg', '-i', file_paths['wav'], '-c:a', 'libvorbis', '-q:a', '4', file_paths['ogg']]
            ffmpeg_result = subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True)
            logger.info(f"FFmpeg conversion successful: {ffmpeg_result.stdout}")
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr}")
            logger.error(f"FFmpeg command: {' '.join(ffmpeg_command)}")
            return None

        # Generate lip sync data
        try:
            rhubarb_command = ['Rhubarb-Lip-Sync-1.13.0-macOS/rhubarb', '-f', 'json', file_paths['ogg'], '-o', file_paths['json']]
            rhubarb_result = subprocess.run(rhubarb_command, check=True, capture_output=True, text=True)
            logger.info(f"Rhubarb lip sync successful: {rhubarb_result.stdout}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Rhubarb error: {e.stderr}")
            logger.error(f"Rhubarb command: {' '.join(rhubarb_command)}")
            return None


        # Zipping it up 
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
            for file_type, file_path in file_paths.items():
                zip_file.write(file_path, os.path.basename(file_path))
        
        return zip_buffer.getvalue()

    except Exception as e:
        logger.exception(f"Error in generate_speech: {str(e)}")
        return None

    finally:
        for file_path in file_paths.values():
            if os.path.exists(file_path):
                os.remove(file_path)