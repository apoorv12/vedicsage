# app.py
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import swisseph as swe

app = Flask(__name__)

@app.route('/api/astro', methods=['POST'])
def calculate_chart():
    data = request.get_json()

    location_name = data.get('location_name')
    latitude = float(data.get('latitude'))
    longitude = float(data.get('longitude'))
    date_str = data.get('date')  # e.g., "2025-07-14"
    time_str = data.get('time')  # e.g., "10:34:00"

    # Convert IST to UTC
    ist_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    utc_time = ist_time - timedelta(hours=5, minutes=30)

    jd_ut = swe.julday(
        utc_time.year, utc_time.month, utc_time.day,
        utc_time.hour + utc_time.minute / 60 + utc_time.second / 3600
    )

    planets = {
        'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY,
        'Venus': swe.VENUS, 'Mars': swe.MARS, 'Jupiter': swe.JUPITER,
        'Saturn': swe.SATURN, 'Rahu': swe.MEAN_NODE, 'Ketu': swe.TRUE_NODE
    }

    planet_data = []
    for name, code in planets.items():
        pos = swe.calc_ut(jd_ut, code)
        planet_data.append({"name": name, "lon": round(pos[0][0], 2)})

    houses, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'P')
    ascendant = round(ascmc[0], 2)

    return jsonify({
        "location": location_name,
        "datetime_ist": ist_time.strftime("%Y-%m-%d %H:%M:%S"),
        "datetime_utc": utc_time.strftime("%Y-%m-%d %H:%M:%S"),
        "ascendant": ascendant,
        "planets": planet_data
    })

if __name__ == '__main__':
    app.run()
