from utils import add_reading, add_station, get_last_reading
from create_db import init_db

if __name__ == "__main__":
    init_db()

    station_id = add_station(
        room="bedroom",
    )
    print("New station id:", station_id)

    add_reading(
        station_id=station_id,
        temperature=21.5,
        humidity=45.2,
        co2=650,
        o2=20.8,
        light=120.0,
    )

    last = get_last_reading(station_id)
    print("Last reading:", last)
