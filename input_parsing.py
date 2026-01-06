def parse_line(line: str):
    """ 
        Parse a line of serial data into a dictionary.
        Expected format: "device_id,humidity,temperature,co2,o2,light" (with device_id)
        or "humidity,temperature,co2,o2,light" (legacy format without device_id)
        
        Args:
            line: A string from the serial port
        
        Returns:
            A dictionary with keys: device_id, humidity, temperature, co2, o2, light
    """
    parts = line.strip().split(",")
    
    # Handle format with device_id (6 parts)
    if len(parts) == 6:
        try:
            return {
                'device_id': parts[0],
                'humidity': float(parts[1]),
                'temperature': float(parts[2]),
                'co2': float(parts[3]),
                'o2': float(parts[4]),
                'light': float(parts[5])
            }
        except ValueError:
            return None
    
    # Handle legacy format without device_id (5 parts)
    elif len(parts) == 5:
        try:
            return {
                'device_id': 'arduino_wired',  # Default ID for wired Arduino
                'humidity': float(parts[0]),
                'temperature': float(parts[1]),
                'co2': float(parts[2]),
                'o2': float(parts[3]),
                'light': float(parts[4])
            }
        except ValueError:
            return None
    else:
        return None
    