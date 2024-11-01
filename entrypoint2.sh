#!/bin/sh

python manage.py check
gunicorn --bind 0.0.0.0:8000 \
         --workers 3 \
         --timeout 120 \
         --access-logfile - \
         --error-logfile - \
         --log-level info \
         --capture-output \
         --enable-stdio-inheritance \
         vital_voices_project.wsgi:application
