# Use an official Python runtime as a parent image
FROM python:3.12

# Set the working directory in the container
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    unixodbc-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Add Microsoft repository
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Install ODBC Driver 18
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y wget unzip

COPY . /app/
# install rhuharb
RUN wget https://github.com/DanielSWolf/rhubarb-lip-sync/releases/download/v1.13.0/Rhubarb-Lip-Sync-1.13.0-Linux.zip \
    && unzip -o Rhubarb-Lip-Sync-1.13.0-Linux.zip \
    && mv Rhubarb-Lip-Sync-1.13.0-Linux/rhubarb /app/vital_voices/ \
    && chmod +x /app/vital_voices/rhubarb \
    && rm -rf Rhubarb-Lip-Sync-1.13.0-Linux.zip


# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt



# Make port 8000 available to the world outside this container
EXPOSE 8000
ENV DJANGO_SETTINGS_MODULE=vital_voices_project.settings
# Run gunicorn when the container launches
COPY entrypoint2.sh /entrypoint2.sh
RUN chmod +x /entrypoint2.sh
CMD ["/entrypoint2.sh"]
