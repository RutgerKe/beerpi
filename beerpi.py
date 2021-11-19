import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import logging
import time

# For reading the PT100
import digitalio
import adafruit_max31865
import board

# These are files
from config import *
from utils import *

GPIO.setmode(GPIO.BCM)

# Set the outputs for the relay, initialize as off
GPIO.setup(COOL_GPIO, GPIO.OUT)
GPIO.setup(HEAT_GPIO, GPIO.OUT)
GPIO.output(COOL_GPIO, GPIO.HIGH)
GPIO.output(HEAT_GPIO, GPIO.HIGH)

# Setup PT100 via MAX31865 board
spi = board.SPI()
cs = digitalio.DigitalInOut(PT100_PIN)
pt100 = adafruit_max31865.MAX31865(spi, cs)


def on_connect(client, userdata, flags, rc):
    logging.info("Connected with result code " + str(rc))
    # With the # suffix we subscribe to all subtopics
    client.subscribe(MQTT_RELAY_READ + "#")


def on_disconnect(client, userdata, rc=0):
    logging.info("Disconnected with result code " + str(rc))


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
    temperature = round(read_temp(), 2)
    beer_temperature = round(pt100.temperature, 2)
    logging.info("Temp: " + str(temperature) + ", PT100: " + beer_temperature)
    client.publish(TEMP_MQTT_TOPIC, str(temperature))
    client.publish(BEER_TEMP_MQTT_TOPIC, str(beer_temperature))
    time.sleep(TEMP_READ_INTERVAL)
