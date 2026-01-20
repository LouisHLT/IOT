from threading import Lock

STATION_CACHE = {}
STATION_LOCK = Lock()
STATIONS = {}

# SERIAL_PORT = "/dev/ttyACM0"
SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 9600
MAX_POINTS = 120              
UPDATE_MS = 200

ESP_URL = "http://192.168.1.53/api"
POLL_INTERVAL = 2  # seconds