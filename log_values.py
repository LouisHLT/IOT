import os
import logging
from datetime import datetime

LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configure logging
log_filename = os.path.join(LOG_DIR, f"arduino_data_{datetime.now().strftime('%Y%m%d')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def log_arduino_value(values):
    """
    Log sensor values to file
    
    Args:
        values: Dictionary containing sensor readings
    """
    log_message = (f"Temp:{values['temperature']:.1f}°C | "
                   f"Hum:{values['humidity']:.1f}% | "
                   f"CO2:{values['co2']} | "
                   f"O2:{values['o2']} | "
                   f"Light:{values['light']}")
    logger.info(log_message)

def log_warning(message, values=None):
    """
    Log a warning message
    
    Args:
        message: Warning message
        values: Optional dictionary of sensor values to include
    """
    if values:
        warning_msg = f"{message} - Values: {values}"
    else:
        warning_msg = message
    logger.warning(warning_msg)