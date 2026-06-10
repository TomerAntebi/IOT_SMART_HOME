# sensor_emulator.py
import json
import time
import random

from mqtt_init import create_client, connect_and_loop

TOPIC_TELEMETRY = "smart-home/telemetry"

def main():
    client = create_client("SR_sensor")
    connect_and_loop(client)

    while True:
        payload = {
            "temp": round(random.uniform(22.0, 34.0), 1),
            "hum": round(random.uniform(35.0, 85.0), 1),
            "ts": time.time()
        }
        client.publish(TOPIC_TELEMETRY, json.dumps(payload))
        print("[sensor] published:", payload)
        time.sleep(2)

if __name__ == "__main__":
    main()

