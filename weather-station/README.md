# Weather Station → InfluxDB

Reads the scout car's weather station, checks every NMEA sentence's checksum, and writes the parsed values to InfluxDB in real time.

## What it reads

The station streams NMEA 0183 sentences over a serial-to-TCP bridge (default `socket://192.168.0.87:8899`, 4800 baud).

| Sentence | InfluxDB measurement | Fields |
|---|---|---|
| `$GPGGA` | `GGA` | UTC time, satellites, latitude, longitude, altitude |
| `$WIMWV` | `MWV` | relative wind angle (−180…180°), wind speed (knots → km/h) |
| `$WIMDA` | `MDA` | pressure, air temperature, humidity, dew point, true/magnetic wind direction, wind speed (m/s → km/h) |
| `$HCHDT` | `HDT` | heading |
| `$GPVTG` | `VTG` | true/magnetic track, ground speed (km/h) |

Sentences with a bad checksum are dropped. If the connection drops, the script waits 5 seconds and reconnects, so it can run unattended for a whole race day.

## Run

With Docker (from the repo root):
```bash
docker compose up -d weather-station
```

Or directly:
```bash
pip install -r requirements.txt
export INFLUX_ORG=... INFLUX_TOKEN=...
python scout_weather_station.py
```

## Settings

| Variable | Default | Meaning |
|---|---|---|
| `INFLUX_URL` | `http://localhost:8086` | InfluxDB address |
| `INFLUX_ORG` | required | InfluxDB organisation |
| `INFLUX_TOKEN` | required | InfluxDB API token |
| `INFLUX_BUCKET` | `ScoutWeather` | Bucket to write to |
| `WEATHER_SERIAL_URL` | `socket://192.168.0.87:8899` | Address of the weather station bridge |
