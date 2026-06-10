# app_manager.py
# -------------------------------------------------------------
# Purpose:
#   Central Data Manager for the Smart Room Monitor IoT project.
#   - Subscribes to sensor telemetry
#   - Subscribes to control mode (AUTO / MANUAL)
#   - Calculates system status (INFO / WARNING / ALARM)
#   - Publishes status and alerts
#   - Controls relay automatically in AUTO mode
#   - Stores measurements and events in SQLite (smart_home.db)
# -------------------------------------------------------------

import json
import time

from mqtt_init import create_client, connect_and_loop
from db import init_db, insert_measurement, insert_event

# =========================
# MQTT Topics (namespace)
# =========================
TOPIC_TELEMETRY   = "smart-home/telemetry"
TOPIC_MODE        = "smart-home/control/mode"
TOPIC_STATUS      = "smart-home/status"
TOPIC_ALERTS      = "smart-home/alerts"
TOPIC_RELAY_CMD   = "smart-home/actuator/relay/cmd"

# =========================
# Thresholds
# =========================
WARN_TEMP  = 28.0
ALARM_TEMP = 32.0

# =========================
# Global State
# =========================
current_mode = "auto"   # default system mode


def classify_temperature(temp: float) -> tuple[str, str]:
    if temp >= ALARM_TEMP:
        return "ALARM", f"Temperature is very high ({temp}°C)"
    if temp >= WARN_TEMP:
        return "WARNING", f"Temperature is high ({temp}°C)"
    return "INFO", f"Temperature is normal ({temp}°C)"


def on_connect(client, userdata, flags, rc):
    print("[manager] connected to broker")
    print("[manager] subscribing to telemetry and control mode topics")
    client.subscribe(TOPIC_TELEMETRY)
    client.subscribe(TOPIC_MODE)


def on_message(client, userdata, msg):
    global current_mode

    # ---------- Handle MODE messages ----------
    if msg.topic == TOPIC_MODE:
        new_mode = msg.payload.decode().strip().lower()

        if new_mode in ("auto", "manual"):
            current_mode = new_mode
            now = time.time()

            print(f"[manager] mode changed -> {current_mode.upper()}")

            # DB: log mode change as event
            insert_event(
                ts=now,
                event_type="MODE_CHANGE",
                level="INFO",
                details=f"Mode changed to {current_mode.upper()}"
            )

            # MQTT: publish status
            status_payload = {
                "level": "INFO",
                "message": f"Mode changed to {current_mode.upper()}",
                "ts": now
            }
            client.publish(TOPIC_STATUS, json.dumps(status_payload))

        return

    # ---------- Handle TELEMETRY messages ----------
    if msg.topic == TOPIC_TELEMETRY:
        try:
            payload = json.loads(msg.payload.decode())

            temp = float(payload["temp"])
            hum  = float(payload.get("hum", 0))
            ts   = float(payload.get("ts", time.time()))

            level, message = classify_temperature(temp)

            # DB: save measurement
            insert_measurement(
                ts=ts,
                temp=temp,
                hum=hum,
                mode=current_mode.upper(),
                level=level,
                message=message
            )

            # MQTT: publish STATUS (always)
            status_payload = {
                "level": level,
                "message": message,
                "temp": temp,
                "hum": hum,
                "mode": current_mode.upper(),
                "ts": ts
            }
            client.publish(TOPIC_STATUS, json.dumps(status_payload))
            print("[manager] status:", status_payload)

            # MQTT + DB: publish/store ALERTS only for WARNING / ALARM
            if level in ("WARNING", "ALARM"):
                alert_payload = {
                    "level": level,
                    "message": message,
                    "ts": ts
                }
                client.publish(TOPIC_ALERTS, json.dumps(alert_payload))
                print("[manager] alert:", alert_payload)

                insert_event(
                    ts=ts,
                    event_type="ALERT",
                    level=level,
                    details=message
                )

            # Automatic relay control (AUTO mode only)
            if current_mode == "auto":
                if level == "ALARM":
                    client.publish(TOPIC_RELAY_CMD, "ON")
                    insert_event(ts=time.time(), event_type="RELAY_CMD", level="ALARM", details="Sent relay cmd: ON")
                elif level == "INFO":
                    client.publish(TOPIC_RELAY_CMD, "OFF")
                    insert_event(ts=time.time(), event_type="RELAY_CMD", level="INFO", details="Sent relay cmd: OFF")
            else:
                print("[manager] MANUAL mode: relay control disabled")

        except Exception as e:
            print("[manager] error processing telemetry:", e)


def main():
    # Ensure DB exists
    init_db()

    client = create_client(
        name_prefix="SR_manager",
        on_connect=on_connect,
        on_message=on_message
    )
    connect_and_loop(client)
    print("[manager] running... (DB enabled)")

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
