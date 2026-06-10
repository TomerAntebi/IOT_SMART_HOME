# button_emulator.py
import time
from mqtt_init import create_client, connect_and_loop

TOPIC_MODE = "smart-home/control/mode"  # "auto" | "manual"

def main():
    client = create_client("SR_button")
    connect_and_loop(client)

    mode = "auto"
    print("[button] running. Toggling mode every 10 seconds...")

    while True:
        mode = "manual" if mode == "auto" else "auto"
        client.publish(TOPIC_MODE, mode)
        print(f"[button] published mode: {mode}")
        time.sleep(10)

if __name__ == "__main__":
    main()

