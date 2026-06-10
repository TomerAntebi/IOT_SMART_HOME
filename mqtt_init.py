# mqtt_init.py
# -------------------------------------------------------------
# Purpose:
#   Create and initialize an MQTT client for the Smart Room Monitor project.
#   Provides a helper function to connect and start the network loop.
# -------------------------------------------------------------

import random
import paho.mqtt.client as mqtt

BROKER_HOST = "broker.hivemq.com"
BROKER_PORT = 1883
KEEPALIVE = 60

def create_client(name_prefix: str, on_message=None, on_connect=None) -> mqtt.Client:
    """
    Creates an MQTT client with a unique client_id.
    Optionally attaches callbacks (on_message, on_connect).
    """
    client_id = f"{name_prefix}_{random.randint(1000, 9999)}"
    client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)

    if on_connect:
        client.on_connect = on_connect
    if on_message:
        client.on_message = on_message

    return client

def connect_and_loop(client: mqtt.Client) -> mqtt.Client:
    """
    Connects the client to the broker and starts the network loop (non-blocking).
    """
    client.connect(BROKER_HOST, BROKER_PORT, KEEPALIVE)
    client.loop_start()
    print(f"[✓] MQTT connected to {BROKER_HOST}:{BROKER_PORT} (client_id={client._client_id.decode()})")
    return client

