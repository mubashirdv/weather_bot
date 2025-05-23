# 🌦️ Weather Bot

A Flask-based webhook for Dialogflow that provides weather updates using the OpenWeather API. It supports current weather, future forecasts (up to 7 days), and date-range forecasts.

## 📁 Project Structure

```

weather\_bot/
│
├── app.py             # Main Flask application
├── .env               # Environment variables (contains API key)
└── README.md          # This documentation

````

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/weather_bot.git
cd weather_bot
````

### 2. Create a Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Add this `requirements.txt` (if needed):

```txt
flask
requests
python-dotenv
python-dateutil
```

### 4. Set Up Environment Variables

Create a `.env` file:

```env
OPENWEATHER_API_KEY=your_openweather_api_key
```

---

## 🚀 Running the App

```bash
python app.py
```

The app runs on `http://localhost:5000` by default.

---

## 🤖 Dialogflow Integration

This bot is intended to be used as a **Dialogflow webhook**:

### ➤ Endpoint:

```
POST http://<your-server>/webhook
```

### ➤ Expected JSON Payload (from Dialogflow):

```json
{
  "queryResult": {
    "parameters": {
      "geo-city": "London",
      "date": "2025-05-24",
      "date-period": {
        "startDate": "2025-05-23",
        "endDate": "2025-05-25"
      }
    }
  }
}
```

---

## 🔍 Features

### ✅ Current Weather

If no date is provided or the date is today, returns the current weather.

### ✅ Forecast for a Specific Date

If a future date (within 7 days) is provided, returns the weather forecast for that day.

### ✅ Forecast for a Date Range

If a `date-period` is provided, returns daily forecasts within that range (max 7 days).

---

## 🧠 Code Overview

### `get_coordinates(city_name)`

Fetches latitude and longitude for a given city using OpenWeather's Geocoding API.

### `get_weather(city, session_date_str, user_date_str, date_period)`

Handles all logic:

* Parses dates
* Validates forecast range (max 7 days)
* Calls OpenWeather's One Call API (v3.0)
* Returns weather info accordingly

### Flask Route: `/webhook`

Processes Dialogflow POST requests:

* Extracts city, date, and date-period
* Calls `get_weather()` and returns response as `fulfillmentText`

---

## 🔐 API Used

* **OpenWeather API**

  * Geocoding API: to get coordinates from city name
  * One Call API 3.0: to get current and daily forecast

Register for a free API key at: [https://openweathermap.org/api](https://openweathermap.org/api)

---

## 📌 Notes

* Forecast is limited to 7 days (as per OpenWeather's free tier).
* Dates are parsed using `dateutil.parser` to handle flexible formats.
* The app uses `.env` for API key security.

