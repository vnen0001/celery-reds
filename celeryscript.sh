#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
BASE_DIR="$SCRIPT_DIR"
VENV="$BASE_DIR/django-back/bin"
LOG_FILE="$BASE_DIR/celery_worker.log"
PID_FILE="$BASE_DIR/celery_worker.pid"
echo "Current working directory: $(pwd)"
echo "BASE_DIR: $BASE_DIR"
export PYTHONPATH="$BASE_DIR:$PYTHONPATH"

# Create log file if it doesn't exist
touch "$LOG_FILE"

CONCURRENCY=10
TASK_TIME_LIMIT=3600  # Hard time limit in seconds (e.g., 1 hour)
TASK_SOFT_TIME_LIMIT=3540  # Soft time limit in seconds (e.g., 59 minutes)

log_message() {
    echo "$(date): $1" >> "$LOG_FILE"
}

check_worker() {
    log_message "Checking worker status"
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null; then
            log_message "Celery worker is already running with PID $PID"
            return 0
        else
            log_message "PID file exists but process is not running. Removing stale PID file."
            rm "$PID_FILE"
        fi
    else
        log_message "PID file not found"
    fi
    return 1
}

start_worker() {
    if check_worker; then
        return
    fi

    log_message "Attempting to start worker"

    if [ -f "$VENV/activate" ]; then
        source "$VENV/activate"
        log_message "Virtual environment activated"
    else
        log_message "Virtual environment not found at $VENV/activate"
        return
    fi

    log_message "Starting Celery worker"
    celery -A vital_voices_project.celery worker --concurrency=$CONCURRENCY --loglevel=info --time-limit=$TASK_TIME_LIMIT --soft-time-limit=$TASK_SOFT_TIME_LIMIT >> "$BASE_DIR/celery_tasks.log" 2>&1 &
    NEW_PID=$!
    echo $NEW_PID > "$PID_FILE"
    
    log_message "Celery worker started. PID: $NEW_PID"
    sleep 2  # Give the worker some time to start

    if ps -p $NEW_PID > /dev/null; then
        log_message "Celery worker successfully started with PID: $NEW_PID"
    else
        log_message "Failed to start Celery worker"
        return 1
    fi
}

stop_worker() {
    log_message "Attempting to stop worker"
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        kill $PID
        rm "$PID_FILE"
        log_message "Celery worker stopped. PID was: $PID"
    else
        log_message "PID file not found. Worker may not be running."
    fi
}

monitor_worker() {
    log_message "Starting worker monitoring"
    while true; do
        if ! check_worker; then
            log_message "Worker not running. Attempting to start..."
            start_worker
        fi
        sleep 60
    done
}

case "$1" in
    start)
        start_worker
        monitor_worker
        ;;
    stop)
        stop_worker
        ;;
    restart)
        stop_worker
        start_worker
        monitor_worker
        ;;
    monitor)
        monitor_worker
        ;;
    *)
        log_message "Usage: $0 {start|stop|restart|monitor}"
        exit 1
        ;;
esac

exit 0
