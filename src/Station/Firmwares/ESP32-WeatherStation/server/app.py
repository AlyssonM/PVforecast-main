from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Adiciona CORS a todas as rotas

# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de dados
class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float, nullable=False)
    pressure = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    rainfall = db.Column(db.Float, nullable=False)
    altitude = db.Column(db.Float, nullable=False)
    wind_speed = db.Column(db.Float, nullable=False)
    wind_direction = db.Column(db.String(50), nullable=False)
    lux = db.Column(db.Float, nullable=False)
    battery_voltage = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

# Cria o banco de dados
with app.app_context():
    db.create_all()

@app.after_request
def apply_ngrok_header(response):
    response.headers['ngrok-skip-browser-warning'] = 'skip-browser-warning'
    return response

@app.route('/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    required_fields = ['temperature', 'pressure', 'humidity', 'altitude', 'rainfall', 'wind_speed', 'wind_direction', 'lux', 'battery_voltage', 'timestamp']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Invalid data"}), 400

    new_data = SensorData(
        temperature=data['temperature'],
        pressure=data['pressure'],
        humidity=data['humidity'],
        altitude=data['altitude'],
        rainfall=data['rainfall'],
        wind_speed=data['wind_speed'],
        wind_direction=data['wind_direction'],
        lux=data['lux'],
        battery_voltage=data['battery_voltage'],
        timestamp=datetime.strptime(data['timestamp'], '%Y-%m-%d %H:%M:%S')
    )
    db.session.add(new_data)
    db.session.commit()

    return jsonify({"message": "Data received and saved successfully"}), 200

@app.route('/data', methods=['GET'])
def get_data():
    start_str = request.args.get('start')
    end_str = request.args.get('end')

    if not start_str or not end_str:
        return jsonify({"error": "Please provide start and end dates in the format 'YYYY-MM-DD HH:MM:SS'"}), 400

    try:
        start = datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S')
        end = datetime.strptime(end_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    data = SensorData.query.filter(SensorData.timestamp >= start, SensorData.timestamp <= end).all()

    # Filtrando a resolução de 15 minutos
    filtered_data = []
    current_time = start
    while current_time <= end:
        interval_data = list(filter(lambda d: d.timestamp >= current_time and d.timestamp < current_time + timedelta(minutes=15), data))
        if interval_data:
            filtered_data.append(interval_data[0])  # Pega o primeiro dado do intervalo de 15 minutos
        current_time += timedelta(minutes=15)

    result = [
        {
            "temperature": d.temperature,
            "pressure": d.pressure,
            "humidity": d.humidity,
            "altitude": d.altitude,
            "rainfall": d.rainfall,
            "wind_speed": d.wind_speed,
            "wind_direction": d.wind_direction,
            "lux": d.lux,
            "battery_voltage": d.battery_voltage,
            "timestamp": d.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        } for d in filtered_data
    ]

    response = jsonify(result)
    return response, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
