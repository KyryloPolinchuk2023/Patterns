import datetime as dt
import json

import requests
from flask import Flask, jsonify, request

API_TOKEN = "Kp03041989!"


API_KEY = "71ee2fe0f3a10287944fd3e346ad43b8"
API_KEY2= "F2EQDPFWZYSALG86SHXXEVXX3"


app = Flask(__name__)


def get_weather(city):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params={"q":city, "appid": API_KEY}
    response = requests.request("GET", url, params=params)
    return json.loads(response.text)

def get_history_weather(location, date):
    base_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"
    location=location
    date=date
    url=f'{base_url}/{location}/{date}?key={API_KEY2}'
    response = requests.request("GET", url)
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
    date = json_data.get("date")

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

    weather_history = get_history_weather(location, date)["days"][0]

    main_history = weather_history["conditions"]
    description_history = weather_history["description"]
    temp_history = ((weather_history["temp"]-32)*5)/9
    temp_history = round(temp_history, 1)
    feelings_history = ((weather_history["feelslike"]-32)*5)/9
    feelings_history = round(feelings_history, 1)
    maxt_history = ((weather_history["tempmax"]-32)*5)/9
    maxt_history = round(maxt_history, 1)
    mint_history = ((weather_history["tempmin"]-32)*5)/9
    mint_history = round(mint_history, 1)
    maxfeeling_history = ((weather_history["feelslikemax"]-32)*5)/9
    maxfeeling_history = round(maxfeeling_history, 1)
    minfeeling_history = ((weather_history["feelslikemin"]-32)*5)/9
    minfeeling_history = round(minfeeling_history, 1)
    visibility_history = weather_history["visibility"]*1000
    wind_history = weather_history["windspeed"]
    wind_history = round(wind_history, 1)
    humidity_history = weather_history["humidity"]
    pressure_history = weather_history["pressure"]
    sunrise_history = weather_history["sunrise"]
    sunset_history = weather_history["sunset"]

    temp_diff=temp-temp_history
    temp_diff=round(temp_diff,1)

    if temp_diff>0:
        difference=f'Today weather is warmer on {temp_diff} degrees Celcius, than on {date}.'
    elif temp_diff<0:
        difference = f'Today weather is colder on {temp_diff} degrees Celcius, than on {date}.'
    else:
        difference = "Today we have the same weather!"


    result = {
        "requester_name": requester_name,
        "timestamp": dt.datetime.now().isoformat(),
        "location": location,
        "weather_datetime": weather_datetime,
        "date_for_compare": date,
        "weather_today":
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
                "visibility": str(int(visibility)) + " m",
                "sunrise": sunrise,
                "sunset": sunset
            },
        "weather_history":
            {
                "date": date,
                "main": main_history,
                "weather_description": description_history,
                "temp": str(temp_history) + " degrees Celcius",
                "max": str(maxt_history) + " degrees Celcius",
                "min": str(mint_history) + " degrees Celcius",
                "feelings": str(feelings_history) + " degrees Celcius",
                "maxfeeling": str(maxfeeling_history) + " degrees Celcius",
                "minfeeling": str(minfeeling_history) + " degrees Celcius",
                "wind": str(wind_history) + " kph",
                "humidity": str(humidity_history) + "%",
                "pressure": str(pressure_history) + " millibars",
                "visibility": str(visibility_history) + " m",
                "sunrise": sunrise_history,
                "sunset": sunset_history
            },
        "run_recomendation": run_recomendation,
        "difference": difference
    }

    return result
