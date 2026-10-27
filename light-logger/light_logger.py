import os
import serial
import time
from datetime import datetime

# Replace with the correct port name
port = os.environ.get('LIGHT_LOGGER_PORT', '/dev/tty.usbserial-142130')  # Use the correct device path
baudrate = 9600  # Change this based on your device's settings

ser = serial.Serial(port, baudrate, timeout=1)
output_file = open("averaged_light_log.csv", "a")
output_file.write("Timestamp,AverageReading\n")  # CSV header

print("Starting to collect and average data...")

buffer = []
start_time = time.time()

try:
    while True:
        line = ser.readline().decode('utf-8').strip()
        if line:
            try:
                value = float(line)  # ← assumes logger sends numeric data
                buffer.append(value)
            except ValueError:
                print("Skipping non-numeric:", line)

        # Check if a second has passed
        if time.time() - start_time >= 1:
            if buffer:
                avg = sum(buffer) / len(buffer)
                timestamp = datetime.now().isoformat()
                log_line = f"{timestamp},{avg:.2f}"
                print(log_line)
                output_file.write(log_line + "\n")
                output_file.flush()
                buffer = []  # Clear for next second
            start_time = time.time()

except KeyboardInterrupt:
    print("\nStopped by user.")
    ser.close()
    output_file.close()
