from flask import Flask, request, jsonify
import requests
import datetime
import dateutil.parser
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Read API key
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

app = Flask(__name__)

def get_coordinates(city_name):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={OPENWEATHER_API_KEY}"
    res = requests.get(url).json()
    if isinstance(res, list) and len(res) > 0:
        return res[0]['lat'], res[0]['lon']
    return None, None

def get_weather(city, session_date_str=None, user_date_str=None, date_period=None):
    lat, lon = get_coordinates(city)
    if not lat or not lon:
        return f"Could not find coordinates for '{city}'. Please check the city name."

    # Parse session date or fallback to today
    if session_date_str:
        try:
            session_date = dateutil.parser.parse(session_date_str).date()
        except Exception:
            session_date = datetime.date.today()
    else:
        session_date = datetime.date.today()

    # Handle date-period first if provided (forecast range)
    if date_period:
        try:
            start_date = dateutil.parser.parse(date_period['startDate']).date()
            end_date = dateutil.parser.parse(date_period['endDate']).date()
        except Exception:
            return "Could not parse date period."

        # Limit max 7 days forecast
        if (end_date - start_date).days > 7:
            end_date = start_date + datetime.timedelta(days=7)

        url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,alerts&units=metric&appid={OPENWEATHER_API_KEY}"
        res = requests.get(url).json()

        if 'daily' not in res:
            return f"Forecast data not available. API returned: {res}"

        responses = []
        for day in res['daily']:
            dt = datetime.date.fromtimestamp(day['dt'])
            if start_date <= dt <= end_date:
                desc = day['weather'][0]['description']
                temp = day['temp']['day']
                responses.append(f"{dt}: {desc}, {temp}°C")

        if responses:
            return f"Weather forecast for {city} from {start_date} to {end_date}:\n" + "\n".join(responses)
        else:
            return f"No forecast available in the range {start_date} to {end_date}."

    # Handle single-date or current weather
    forecast_date = session_date
    if user_date_str:
        try:
            forecast_date = dateutil.parser.parse(user_date_str).date()
        except Exception:
            forecast_date = session_date

    # Call One Call API once here for both current and forecast data
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,alerts&units=metric&appid={OPENWEATHER_API_KEY}"
    res = requests.get(url).json()

    if 'current' not in res or 'daily' not in res:
        return f"Weather data not available. API returned: {res}"

    if forecast_date < session_date:
        return "Sorry, I can only provide current and forecast weather for today or future dates."

    # If user asked for today's date or no date → return current weather
    if forecast_date == session_date or not user_date_str:
        current = res['current']
        desc = current['weather'][0]['description']
        temp = current['temp']
        return f"The current weather in {city} on {session_date} is {desc} with a temperature of {temp}°C."

    # Otherwise, provide forecast for the specific future date (max 7 days)
    start_date = session_date
    end_date = session_date + datetime.timedelta(days=7)

    if not (start_date <= forecast_date <= end_date):
        return f"Forecast is available only from {start_date} to {end_date}."

    for day in res['daily']:
        dt = datetime.date.fromtimestamp(day['dt'])
        if dt == forecast_date:
            desc = day['weather'][0]['description']
            temp = day['temp']['day']
            return f"Weather in {city} on {dt} is expected to be {desc} with a temperature of {temp}°C."

    return "Forecast not found for the selected date."

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()

    parameters = req.get('queryResult', {}).get('parameters', {})
    city = parameters.get('geo-city')
    user_date = parameters.get('date')  
    date_period = parameters.get('date-period')  

    session_timestamp = datetime.datetime.utcnow().isoformat()

    weather_info = get_weather(
        city,
        session_date_str=session_timestamp,
        user_date_str=user_date,
        date_period=date_period
    )
    return jsonify({"fulfillmentText": weather_info})

if __name__ == "__main__":
    app.run(port=5000, debug=True)
