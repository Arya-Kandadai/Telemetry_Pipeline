from labjack import ljm
import os
import time
from influxdb_client import InfluxDBClient, Point, WritePrecision

# --- Pyranometer Conversion ---
def pyro_to_irradiance(voltage_reading, sensitivity_uv_per_wm2):
    """
    Convert pyranometer voltage reading to irradiance (W/m²).
    sensitivity_uv_per_wm2: sensor sensitivity from calibration [µV per W/m²]
    """
    sensitivity_v_per_wm2 = sensitivity_uv_per_wm2 * 1e-6  # convert µV/W·m² → V/W·m²
    return voltage_reading / sensitivity_v_per_wm2

# Set your pyranometer's calibration constant here (check sensor certificate!)
PYRO_SENSITIVITY = float(os.environ.get("PYRO_SENSITIVITY", "10.0"))  # example: 10 µV/W·m²

# --- LabJack Connection ---
handle = ljm.openS("T7", "USB", "ANY")
channels = ["AIN1"]  # Pyranometer connected here

# --- InfluxDB Setup ---
# All settings come from environment variables (see .env.example)
INFLUX_URL = os.environ.get("INFLUX_URL", "http://localhost:8086")
INFLUX_TOKEN = os.environ["INFLUX_TOKEN"]
INFLUX_ORG = os.environ["INFLUX_ORG"]
INFLUX_BUCKET = os.environ.get("INFLUX_LABJACK_BUCKET", "JabLack")

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api()

# --- Logging Loop ---
try:
    while True:
        # Read voltage from LabJack
        values = ljm.eReadNames(handle, len(channels), channels)

        for ch_name, ch_value in zip(channels, values):
            # Convert to irradiance
            irradiance = pyro_to_irradiance(ch_value, PYRO_SENSITIVITY)

            # Write both voltage + irradiance to InfluxDB
            point = (
                Point("pyranometer")
                .tag("device", "T7")
                .tag("channel", ch_name)
                .field("voltage", float(ch_value))
                .field("irradiance", float(irradiance))
                .time(time.time_ns(), WritePrecision.NS)
            )
            write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)

        print(f"Logged: Voltage={ch_value:.6f} V, Irradiance={irradiance:.2f} W/m²")
        time.sleep(1)

except KeyboardInterrupt:
    print("\nStopping...")
finally:
    ljm.close(handle)
