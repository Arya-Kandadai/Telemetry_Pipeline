# Light Logger

Reads a light sensor over USB serial and saves one averaged reading per second to a CSV file.

## How it works

- Reads every numeric line the sensor sends (9600 baud) and skips anything that isn't a number.
- Once per second, writes the average of the readings from that second to `averaged_light_log.csv`:
  ```
  Timestamp,AverageReading
  2025-07-21T10:15:01.002345,812.40
  ```
- Flushes after every line, so no data is lost if the laptop dies.

## Run

```bash
pip install -r requirements.txt
ls /dev/tty.usbserial-*                      # find your sensor's port (macOS)
export LIGHT_LOGGER_PORT=/dev/tty.usbserial-142130
python light_logger.py
```

Press Ctrl-C to stop.

| Variable | Default | Meaning |
|---|---|---|
| `LIGHT_LOGGER_PORT` | `/dev/tty.usbserial-142130` | Serial port of the sensor |
