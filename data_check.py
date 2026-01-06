from statistics import mean
from typing import Dict, Any

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

def format_values(values):
    device_id = values.get('device_id', 'unknown')
    return (f"[Device:{device_id}] "
            f"Temp:{values['temperature']:.1f}°C | "
            f"Hum:{values['humidity']:.1f}% | "
            f"CO2:{values['co2']} | "
            f"O2:{values['o2']} | "
            f"Light:{values['light']}")



def oof_values(parsed_data: Dict[str, Any]):#TODO dev tests to check if oot values function is working well
    """ 
        Check for out-of-range values and log warnings.

        Args:
            parsed_data: Dictionary with sensor readings

        Returns:
            Dictionary with validated sensor readings (None for out-of-range)
    """
    temp = parsed_data.get("temperature", 0)
    hum = parsed_data.get("humidity", 0)
    co2 = parsed_data.get("co2", 0)
    o2 = parsed_data.get("o2", 0)
    light = parsed_data.get("light", 0)

    corrected = False
    corrected_fields = []

    # Out of range checks
    if not ( -10 <= temp <= 50):
        corrected = True
        corrected_fields.append("TEMP")
        temp = mean([-10,50])  # set to medium temp if oof
        print("temp oof set to medium:", temp)
    if not (10 <= hum <= 80):
        corrected = True
        corrected_fields.append("HUM")
        hum = mean([10,80])  # set to medium hum if oof
        print("hum oof set to medium:", hum)
    if not (200 <= co2 <= 4500):
        corrected = True
        corrected_fields.append("CO2")
        co2 = mean([200,4500])  # set to medium co2 if oof
        print("co2 oof set to medium:", co2)
    if not (5 <= o2 <= 30):
        corrected = True
        corrected_fields.append("O2")
        o2 = mean([5,30])  # set to medium o2 if oof
        print("o2 oof set to medium:", o2)
    if not (0 <= light <= 100):
        corrected = True
        corrected_fields.append("LIGHT")
        light = mean([0,50])  # set to medium light if oof
        print("light oof set to medium:", light)

    print("corrected fields:", corrected_fields)
    print("temp:", temp, "hum:", hum, "co2:", co2, "o2:", o2, "light:", light)

    cleaned = {
        "device_id": parsed_data.get("device_id", "default"),
        "temperature": temp,
        "humidity": hum,
        "co2": co2,
        "o2": o2,
        "light": light
    }

    # return cleaned
    return cleaned, corrected, corrected_fields

def threshold_management():
    pass



# def scale(value, min_v, max_v):
#     """
#         Scale value between 0 and 100
#         0 if value <= min_v
#         100 if value >= max_v

#         Args:
#             value: value to scale
#             min_v: minimum value
#             max_v: maximum value
#         Returns:
#             Scaled value between 0 and 100
#     """
#     return max(0, min(100, 100 * (value - min_v) / (max_v - min_v)))

