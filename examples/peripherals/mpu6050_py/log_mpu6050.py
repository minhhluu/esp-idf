import serial
import time
import csv
from datetime import datetime

# Adjust this to match your serial port (check with `ls /dev/ttyUSB*` or `ls /dev/tty.*` on Mac)
SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200
CSV_FILE = "mpu6050_log.csv"
LOG_INTERVAL_SEC = 1

def main():
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud.")
    
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Angle X (deg)", "Angle Y (deg)", "Angle Z (deg)"])
        
        last_log_time = time.time()

        while True:
            raw = ser.readline()
            try:
                line = raw.decode('utf-8').strip()
                
            except UnicodeDecodeError:
                print(f"Skipped invalid line: {raw}")
                continue  # or return

            if not line:
                continue

            if line.startswith("Angle X:"):
                try:
                    parts = line.replace("°", "").split(",")
                    angle_x = float(parts[0].split(":")[1])
                    angle_y = float(parts[1].split(":")[1])
                    angle_z = float(parts[2].split(":")[1])

                    now = time.time()
                    if now - last_log_time >= LOG_INTERVAL_SEC:
                        timestamp = datetime.now().isoformat()
                        writer.writerow([timestamp, angle_x, angle_y, angle_z])
                        print(f"[{timestamp}] Saved: X={angle_x}, Y={angle_y}, Z={angle_z}]")
                        last_log_time = now
                except Exception as e:
                    print(f"Parse error: {e} -- Line: {line}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nLogging stopped.")
