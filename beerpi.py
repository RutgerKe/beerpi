import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import logging
import time

# These are files
from config import *
from utils import *

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


def on_disconnect(client, userdata, rc=0):
    logging.info("Disconnected with result code " + str(rc))
    client.loop_stop()


def on_message(client, userdata, msg):
    logging.info(msg.topic + " " + str(msg.payload))

    sensor_nr = msg.topic.split(MQTT_RELAY_READ)[1]
    if sensor_nr == FRIDGE_HEAT_TOPIC:
        pin = HEAT_GPIO
    elif sensor_nr == FRIDGE_COOL_TOPIC:
        pin = COOL_GPIO
    else:
        logging.error("Unknown topic")
        return

    if msg.payload == RELAY_OFF_PAYLOAD:
        pinstate = GPIO.HIGH
    elif msg.payload == RELAY_ON_PAYLOAD:
        pinstate = GPIO.LOW
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
    temperature = read_temp()
    logging.info("Temp: " + str(temperature))
    client.publish(TEMP_MQTT_TOPIC, str(temperature))
    time.sleep(TEMP_READ_INTERVAL)
