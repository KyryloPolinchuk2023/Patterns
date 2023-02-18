import datetime as dt
import json

import requests
from flask import Flask, jsonify, request

API_TOKEN = "Kp03041989!"


API_KEY = "71ee2fe0f3a10287944fd3e346ad43b8"

app = Flask(__name__)


def get_weather(city):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params={"q":city, "appid": API_KEY}
    response = requests.request("GET", url, params=params)
    return json.loads(response.text)

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>Kyrylo Polinchuk HomeWork</h2></p>"


@app.route(
    "/content/api/v1/integration/generate",
    methods=["PUT"],
)
def weather_endpoint():
    json_data = request.get_json()

    if json_data.get("token") is None:
        raise InvalidUsage("token is required", status_code=400)

    token = json_data.get("token")

    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)

    location = json_data.get("location")
    city = location.split(",")[0]

    requester_name=json_data.get("requester_name")

    weather = get_weather(city)

    main = weather["weather"][0]["main"]
    description = weather["weather"][0]["description"]
    temp = weather["main"]["temp"] - 273.15
    temp = round(temp, 1)
    feelings = weather["main"]["feels_like"] - 273.15
    feelings = round(feelings, 1)
    maxt = weather["main"]["temp_max"] - 273.15
    maxt = round(maxt, 1)
    mint = weather["main"]["temp_min"] - 273.15
    mint = round(mint, 1)
    visibility = weather["visibility"]
    wind = weather["wind"]["speed"] * 3.6
    wind = round(wind, 1)
    humidity = weather["main"]["humidity"]
    pressure = weather["main"]["pressure"]
    sunrise = dt.datetime.fromtimestamp(weather["sys"]["sunrise"]).strftime('%H:%M:%S')
    sunset = dt.datetime.fromtimestamp(weather["sys"]["sunset"]).strftime('%H:%M:%S')
    weather_datetime = dt.datetime.fromtimestamp(weather["dt"]).strftime("%m/%d/%Y, %H:%M:%S")

    windstop = "Please don`t forget windstop jacket!"
    if feelings < -10:
        clothes = "Please, put on 3 layer of clothes!"
    elif -10 <= feelings <= 5:
        clothes = "Please, put on 2 layer of clothes!"
    elif 5 < feelings < 15:
        clothes = "Please, put on 1 layer of clothes!"
    elif feelings >= 15:
        clothes = "Please, put on shorts and T-shirt!"
    if wind > 15:
        run_recomendation = clothes + " " + windstop
    else:
        run_recomendation = clothes

    result = {
        "requester_name": requester_name,
        "timestamp": dt.datetime.now().isoformat(),
        "location": location,
        "weather_datetime": weather_datetime,
        "weather":
            {
                "main": main,
                "weather_description": description,
                "temp": str(temp) + " degrees Celcius",
                "max": str(maxt) + " degrees Celcius",
                "min": str(mint) + " degrees Celcius",
                "feelings": str(feelings) + " degrees Celcius",
                "wind": str(wind) + " kph",
                "humidity": str(humidity) + "%",
                "pressure": str(pressure) + " millibars",
                "visibility": str(visibility) + " m",
                "sunrise": sunrise,
                "sunset": sunset
            },
        "run_recomendation": run_recomendation
    }

    return result