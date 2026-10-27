# Solar Car Telemetry Pipeline

Live data pipeline for a solar car race team. Sensors on the scout car (a weather station, a pyranometer and a light logger) are read in real time, stored in **InfluxDB**, and forwarded to **AWS Kinesis** so the strategy team can use them from anywhere.

```
 Weather station ──(NMEA over TCP)──► weather-station ──┐
                                                         ├──► InfluxDB ──► influx-to-kinesis ──► AWS Kinesis ──► API Gateway
 Pyranometer ──(LabJack T7, USB)──► labjack-pyranometer ─┘
 Light logger ──(USB serial)──► light-logger ──► CSV
```

## Components

| Folder | What it does |
|---|---|
| [`weather-station/`](weather-station/) | Parses NMEA sentences (GPS, wind, pressure, temperature, heading) and writes them to InfluxDB |
| [`labjack-pyranometer/`](labjack-pyranometer/) | Reads a pyranometer through a LabJack T7, converts voltage to irradiance (W/m²), writes to InfluxDB |
| [`influx-to-kinesis/`](influx-to-kinesis/) | Polls an InfluxDB bucket and pushes every new point to an AWS Kinesis stream |
| [`light-logger/`](light-logger/) | Reads a serial light sensor and logs one averaged reading per second to CSV |
| [`api-test/`](api-test/) | Small script for testing the AWS API Gateway endpoint |

## Quick start

```bash
git clone https://github.com/<your-username>/solar-telemetry-pipeline.git
cd solar-telemetry-pipeline
cp .env.example .env        # then fill in your real tokens and keys
docker compose up -d --build
```

This starts InfluxDB (on http://localhost:8086), the weather station logger and two Kinesis forwarders, one for the weather bucket and one for the LabJack bucket.

The LabJack and light logger scripts need direct USB access, so run them on the host machine. Each folder's README has the steps.

## Configuration

All settings (tokens, bucket names, ports, AWS region) are read from environment variables. See [`.env.example`](.env.example) for the full list. `.env` is git-ignored, so keys never end up in the repo.

## Tech

Python · InfluxDB 2 · AWS Kinesis · AWS API Gateway · Docker Compose · LabJack LJM · pySerial
