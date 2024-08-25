# Use official Python image as base image
FROM python:3.9-slim

# Set working directory in the container
WORKDIR /app

RUN pip install --upgrade pip

ADD ./requirements.txt ./requirements.txt

# Copy the Python script into the container
COPY db_connection.py .
COPY spotify_api_auth_token.py .
COPY spotify_api.py .

# Install dependencies
RUN pip install -r requirements.txt

# Command to run the Python script
CMD ["python", "spotify_api.py"]