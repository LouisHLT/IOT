import json

def parse_line(line: str):
    """
        Parse a line of JSON-formatted sensor data. 
        
        Args:
            line: A string containing JSON data from the sensor.

        Returns:
            A dictionary with parsed sensor values or None if parsing fails. 
    """
    try:
        data = json.loads(line)

        return {
            "device_id": "arduino_wired",
            "humidity": float(data["h"]),
            "temperature": float(data["t"]),
            "co2": float(data["co2"]),
            "o2": float(data["o2"]),
            "light": float(data["lux"]),
        }
    except Exception:
        return None