# relay_emulator.py
from mqtt_init import create_client, connect_and_loop

TOPIC_RELAY_CMD = "smart-home/actuator/relay/cmd"
TOPIC_RELAY_STATE = "smart-home/actuator/relay/state"

relay_state = "OFF"

def on_connect(client, userdata, flags, rc):
    print("[relay] connected. Subscribing to cmd topic...")
    client.subscribe(TOPIC_RELAY_CMD)

def on_message(client, userdata, msg):
    global relay_state
    cmd = msg.payload.decode().strip().upper()

    if cmd in ("ON", "OFF"):
        relay_state = cmd
        print(f"[relay] cmd received -> relay_state={relay_state}")
        client.publish(TOPIC_RELAY_STATE, relay_state)
    else:
        print(f"[relay] unknown cmd: {cmd}")

def main():
    client = create_client("SR_relay", on_message=on_message, on_connect=on_connect)
    connect_and_loop(client)

    print("[relay] running...")
    # keep alive
    while True:
        pass

if __name__ == "__main__":
    main()

