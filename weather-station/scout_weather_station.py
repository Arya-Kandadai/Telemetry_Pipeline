import serial
import time
import datetime
import os
import influxdb_client
from influxdb_client.client.write_api import ASYNCHRONOUS
import operator
from functools import reduce

def nmea_checksum(sentence: str):
    try:
        sentence_stripped = sentence.strip("$\n")
        nmeadata, checksum = sentence_stripped.split("*", 1)
        calculated_checksum = reduce(operator.xor, (ord(s) for s in nmeadata), 0)
        if int(checksum, base=16) == calculated_checksum:
            return sentence
    except:
        pass
    return None

def floatOr0(input):
    try:
        output = float(input)
    except:
        output = float(0)
    return output

def AngleClean(input):
    return input if input <= 180 else -(360 - input)

def translate(line):
    data = line.split(',')
    p = ""

    try:
        if data[0] == "$GPGGA":
            lat = floatOr0(data[2][0:2]) + floatOr0(data[2][2:]) / 60
            if data[3] == "S":
                lat *= -1
            lon = floatOr0(data[4][0:3]) + floatOr0(data[4][3:]) / 60
            if data[5] == "W":
                lon *= -1
            lat = round(lat, 5)
            lon = round(lon, 5)
            print("Got GPS:", lat, lon)
            p = influxdb_client.Point("GGA") \
                .field("utc", data[1]) \
                .field("n_sats", floatOr0(data[7])) \
                .field("latitude", lat) \
                .field("longitude", lon) \
                .field("altitude", floatOr0(data[9]))
        elif data[0] == "$WIMWV":
            p = influxdb_client.Point("MWV") \
                .tag("reference", data[2]) \
                .field("angle", AngleClean(floatOr0(data[1]))) \
                .field("v_wind", floatOr0(data[3]) * 1.852) \
                .field("units", data[4])
        elif data[0] == "$WIMDA":
            p = influxdb_client.Point("MDA") \
                .field("pressure_I", floatOr0(data[1])) \
                .field("pressure_B", floatOr0(data[3])) \
                .field("temperature", floatOr0(data[5])) \
                .field("rel_humidity", floatOr0(data[9])) \
                .field("dew_point", floatOr0(data[11])) \
                .field("wind_dir_T", floatOr0(data[13])) \
                .field("wind_dir_M", floatOr0(data[15])) \
                .field("wind_speed", floatOr0(data[19]) * 3.6)
        elif data[0] == "$HCHDT":
            p = influxdb_client.Point("HDT").field("heading", floatOr0(data[1]))
        elif data[0] == "$GPVTG":
            p = influxdb_client.Point("VTG") \
                .field("track_degrees_true", floatOr0(data[1])) \
                .field("track_degrees_magnetic", floatOr0(data[2])) \
                .field("speed_kph", floatOr0(data[7]))
    except Exception as e:
        print("Error parsing line:", line)
        print(e)
    return p
# InfluxDB configuration
# All settings come from environment variables (see .env.example)
bucket = os.environ.get("INFLUX_BUCKET", "ScoutWeather")
org = os.environ["INFLUX_ORG"]
token = os.environ["INFLUX_TOKEN"]
url = os.environ.get("INFLUX_URL", "http://localhost:8086")
# Weather station serial-over-TCP bridge, e.g. socket://192.168.0.87:8899
SERIAL_URL = os.environ.get("WEATHER_SERIAL_URL", "socket://192.168.0.87:8899")

client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=ASYNCHRONOUS)

# Continuous execution loop
while True:
    try:
        with serial.serial_for_url(SERIAL_URL, timeout=1, baudrate=4800) as ser:
            print("Logging started. Ctrl-C to stop.")
            while True:
                try:
                    data = nmea_checksum(ser.readline().decode())
                    if data:
                        point = translate(data)
                        if point != "":
                            write_api.write(bucket=bucket, org=org, record=point)
                except Exception as inner_e:
                    print("Inner error:", inner_e)
                    time.sleep(1)  # avoid tight crash loop

    except Exception as outer_e:
        print("Serial connection error:", outer_e)
        try:
            client.close()
            ser.close()
        except:
            pass
        print("Logging stopped")
        time.sleep(5)
