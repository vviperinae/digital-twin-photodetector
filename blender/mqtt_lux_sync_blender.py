"""
mqtt_lux_sync_blender.py

import sys
import os

# Manually add the folder where pip actually installed paho-mqtt,
# since Blender's bundled Python ignores the user site-packages folder by default.
_user_site = os.path.join(os.environ["APPDATA"], "Python", "Python313", "site-packages")
if _user_site not in sys.path:
    sys.path.append(_user_site)

import bpy
import json
import queue
import threading
import paho.mqtt.client as mqtt

# --- Team MQT contract (same as Node-RED / InfluxDB / Omniverse) ---
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_TOPIC = "photodetector/team7/reading"
LIGHT_ENERGY_SCALE = 5  # tune this until brightness changes are clearly visible

# --- Name of the light object in your Blender scene to drive ---
# Check the Outliner (top-right panel) for the exact name, e.g. "Light", "Point", "Sun"
LIGHT_OBJECT_NAME = "Light"

_lux_queue = queue.Queue()


def _on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[BlenderLuxSync] MQTT CONNECTED (rc={rc})")
        client.subscribe(MQTT_TOPIC)
        print(f"[BlenderLuxSync] Subscribed to '{MQTT_TOPIC}'")
    else:
        print(f"[BlenderLuxSync] MQTT CONNECT FAILED (rc={rc})")


def _on_disconnect(client, userdata, rc):
    print(f"[BlenderLuxSync] MQTT DISCONNECTED (rc={rc})")


def _on_message(client, userdata, msg):
    print(f"[BlenderLuxSync] Message: {msg.payload.decode()}")
    try:
        data = json.loads(msg.payload.decode())
        lux_value = float(data["lux"])
        _lux_queue.put(lux_value)
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"[BlenderLuxSync] Ignored malformed payload: {msg.payload} ({e})")


def _start_mqtt():
    print(f"[BlenderLuxSync] Connecting to {MQTT_BROKER}:{MQTT_PORT} ...")
    client = mqtt.Client()
    client.on_connect = _on_connect
    client.on_disconnect = _on_disconnect
    client.on_message = _on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()


def _drain_queue_and_update_light():
    """
    Called repeatedly by Blender's timer system. Must only touch bpy.data
    from here (Blender's API is not thread-safe) -- never from the MQTT
    thread directly.
    """
    latest = None
    while not _lux_queue.empty():
        latest = _lux_queue.get()

    if latest is not None:
        light_obj = bpy.data.objects.get(LIGHT_OBJECT_NAME)
        if light_obj is not None and light_obj.type == 'LIGHT':
            light_obj.data.energy = max(0.0, latest * LIGHT_ENERGY_SCALE)
            print(f"[BlenderLuxSync] Set '{LIGHT_OBJECT_NAME}' energy to {light_obj.data.energy}")
        else:
            print(f"[BlenderLuxSync] No light object named '{LIGHT_OBJECT_NAME}' found!")

    return 0.2  # re-run this function again in 0.2 seconds


# --- Entry point ---
print("[BlenderLuxSync] Starting MQTT lux sync...")
_mqtt_thread = threading.Thread(target=_start_mqtt, daemon=True)
_mqtt_thread.start()

bpy.app.timers.register(_drain_queue_and_update_light)
print("[BlenderLuxSync] Timer registered, MQTT thread started.")