# LabJack Pyranometer → InfluxDB

Measures solar irradiance with a pyranometer connected to a **LabJack T7** and logs it to InfluxDB once per second.

## How it works

1. Opens the LabJack T7 over USB and reads the voltage on `AIN1`.
2. Converts voltage to irradiance using the sensor's calibration constant:

   `irradiance (W/m²) = voltage (V) / (sensitivity (µV per W/m²) × 10⁻⁶)`

3. Writes both the raw voltage and the irradiance to the `pyranometer` measurement, tagged with the device and channel.

## Run

This needs USB access to the LabJack, so run it on the host rather than in Docker.

1. Install the LabJack LJM driver from [labjack.com](https://labjack.com/pages/support?doc=/software-driver/ljm-software-installers-t4-t7-digit/).
2. Then:
   ```bash
   pip install -r requirements.txt
   export INFLUX_ORG=... INFLUX_TOKEN=... PYRO_SENSITIVITY=10.0
   python labjack_pyranometer.py
   ```

Press Ctrl-C to stop. The LabJack connection is closed cleanly on exit.

## Settings

| Variable | Default | Meaning |
|---|---|---|
| `INFLUX_URL` | `http://localhost:8086` | InfluxDB address |
| `INFLUX_ORG` / `INFLUX_TOKEN` | required | InfluxDB credentials |
| `INFLUX_LABJACK_BUCKET` | `JabLack` | Bucket to write to |
| `PYRO_SENSITIVITY` | `10.0` | Sensor sensitivity in µV per W/m². Use the value on your sensor's calibration certificate |
