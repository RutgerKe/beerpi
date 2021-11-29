import logging
import board

# Debug level of info prints the temperature every minute, might be
# too much data
logging.getLogger().setLevel(logging.INFO)

# Currently no authentication on client level implemented
# Should be really easy to add
MQTT_HOST = "10.80.30.11"
MQTT_PORT = 1883
# We end both with a slash, and append the string of the topics below
# (FRIDGE_COOL_TOPIC and FRIDGE_HEAT_TOPIC) for the specific topics
MQTT_RELAY_READ = "raspberry/switch/"
MQTT_RELAY_PUBLISH = "raspberry/switch_state/"

# Listen for data from an ispinel-like device, usually in the beer
MQTT_BREWBRAIN_TOPIC = "float/ispindel_base"

# How often to read the temperature and send to mqtt server
# In seconds
TEMP_READ_INTERVAL = 60
#TEMP_MQTT_TOPIC = "raspberry/temperature/1"
BEER_TEMP_MQTT_TOPIC = "raspberry/temperature/1"

# Pin for PT100
PT100_PIN = board.D5

# The settings for the two relays
COOL_GPIO = 21
HEAT_GPIO = 20
FRIDGE_COOL_TOPIC = "1"
FRIDGE_HEAT_TOPIC = "2"
RELAY_OFF_PAYLOAD = b"1"
RELAY_ON_PAYLOAD = b"0"
