pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Start Gunicorn
gunicorn your_project.wsgi