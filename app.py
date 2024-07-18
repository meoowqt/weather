from flask import Flask, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///weather.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Search(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False)
    count = db.Column(db.Integer, default=1)

    def __repr__(self) -> str:
        return f"History {self.city}"


with app.app_context():
    db.create_all()

app.secret_key = "NOSECRET"
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
            search = Search.query.filter_by(city=city_name).first()
            if search:
                search.count += 1
            else:
                search = Search(city=city_name)
                db.session.add(search)
            db.session.commit()
            searches = Search.query.order_by(Search.count.desc()).all()
            session["last_city"] = city_name
            return render_template(
                "index.html", weather_data=weather_data, searches=searches
            )
        else:
            flash("Город не найден", "error")
    searches = Search.query.order_by(Search.count.desc()).all()
    last_city = session.get("last_city", None)
    return render_template("index.html", searches=searches, last_city=last_city)


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
        99: "Сильная гроза с градом",
    }
    return codes.get(code, "Неизвестный код погоды")


def get_weather(latitude, longitude, city):
    response = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,apparent_temperature,precipitation,weather_code"
    )
    if response.status_code == 200:
        weather_data = response.json()
        weather = {
            "city": city,
            "temperature": weather_data["current"]["temperature_2m"],
            "precipitation": str(
                int(weather_data["current"].get("precipitation", "N/A")) * 100
            ),
            "feel_like": weather_data["current"]["apparent_temperature"],
            "weather": decode_weather_code(weather_data["current"].get("weather_code")),
        }
        return weather
    return None


if __name__ == "__main__":
    app.run(debug=True)
