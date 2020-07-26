Simple python program to control a fridge with a temperature sensor, cooling and heating. It is used to control fermenation of beer.

There is no intelligence in this script, it simply listens and publishes on an MQTT server. The actual logic is handled by another program, in this case home assistant.

# Hardware:
- Relay module (4CH, only using 2 channels)
- DS18B20 (temperature sensor)
- Raspberry pi zero W

## Connecting

The Pi has the following GPIO connections:
- Relay channel 1 (cooling): 20
- Relay channel 2 (heating): 21
- DS18B20 on the one wire interface: pin 4

The DS18B20 is connected with a resistor, simply as in the [Adafruit tutorial](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/hardware)

# Setup OS
Simply flash a raspbian or something to a SD card, to make sure it boots headless:
- Create a wpa_supplicant.conf, as explained in the [Raspberry Pi Documentation](https://www.raspberrypi.org/documentation/configuration/wireless/headless.md).
- Add an ssh file, again, see [the official docs](https://www.raspberrypi.org/documentation/remote-access/ssh/README.md).
- Activate the one-wire inteface, [some random website](https://www.raspberrypi-spy.co.uk/2018/02/enable-1-wire-interface-raspberry-pi/), I used method 3.

# This software
- Install some tools `apt install python3-pip git`
- Clone the repo `git clone https://github.com/RutgerKe/beerpi.git`, enter it `cd beerpi`
- Istall the dependencies `pip3 install -r requirements.txt`
- Copy the systemd service file: `sudo cp beerpi.service /lib/systemd/system/` and enable it `sudo systemctl enable beerpi`

The service script works on a raspberry pi default installation when cloning from the home folder. It also runs as the pi user, you might want to change those things.

## Configuration
Everything I've wanted to change is in the `config.py` file, just edit that and restart the service

## Debugging
A flaky connection or some other thing can cause the script to fail, you can checkout `systemctl status beerpi` to see if it is running, it usually shows a few last lines of output. Checkout the `/var/log/daemon.log` file for more output: `tail -f /var/log/daemon.log`

# Home Assitant
Currently using a setup with [Home Assistant](https://www.home-assistant.io/).

## Configuration

Home Assistant supports automatic discovery on MQTT messages, might add that in the future. Right now, just add the switches and sensor to the `configuration.yaml`:

```
switch:
  - platform: mqtt
    state_topic: "raspberry/switch_state/1"
    command_topic: "raspberry/switch/1"
    name: "Fridge on"
    state_on: "0"
    state_off: "1"
    payload_on: "0"
    payload_off: "1"
    icon: "mdi:fridge-outline"
  - platform: mqtt
    state_topic: "raspberry/switch_state/2"
    command_topic: "raspberry/switch/2"
    name: "Fridge heating"
    state_on: "0"
    state_off: "1"
    payload_on: "0"
    payload_off: "1"
    icon: "mdi:fridge"

sensor:
 - platform: mqtt
    state_topic: "raspberry/temperature/1"
    value_template: "{{ value }}"
    name: "Fridge temperature"
    unit_of_measurement: '°C'
```

## Automation

Most beers ferment around 20 degrees celcius, like the popular [Safale US-05](https://fermentis.com/en/fermentation-solutions/you-create-beer/safale-us-05/) which has an ideal temperature of 15-22 (according to the package, not the site). Because of that, in summer I have only the cooling rule enabled. Right now setting the target temperature needs an edit of 4 temperatures, another project on the todo-list: Simply make a target-temperature input and figure out the rules automatically.

```
- id: fridge_hot_start_cool
  alias: Fridge on when too hot
  - above: '19'
    entity_id: sensor.fridge_temperature
    platform: numeric_state
  action:
  - data:
      entity_id: switch.fridge_on
    service: switch.turn_on
- id: fridge_cold_stop_cool
  alias: Fridge off when cold enough
  trigger:
  - below: '16.0'
    entity_id: sensor.fridge_temperature
    platform: numeric_state
  action:
  - data:
      entity_id: switch.fridge_on
    service: switch.turn_off
```

Note that the ranges above are quite wide, the temperature sensor is currently outside of the fermentation barrel, and drops/rises a lot faster than the actual liquid. You probably need some time to figure out what temperatures work for your specific setup, to keep temperature changes to a minimum without turning on/off the fridge all the time.

The heating rules are similar, simply switch the values around a bit and use the entity `switch.fridge_heating`.

## User Interface
I've made a simple page which enables me to keep an eye on the temperature, quickly override cooling/heating and turn on or off the automations.

```
  - badges: []
    cards:
      - cards:
          - entities:
              - entity: sensor.fridge_temperature
              - entity: switch.fridge_on
              - entity: switch.fridge_heating
              - entity: automation.fridge_off_when_cold_enough
              - entity: automation.fridge_on_when_too_hot
            show_header_toggle: false
            type: entities
          - entities:
              - entity: sensor.fridge_temperature
            hours_to_show: 24
            refresh_interval: 30
            type: history-graph
        type: vertical-stack
    panel: false
    path: brew
    title: Brew
```

Which looks like this:

![BeerPi in Hass](hass_beerpi.png?raw=true)

*Data shown collected during development, fermentation should look different*

# Improving temperature readings

Even better results can be achieved by using a sensor in the barrel, I've had success with the [Brewbrain Float](https://www.brewbrain.nl/). For that I setup a slightly modified [iSpindle TCP server](https://github.com/avollkopf/iSpindel-TCP-Server) for the sensor to write to, so it can forward to both MQTT and the brewbrain website. In home assistant the rules can then be based on a combination of the different temperatures measured.
