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