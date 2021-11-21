import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import logging
import time

# These are files
from config import *
from utils import *
from metrics import *

GPIO.setmode(GPIO.BCM)

# Set the outputs for the realy, initialize as off
GPIO.setup(COOL_GPIO, GPIO.OUT)
GPIO.setup(HEAT_GPIO, GPIO.OUT)
GPIO.output(COOL_GPIO, GPIO.HIGH)
GPIO.output(HEAT_GPIO, GPIO.HIGH)

def on_connect(client, userdata, flags, rc):
    logging.info("Connected with result code " + str(rc))
    # With the # suffix we subscribe to all subtopics
    client.subscribe(MQTT_RELAY_READ + "#")
    client.subscribe(MQTT_BREWBRAIN_TOPIC)


def on_disconnect(client, userdata, rc=0):
    logging.info("Disconnected with result code " + str(rc))


def on_message(client, userdata, msg):
    logging.info(msg.topic + " " + str(msg.payload))

    if msg.topic == MQTT_BREWBRAIN_TOPIC:
        m = msg.payload
        ispindel_temp_gauge.set(m['temperature'])
        ispindel_gravity_gauge.set(m['gravity'])
        ispindel_angle_gauge.set(m['angle'])
        ispindel_battery_gauge.set(m['batery'])
        ispindel_rssi_gauge.set(m['RSSI'])
        return

    sensor_nr = msg.topic.split(MQTT_RELAY_READ)[1]
    if sensor_nr == FRIDGE_HEAT_TOPIC:
        pin = HEAT_GPIO
        gauge = fridge_heating_gauge
        counter = fridge_heating_counter
    elif sensor_nr == FRIDGE_COOL_TOPIC:
        pin = COOL_GPIO
        gauge = fridge_cooling_gauge
        counter = fridge_cooling_counter
    else:
        logging.error("Unknown topic")
        return

    if msg.payload == RELAY_OFF_PAYLOAD:
        pinstate = GPIO.HIGH
        gauge.set(0)
    elif msg.payload == RELAY_ON_PAYLOAD:
        pinstate = GPIO.LOW
        gauge.set(1)
        counter.inc()
    else:
        logging.error("Unknown payload")
        return

    GPIO.output(pin, pinstate)
    logging.info("Set pin " + str(pin) + " to " + str(pinstate))
    client.publish(MQTT_RELAY_PUBLISH + sensor_nr, msg.payload)


client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.connect(MQTT_HOST, MQTT_PORT, 60)

# Non-blocking loop
client.loop_start()

# So we can loop forever
while True:
    temperature = round(read_temp(), 2)
    logging.info("Temp: " + str(temperature))
    client.publish(TEMP_MQTT_TOPIC, str(temperature))
    fridge_temp_gauge.set(temperature)
    time.sleep(TEMP_READ_INTERVAL)
