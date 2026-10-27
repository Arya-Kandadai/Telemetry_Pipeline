FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scout_weather_station.py .

CMD ["python", "-u", "scout_weather_station.py"]
