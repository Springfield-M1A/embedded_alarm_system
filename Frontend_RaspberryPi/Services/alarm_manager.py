import requests
from datetime import datetime

API_BASE_URL = "http://127.0.0.1:5000"

def get_regular_alarms():
    today = datetime.now()
    weekday = str(today.weekday())  # Monday=0, Sunday=6
    try:
        response = requests.get(f"{API_BASE_URL}/api/alarms")
        response.raise_for_status()
        alarms = response.json()
        result = []
        for alarm in alarms:
            if alarm['is_active'] and not alarm['specific_date']:
                if alarm['days'] and weekday in alarm['days'].split(','):
                    result.append((alarm['time'], alarm['label']))
        return result
    except:
        return []

def get_temporary_alarm():
    today = datetime.now().strftime('%Y-%m-%d')
    try:
        response = requests.get(f"{API_BASE_URL}/api/alarms")
        response.raise_for_status()
        alarms = response.json()
        upcoming = sorted(
            [a for a in alarms if a['is_active'] and a['specific_date'] and a['specific_date'] >= today],
            key=lambda x: (x['specific_date'], x['time'])
        )
        if upcoming:
            a = upcoming[0]
            return f"{a['time']} ({a['label']} - {a['specific_date']})"
        return None
    except:
        return None