# InfluxDB → AWS Kinesis

Forwards live telemetry from an InfluxDB bucket to an **AWS Kinesis** data stream, so data collected on the road can be read in the cloud.

## How it works

Every few seconds (5 by default) the script:
1. Runs a Flux query for all points written since the previous query.
2. Converts each point to JSON: `{"time", "measurement", "field", "value"}`.
3. Sends each one to Kinesis with `put_record`.

The same script handles any bucket. `docker-compose.yml` runs two copies: one for `ScoutWeather` (weather station) and one for `JabLack` (pyranometer).

## Run

With Docker (from the repo root):
```bash
docker compose up -d kinesis-scout kinesis-labjack
```

Or directly:
```bash
pip install -r requirements.txt
export INFLUX_ORG=... INFLUX_TOKEN=... INFLUX_BUCKET=ScoutWeather
export AWS_ACCESS_KEY_ID=... AWS_SECRET_ACCESS_KEY=...
python influx_to_kinesis.py
```

## Settings

| Variable | Default | Meaning |
|---|---|---|
| `INFLUX_URL` | `http://localhost:8086` | InfluxDB address |
| `INFLUX_ORG` / `INFLUX_TOKEN` | required | InfluxDB credentials |
| `INFLUX_BUCKET` | `ScoutWeather` | Bucket to forward |
| `KINESIS_STREAM_NAME` | `weather-station-scout-dataStream` | Target Kinesis stream |
| `AWS_REGION` | `ap-southeast-2` | AWS region |
| `QUERY_INTERVAL` | `5` | Seconds between polls |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | from env or `~/.aws/credentials` | AWS credentials. Use an IAM user that can only write to this stream |
