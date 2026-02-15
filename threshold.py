import os
import yagmail
from dotenv import load_dotenv
from datetime import datetime

from logger import logger
from config import ALERT_STATE, ALERT_COOLDOWN, STATION_LOCK

load_dotenv()

DEST = os.getenv('DEST')
SEND = os.getenv('SEND')
SUBJECT = None
CONTENTS = None


"""
VALUES MIN, MAX FOR ERROR/SMOOTHING

-10 < Tem < 50
10% < Hum < 80%
200ppm < CO2 < 4500ppm
5% < O2 < 30%
0% < light < 100%
"""

"""
VALUES THRESHOLD

HUM
40% < Hum (50%) < 60%

TEMP
confort range: 18° < temp < 24°
bedroom range: 16° < temp < 19°
living room range: 20° < temp < 22°

CO2
< 600 ppm: Excellent ventilation.
600-1000 ppm: Good to fair ventilation; typical for occupied indoor spaces.
> 1000 ppm: Poor air quality, associated with drowsiness, stuffiness, and poor concentration.
> 2000 ppm: Headaches, sleepiness, poor focus, increased heart rate, slight nausea. 

O2
20.9%: Normal, fresh air.
19.5%: Minimum "safe level" for entry into a confined space or workplace without respiratory protection. Adverse physiological effects may not be noticeable at first.
16% - 19%: Impaired thinking and coordination, increased breathing and pulse rates, and reduced ability to work strenuously.
10% - 14%: Poor judgment, abnormal fatigue, emotional upset, and impaired respiration.
6% - 10%: Nausea, vomiting, lethargy, loss of consciousness, and potentially permanent heart damage.
Less than 6%: Convulsions, cessation of breathing, cardiac arrest, and death within a few minutes. 

LIGHT
General Home Areas (Living Room, Bedroom): 5–20% (50-200 lux), with flexibility
"""

def check_threshold(values):
    """
        Check sensor values against predefined thresholds.

        Args:
            values: Dictionary with sensor readings (e.g., temp, hum, co2, o2, light)

        Returns:
            Tuple of (alert_key, subject, contents) if any threshold is exceeded, else (None, None, None)
    """
    # TEMP
    if values["temp"] > 24 or values["temp"] < 18:
        logger.warning("THRESHOLD WARNING TEMP")
        return(
            "temp",
            "Warning Temperature",
            f'Current temperature: {values["temp"]}°C, is over or below the reasonable threshold. Please adjust climate control.'
        )
    
    # HUM
    if values["hum"] > 60 or values["hum"] < 40:
        logger.warning("THRESHOLD WARNING HUM")
        return(
            "hum",
            "Warning Humidity",
            f'Current humidity: {values["hum"]}%, is over or below the reasonable threshold. Please adjust ventilation.'
        )
    
    # CO2 check - most critical first
    if values["co2"] > 2000:
        logger.warning("THRESHOLD DANGER CO2")
        return(
            "co2",
            "Danger CO2",
            f'Current CO2 is way over the reasonable threshold: {values["co2"]} ppm. Ventilate immediately!'
        )
    elif values["co2"] > 1000:
        logger.warning("THRESHOLD WARNING CO2")
        return(
            "co2",
            "Warning CO2",
            f'Current CO2 is over the reasonable threshold: {values["co2"]} ppm. Please ventilate.'
        )
    elif values["co2"] > 800:
        logger.warning("THRESHOLD SUGGESTION CO2")
        return(
            "co2",
            "CO2 Suggestion",
            f'The room could use ventilation (CO2: {values["co2"]} ppm). Ideal ventilation time is 15-20 minutes.'
        )
    elif values["co2"] > 600:
        logger.warning("THRESHOLD NOTICE CO2")
        return(
            "co2",
            "CO2 Notice",
            f'Current CO2 is slightly elevated: {values["co2"]} ppm. Consider ventilating the room.'
        )
    
    # O2 check - most critical first
    if values["o2"] < 10:
        logger.warning("THRESHOLD CRITICAL O2")
        return(
            "o2",
            "Critical O2 Level",
            f'Current O2 is critically low: {values["o2"]}%. Evacuate and ventilate immediately!'
        )
    elif values["o2"] < 16:
        logger.warning("THRESHOLD WARNING O2")
        return(
            "o2",
            "Warning O2",
            f'Current O2 is below safe threshold: {values["o2"]}%. Please ventilate immediately.'
        )
    elif values["o2"] < 19.5:
        logger.warning("THRESHOLD SUGGESTION O2")
        return(
            "o2",
            "O2 Suggestion",
            f'Current O2 is slightly low: {values["o2"]}%. Consider ventilating the room.'
        )
        
    # LIGHT
    if values["light"] > 20 or values["light"] < 5:
        logger.warning("THRESHOLD WARNING LIGHT")
        return(
            "light",
            "Warning Light",
            f'Current light in the room : {values["light"]}% is outside reasonable range. Please adjust lighting.'
        )

    # No thresholds exceeded
    return None, None, None

def manage_alert(device_id, alert_key, subject, contents, now=None):
    """
        Manage alert sending with cooldown logic.
        
        Args:
            device_id: The device identifier
            alert_key: The type of alert (e.g., 'temp', 'co2', 'o2')
            subject: Email subject
            contents: Email contents
            now: Current datetime (defaults to datetime.now())
    """
    with STATION_LOCK:
        if now is None:
            now = datetime.now()
        
        if alert_key:
            last = ALERT_STATE.get(device_id)

            should_send = False

            if last is None:
                # first alert ever
                should_send = True

            elif last["type"] != alert_key:
                # alert type changed (temp → co2, warning → danger)
                should_send = True

            elif now - last["last_sent"] > ALERT_COOLDOWN:
                # same alert, but cooldown expired
                should_send = True

            if should_send:
                send_email(device_id, subject=subject, contents=contents)
                ALERT_STATE[device_id] = {
                    "type": alert_key,
                    "last_sent": now
                }

        else:
            # everything back to normal → reset alert state
            ALERT_STATE.pop(device_id, None)


def send_email(value, subject=SUBJECT, contents=CONTENTS):
    """
        Send an email notification.

        Args:
            value: Value to include in the email subject
            subject: Email subject
            contents: Email contents
    """
    if not SEND or not DEST:
        raise RuntimeError("SEND or DEST email env vars are not set")

    yag = yagmail.SMTP({SEND: f'{value} Notification - Weather Station'})
    yag.send(
        to=DEST,
        subject=subject,
        contents=contents
    )
