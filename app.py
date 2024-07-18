from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)

app.secret_key = "NOSECRET;("
API_NINJAS_KEY = "19XnYwxNhqsNSVecc07O5g==ITo85sc4hjl01O0o"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        city_name = request.form["city"]
        coordinates = get_coordinates(city_name)
        if coordinates:
            weather_data = get_weather(
                coordinates["latitude"], coordinates["longitude"], city_name
            )
            return render_template("index.html", weather_data=weather_data)
        else:
            return render_template("index.html", error="City not found")
    return render_template("index.html")


def get_coordinates(city_name):
    url = f"https://api.api-ninjas.com/v1/geocoding?city={city_name}"
    headers = {"X-Api-Key": API_NINJAS_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data:
            coordinates = data[0]
            return {
                "latitude": coordinates["latitude"],
                "longitude": coordinates["longitude"],
            }
    return None

def decode_weather_code(code):
    codes = {
        0: "Ясное небо",
        1: "В основном ясно",
        2: "Переменная облачность",
        3: "Пасмурно",
        45: "Туман",
        48: "Оседающая изморозь",
        51: "Легкая морось",
        53: "Умеренная морось",
        55: "Интенсивная морось",
        56: "Легкая ледяная морось",
        57: "Интенсивная ледяная морось",
        61: "Небольшой дождь",
        63: "Умеренный дождь",
        65: "Сильный дождь",
        66: "Легкий ледяной дождь",
        67: "Сильный ледяной дождь",
        71: "Небольшой снег",
        73: "Умеренный снег",
        75: "Сильный снег",
        77: "Снежные зерна",
        80: "Слабые ливневые дожди",
        81: "Умеренные ливневые дожди",
        82: "Сильные ливневые дожди",
        85: "Слабые снежные ливни",
        86: "Сильные снежные ливни",
        95: "Гроза",
        96: "Гроза с градом",
        99: "Сильная гроза с градом"
    }
    return codes.get(code, "Неизвестный код погоды")

def get_weather(latitude, longitude, city):
    response = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
    )
    if response.status_code == 200:
        weather_data = response.json()
        weather = {
            "city": city,
            "temperature": weather_data["current_weather"]["temperature"],
            "precipitation": weather_data["current_weather"].get(
                "precipitation", "N/A"
            ),
            "weather": decode_weather_code(weather_data["current_weather"].get("weathercode", "N/A")),
        }
        return weather
    return None


if __name__ == "__main__":
    app.run(debug=True)
