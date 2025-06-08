from flask import Blueprint, render_template, request, jsonify
from app.models.alarm import Alarm, Memo
from app import db
from datetime import datetime
import requests

main_bp = Blueprint('main', __name__)

# ----------------------------
# 1. Main Page
# ----------------------------
@main_bp.route('/')
def index():
    return render_template('index.html')


# ----------------------------
# 2. Alarm API
# ----------------------------
@main_bp.route('/api/alarms', methods=['GET'])
def get_alarms():
    alarms = Alarm.query.all()
    return jsonify([alarm.to_dict() for alarm in alarms])

@main_bp.route('/api/alarms', methods=['POST'])
def create_alarm():
    data = request.json
    alarm = Alarm(
        time=data['time'],
        label=data.get('label'),
        days=data.get('days'),
        specific_date=_parse_date(data.get('specific_date')),
        is_active=True
    )
    db.session.add(alarm)
    db.session.commit()
    return jsonify(alarm.to_dict()), 201

@main_bp.route('/api/alarms/<int:alarm_id>', methods=['PUT'])
def update_alarm(alarm_id):
    alarm = Alarm.query.get_or_404(alarm_id)
    data = request.json
    alarm.time = data.get('time', alarm.time)
    alarm.label = data.get('label', alarm.label)
    alarm.days = data.get('days', alarm.days)
    alarm.specific_date = _parse_date(data.get('specific_date')) or alarm.specific_date
    alarm.is_active = data.get('is_active', alarm.is_active)
    db.session.commit()
    return jsonify(alarm.to_dict())

@main_bp.route('/api/alarms/<int:alarm_id>', methods=['DELETE'])
def delete_alarm(alarm_id):
    alarm = Alarm.query.get_or_404(alarm_id)
    db.session.delete(alarm)
    db.session.commit()
    return '', 204

# Temporary Alarm Creation (with specific date only)
@main_bp.route('/api/alarms/temp', methods=['POST'])
def create_temp_alarm():
    data = request.json
    time = data.get('time')
    date = _parse_date(data.get('date'))
    if not time or not date:
        return jsonify({'error': 'Invalid input'}), 400

    temp_alarm = Alarm(time=time, specific_date=date, is_active=True)
    db.session.add(temp_alarm)
    db.session.commit()
    return jsonify(temp_alarm.to_dict()), 201

# Temporary Alarm Deletion
@main_bp.route('/api/alarms/temp', methods=['DELETE'])
def delete_temp_alarm():
    data = request.json
    time = data.get('time')
    date = _parse_date(data.get('date'))
    if not time or not date:
        return jsonify({'error': 'Invalid input'}), 400

    alarm = Alarm.query.filter_by(time=time, specific_date=date).first()
    if alarm:
        db.session.delete(alarm)
        db.session.commit()
        return jsonify({'message': 'Deleted'}), 200
    else:
        return jsonify({'error': 'Not found'}), 404


# ----------------------------
# 3. Memo API
# ----------------------------
@main_bp.route('/api/memos', methods=['GET'])
def get_memos():
    memos = Memo.query.all()
    return jsonify([memo.to_dict() for memo in memos])

@main_bp.route('/api/memos', methods=['POST'])
def create_memo():
    data = request.json
    memo = Memo(
        content=data['content'],
        date=_parse_date(data.get('date'))
    )
    db.session.add(memo)
    db.session.commit()
    return jsonify(memo.to_dict()), 201

@main_bp.route('/api/memos/<int:memo_id>', methods=['PUT'])
def update_memo(memo_id):
    memo = Memo.query.get_or_404(memo_id)
    data = request.json
    memo.content = data.get('content', memo.content)
    memo.date = _parse_date(data.get('date')) or memo.date
    db.session.commit()
    return jsonify(memo.to_dict())

@main_bp.route('/api/memos/<int:memo_id>', methods=['DELETE'])
def delete_memo(memo_id):
    memo = Memo.query.get_or_404(memo_id)
    db.session.delete(memo)
    db.session.commit()
    return '', 204


# ----------------------------
# 4. Weather API
# ----------------------------

@main_bp.route('/api/weather', methods=['GET'])
def get_weather():
    try:
        # Get Weather Information : Open Meteo API | Asia/Seoul
        weather_response = requests.get("https://api.open-meteo.com/v1/forecast", params={
            "latitude": 37.5665,
            "longitude": 126.9780,
            "current": "temperature_2m,weather_code",
            "timezone": "Asia/Seoul"
        }, timeout=10)
        weather_response.raise_for_status()
        weather_data = weather_response.json().get("current", {})
        
        # Convert weather_code to integer
        weather_code = weather_data.get('weather_code', 0)
        try:
            weather_code = int(weather_code)
        except Exception:
            weather_code = 0
        
        def get_weather_description(code):
            weather_codes = {
                0: "Clear", 1: "Mostly Clear", 2: "Partly Cloudy", 3: "Cloudy",
                45: "Fog", 48: "Freezing Fog",
                51: "Light Drizzle", 53: "Drizzle", 55: "Heavy Drizzle",
                61: "Light Rain", 63: "Rain", 65: "Heavy Rain",
                71: "Light Snow", 73: "Snow", 75: "Heavy Snow",
                80: "Rain Showers", 81: "Heavy Showers", 95: "Thunderstorm"
            }
            return weather_codes.get(code, f"Unknown ({code})")
        
        # Air Quality Information
        try:
            air_response = requests.get("https://air-quality-api.open-meteo.com/v1/air-quality", params={
                "latitude": 37.5665,
                "longitude": 126.9780,
                "current": "pm2_5,pm10"
            }, timeout=10)
            dust_info = "Unavailable"
            if air_response.status_code == 200:
                air_data = air_response.json().get("current", {})
                pm2_5 = air_data.get("pm2_5")
                # print("air_data: ", air_data)  // Debugging line
                if pm2_5 is not None:
                    if pm2_5 <= 15:
                        dust_info = f"Good ({int(pm2_5)})"
                    elif pm2_5 <= 35:
                        dust_info = f"Moderate ({int(pm2_5)})"
                    elif pm2_5 <= 75:
                        dust_info = f"Poor ({int(pm2_5)})"
                    else:
                        dust_info = f"Very Poor ({int(pm2_5)})"
        except Exception as e:
            print("air-quality API error:", e)
            dust_info = "Unavailable"
        
        temperature = weather_data.get('temperature_2m')
        
        return jsonify({
            "temperature": f"{temperature}°C" if temperature is not None else "N/A",
            "weather": get_weather_description(weather_code),
            "dust": dust_info
        })
        
    except Exception as e:
        print(f"Weather API error: {e}")
        return jsonify({
            "temperature": "N/A",
            "weather": "Error occurred",
            "dust": "N/A"
        })

# ----------------------------
# 내부 유틸
# ----------------------------
def _parse_date(date_str):
    if date_str:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return None
    return None