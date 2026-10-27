FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY influx_to_kinesis.py .

CMD ["python", "-u", "influx_to_kinesis.py"]
