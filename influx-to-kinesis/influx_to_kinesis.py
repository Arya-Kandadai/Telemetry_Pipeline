import os
import time
import json
import boto3
from influxdb_client import InfluxDBClient

# ==== CONFIG ====
# All settings come from environment variables (see .env.example).
# Run one copy per bucket, e.g. INFLUX_BUCKET=ScoutWeather or INFLUX_BUCKET=JabLack
INFLUX_URL = os.environ.get("INFLUX_URL", "http://localhost:8086")
INFLUX_TOKEN = os.environ["INFLUX_TOKEN"]
INFLUX_ORG = os.environ["INFLUX_ORG"]
INFLUX_BUCKET = os.environ.get("INFLUX_BUCKET", "ScoutWeather")

KINESIS_STREAM_NAME = os.environ.get("KINESIS_STREAM_NAME", "weather-station-scout-dataStream")
AWS_REGION = os.environ.get("AWS_REGION", "ap-southeast-2")
QUERY_INTERVAL = int(os.environ.get("QUERY_INTERVAL", "5"))  # seconds between queries

# Connect to InfluxDB
influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
query_api = influx_client.query_api()

# Connect to AWS Kinesis (credentials from AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY or ~/.aws/credentials)
kinesis_client = boto3.client("kinesis", region_name=AWS_REGION)

# Keep track of the last query time
last_query_time = "-5s"  # initial query range (last 10s)

while True:
    try:
        # Flux query: get data since last_query_time
        flux_query = f'''
        from(bucket: "{INFLUX_BUCKET}")
        |> range(start: {last_query_time})
        |> sort(columns: ["_time"])
        '''
        tables = query_api.query(flux_query)

        # Update the last_query_time to now for next iteration
        now_rfc3339 = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        last_query_time = f"time(v: {json.dumps(now_rfc3339)})"

        for table in tables:
            for record in table.records:
                # Prepare data payload
                data_point = {
                    "time": str(record.get_time()),
                    "measurement": record.get_measurement(),
                    "field": record.get_field(),
                    "value": record.get_value()
                }

                # Send to Kinesis
                kinesis_client.put_record(
                    StreamName=KINESIS_STREAM_NAME,
                    Data=json.dumps(data_point).encode("utf-8"),
                    PartitionKey="influx"  # all go to same partition here
                )
                print(f"Sent: {data_point}")

    except Exception as e:
        print(f"Error: {e}")

    time.sleep(QUERY_INTERVAL)
