# dashboard.py
import json
import time
import queue
import os
from collections import deque
from datetime import datetime, time as dt_time

import pandas as pd
import streamlit as st
import paho.mqtt.client as mqtt
from streamlit_autorefresh import st_autorefresh

BROKER = "broker.hivemq.com"
PORT = 1883

TOPIC_STATUS = "smart-home/status"
TOPIC_RELAY_STATE = "smart-home/actuator/relay/state"
TOPIC_MODE = "smart-home/control/mode"

MAX_POINTS = 180
ROOMS_FILE = os.path.join(os.path.dirname(__file__), "rooms.json")

# Initialize authentication and room selection state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "selected_room" not in st.session_state:
    st.session_state.selected_room = None

if "username" not in st.session_state:
    st.session_state.username = None

# Initialize session state for data storage
if "data_points" not in st.session_state:
    st.session_state.data_points = deque(maxlen=MAX_POINTS)

if "latest" not in st.session_state:
    st.session_state.latest = {
        "temp": None,
        "hum": None,
        "level": "INFO",
        "message": "",
        "mode": "-",
        "relay": "UNKNOWN",
        "ts": None
    }

# Initialize system control state
if "system_enabled" not in st.session_state:
    st.session_state.system_enabled = False

if "timer_enabled" not in st.session_state:
    st.session_state.timer_enabled = False

if "timer_start" not in st.session_state:
    st.session_state.timer_start = dt_time(8, 0)

if "timer_end" not in st.session_state:
    st.session_state.timer_end = dt_time(22, 0)

# Thread-safe queue for MQTT messages (global for callback access)
_mqtt_queue = None

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("[dashboard] Connected to MQTT broker")
        client.subscribe(TOPIC_STATUS)
        client.subscribe(TOPIC_RELAY_STATE)
        print("[dashboard] Subscribed to topics")
    else:
        print(f"[dashboard] Failed to connect, return code {rc}")

def on_message(client, userdata, msg, properties=None):
    # Debug (optional)
    print("[dashboard] got message:", msg.topic, msg.payload[:80])
    
    # Put message in queue (thread-safe) - use global queue
    global _mqtt_queue
    try:
        if _mqtt_queue:
            _mqtt_queue.put((msg.topic, msg.payload.decode()))
    except Exception as e:
        print(f"[dashboard] Error putting message in queue: {e}")

def load_rooms():
    """Load rooms from JSON file"""
    if os.path.exists(ROOMS_FILE):
        try:
            with open(ROOMS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_rooms(rooms):
    """Save rooms to JSON file"""
    with open(ROOMS_FILE, 'w', encoding='utf-8') as f:
        json.dump(rooms, f, indent=2, ensure_ascii=False)

def add_room(room_name, room_id):
    """Add a new room"""
    rooms = load_rooms()
    # Check if room_id already exists
    if any(r.get("id") == room_id for r in rooms):
        return False, "Room ID already exists"
    rooms.append({"id": room_id, "name": room_name})
    save_rooms(rooms)
    return True, "Room added successfully"

def start_mqtt(msg_queue):
    global _mqtt_queue
    _mqtt_queue = msg_queue
    
    client_id = f"SR_dashboard_{int(time.time())}"

    # Fix deprecation warning (new callback API)
    try:
        client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=client_id,
            protocol=mqtt.MQTTv311
        )
    except TypeError:
        # Fallback for older versions
        client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)

    client.on_connect = on_connect
    client.on_message = on_message
    try:
        client.connect(BROKER, PORT, 60)
        client.loop_start()
        # Give it a moment to connect
        time.sleep(0.5)
        print("[dashboard] MQTT client started")
    except Exception as e:
        print(f"[dashboard] Error connecting to MQTT: {e}")
    return client

def show_login_screen():
    """Display login screen"""
    st.title("🔐 Smart Room Monitor - Login")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("---")
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Login", type="primary", use_container_width=True):
                # Simple authentication (you can enhance this)
                if username and password:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Please enter both username and password")
        
        with col_btn2:
            if st.button("Guest Access", use_container_width=True):
                st.session_state.authenticated = True
                st.session_state.username = "Guest"
                st.rerun()

def show_room_selection():
    """Display room selection screen"""
    st.title("🏠 Select Room")
    
    # Show current user
    st.info(f"Logged in as: **{st.session_state.username}**")
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.selected_room = None
        st.session_state.username = None
        st.rerun()
    
    st.divider()
    
    # Load rooms
    rooms = load_rooms()
    
    # Room selection
    st.subheader("Available Rooms")
    
    if not rooms:
        st.info("No rooms available. Please add a new room.")
    else:
        # Display rooms in a grid
        cols = st.columns(3)
        for idx, room in enumerate(rooms):
            with cols[idx % 3]:
                room_name = room.get("name", room.get("id", "Unknown"))
                room_id = room.get("id", "")
                if st.button(f"🏠 {room_name}", key=f"room_{room_id}", use_container_width=True):
                    st.session_state.selected_room = room
                    st.rerun()
    
    st.divider()
    
    # Add new room section
    st.subheader("Add New Room")
    with st.form("add_room_form"):
        room_name = st.text_input("Room Name", placeholder="e.g., Living Room")
        room_id = st.text_input("Room ID", placeholder="e.g., room_001", help="Unique identifier for the room")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Add Room", type="primary", use_container_width=True)
        with col2:
            if st.form_submit_button("Cancel", use_container_width=True):
                pass
        
        if submitted:
            if room_name and room_id:
                success, message = add_room(room_name, room_id)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Please fill in both Room Name and Room ID")

st.set_page_config(page_title="Smart Room Dashboard", layout="wide")

# Navigation logic
if not st.session_state.authenticated:
    show_login_screen()
    st.stop()

if st.session_state.selected_room is None:
    show_room_selection()
    st.stop()

# Initialize queue in session state (only after room selection)
if "mqtt_queue" not in st.session_state:
    st.session_state.mqtt_queue = queue.Queue()

# Start MQTT once (only after room selection)
if "mqtt_client" not in st.session_state:
    st.session_state.mqtt_client = start_mqtt(st.session_state.mqtt_queue)

# Process messages from MQTT queue (thread-safe)
mqtt_queue = st.session_state.mqtt_queue
while not mqtt_queue.empty():
    try:
        topic, payload = mqtt_queue.get_nowait()
        
        if topic == TOPIC_RELAY_STATE:
            st.session_state.latest["relay"] = payload.strip()
        elif topic == TOPIC_STATUS:
            try:
                data = json.loads(payload)
                st.session_state.latest["level"] = data.get("level", "INFO")
                st.session_state.latest["message"] = data.get("message", "")
                st.session_state.latest["mode"] = data.get("mode", st.session_state.latest["mode"])
                st.session_state.latest["temp"] = data.get("temp", st.session_state.latest["temp"])
                st.session_state.latest["hum"] = data.get("hum", st.session_state.latest["hum"])
                st.session_state.latest["ts"] = data.get("ts", time.time())

                if isinstance(st.session_state.latest["temp"], (int, float)) and isinstance(st.session_state.latest["hum"], (int, float)):
                    st.session_state.data_points.append({
                        "time": pd.to_datetime(st.session_state.latest["ts"], unit="s"),
                        "temp": float(st.session_state.latest["temp"]),
                        "hum": float(st.session_state.latest["hum"])
                    })
            except Exception as e:
                print(f"[dashboard] parse error: {e}")
    except queue.Empty:
        break
    except Exception as e:
        print(f"[dashboard] Error processing queue: {e}")

# Auto-refresh UI every 1 second
st_autorefresh(interval=1000, key="sr_refresh")

# Dashboard header with room info and navigation
col_header1, col_header2 = st.columns([3, 1])
with col_header1:
    room_name = st.session_state.selected_room.get("name", st.session_state.selected_room.get("id", "Unknown"))
    st.title(f"Smart Room Monitor - {room_name}")

with col_header2:
    st.write("")  # Spacing
    if st.button("← Back to Rooms", use_container_width=True):
        st.session_state.selected_room = None
        st.rerun()
    
    st.caption(f"User: {st.session_state.username}")

latest = st.session_state.latest
data_points = st.session_state.data_points

level = latest["level"]
msg = latest["message"] or "Waiting for system messages..."

if level == "ALARM":
    st.error(f"ALARM: {msg}")
elif level == "WARNING":
    st.warning(f"WARNING: {msg}")
else:
    st.success(f"INFO: {msg}")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Temperature (°C)", "-" if latest["temp"] is None else f"{latest['temp']}")
c2.metric("Humidity (%)", "-" if latest["hum"] is None else f"{latest['hum']}")
c3.metric("Mode", latest["mode"] if latest["mode"] else "-")
c4.metric("Relay", latest["relay"])

st.divider()

# System Control Section
st.subheader("System Control")

# Check timer if enabled (runs every refresh)
if st.session_state.timer_enabled:
    now = datetime.now().time()
    timer_start = st.session_state.timer_start
    timer_end = st.session_state.timer_end
    
    if timer_start <= timer_end:
        # Normal case: start < end (same day)
        in_timer_range = timer_start <= now <= timer_end
    else:
        # Overnight case: start > end (spans midnight)
        in_timer_range = now >= timer_start or now <= timer_end
    
    # Auto control based on timer
    if in_timer_range and not st.session_state.system_enabled:
        st.session_state.mqtt_client.publish(TOPIC_MODE, "auto")
        st.session_state.system_enabled = True
    elif not in_timer_range and st.session_state.system_enabled and st.session_state.timer_enabled:
        st.session_state.mqtt_client.publish(TOPIC_MODE, "manual")
        st.session_state.system_enabled = False

col1, col2 = st.columns([1, 1])

with col1:
    st.write("**Manual Control**")
    if st.button("🟢 Turn ON", type="primary", disabled=st.session_state.system_enabled):
        st.session_state.mqtt_client.publish(TOPIC_MODE, "auto")
        st.session_state.system_enabled = True
        st.rerun()
    
    if st.button("🔴 Turn OFF", type="secondary", disabled=not st.session_state.system_enabled):
        st.session_state.mqtt_client.publish(TOPIC_MODE, "manual")
        st.session_state.system_enabled = False
        st.rerun()
    
    if st.session_state.system_enabled:
        st.success("System is ON")
    else:
        st.info("System is OFF")

with col2:
    st.write("**Timer Control**")
    timer_enabled = st.checkbox("Enable Timer", value=st.session_state.timer_enabled)
    st.session_state.timer_enabled = timer_enabled
    
    if timer_enabled:
        timer_start = st.time_input("Start Time", value=st.session_state.timer_start)
        timer_end = st.time_input("End Time", value=st.session_state.timer_end)
        st.session_state.timer_start = timer_start
        st.session_state.timer_end = timer_end
        
        # Show timer status
        now = datetime.now().time()
        if timer_start <= timer_end:
            in_timer_range = timer_start <= now <= timer_end
        else:
            in_timer_range = now >= timer_start or now <= timer_end
        
        if in_timer_range:
            st.success(f"⏰ Timer Active (until {timer_end.strftime('%H:%M')})")
        else:
            st.info(f"⏰ Timer Inactive (starts at {timer_start.strftime('%H:%M')})")
    else:
        st.info("Timer is disabled")

st.divider()

if len(data_points) > 2:
    df = pd.DataFrame(list(data_points)).set_index("time")
    st.line_chart(df[["temp", "hum"]])
else:
    st.info("Waiting for telemetry... run sensor_emulator + app_manager.")
