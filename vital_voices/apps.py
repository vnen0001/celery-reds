from django.apps import AppConfig
from .utils import find_ffmpeg
from pydub import AudioSegment

class VitalVoicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vital_voices'

    def ready(self):
        ffmpeg_path = find_ffmpeg()
        if ffmpeg_path:
            AudioSegment.converter = ffmpeg_path
            print(f"FFmpeg path set to: {ffmpeg_path}")
        else:
            print("FFmpeg not found in system PATH")
