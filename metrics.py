from prometheus_client import Gauge, Counter, start_http_server

mqtt_server_connected = Counter('mqtt_server_connected', 'Total times connected to MQTT server')

beer_temp_gauge = Gauge('fridge_temp', 'Temperature inside the fermentation bucket')
fridge_temp_gauge = Gauge('fridge_temp', 'Temperature inside the fermentation fridge')
fridge_cooling_gauge = Gauge('fridge_cooling_status', 'Fridge cooling turned on or not')
fridge_cooling_counter = Counter('fridge_cooling_total', 'Total times fridge cooling turned on')
fridge_heating_gauge = Gauge('fridge_heating_status', 'Fridge heating turned on or not')
fridge_heating_counter = Counter('fridge_heating_total', 'Total times fridge heating turned on')

ispindel_temp_gauge = Gauge('ispindel_temp', 'Temperature according to the ispindel inside fermentation bucket')
ispindel_gravity_gauge = Gauge('ispindel_sg', 'Gravity according to the ispindel inside fermentation bucket')
ispindel_angle_gauge = Gauge('ispindel_angle', 'Angle of to the ispindel inside fermentation bucket')
ispindel_battery_gauge = Gauge('ispindel_battery', 'Battery of the ispindel inside fermentation bucket')
ispindel_rssi_gauge = Gauge('ispindel_rssi', 'WiFi RSSI of the ispindel inside fermentation bucket')


# Start a server to expose prometheus-style metrics
start_http_server(8000)