pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Start Gunicorn
echo Starting Gunicorn.
exec gunicorn vital_voices_project.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3
