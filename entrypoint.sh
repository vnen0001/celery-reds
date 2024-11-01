#!/bin/bash

NAME="vital_voices_project"
DJANGODIR= /home/ubuntu/final_backend
USER=ubuntu
GROUP=ubuntu
WORKERS=3
BIND="0.0.0.0:8000"
DJANGO_SETTINGS_MODULE=vital_voices_project.settings
DJANGO_WSGI_MODULE=vital_voices_project.wsgi
LOG_LEVEL=info
cd "$DJANGODIR"
echo "Changed to directory: $(pwd)"
echo "Starting $NAME as `whoami`"
echo "Current directory: $(pwd)"
echo "Python version: $(python3 --version)"
# Activate the virtual environment
VENV_PATH="/home/ubuntu/final_backend/django-back"
if [ -d "$VENV_PATH" ]; then
    echo "Activating virtual environment"
    source "$VENV_PATH/bin/activate"
    echo "Virtual environment activated"
    echo "Python path: $(which python)"
    echo "Gunicorn path: $(which gunicorn)"
else
    echo "Error: Virtual environment not found at $VENV_PATH"
    exit 1
fi
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH
echo "PYTHONPATH: $PYTHONPATH"
echo "DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"

# Check if the WSGI module can be imported
echo "Attempting to import WSGI module:"
python -c "import $DJANGO_WSGI_MODULE" 2>&1 || echo "Failed to import WSGI module"
# Start Gunicorn
echo "Starting Gunicorn"
exec $VENV_PATH/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $WORKERS \
  --user=$USER \
  --group=$GROUP \
  --bind=$BIND \
  --log-level=$LOG_LEVEL \
  --log-file=- \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  --capture-output \
  --enable-stdio-inheritance
