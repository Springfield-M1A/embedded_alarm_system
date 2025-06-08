import requests
from datetime import datetime

API_BASE_URL = "http://127.0.0.1:5000"

def get_regular_memo():
    try:
        response = requests.get(f"{API_BASE_URL}/api/memos")
        response.raise_for_status()
        memos = response.json()
        regular_memos = [m for m in memos if not m['date']]
        sorted_memos = sorted(regular_memos, key=lambda x: x['created_at'])
        return sorted_memos[-1]['content'] if sorted_memos else ""
    except Exception as e:
        print(f"Error Occured : {e}")
        return ""

def get_date_memo():
    today = datetime.now().strftime('%Y-%m-%d')
    try:
        response = requests.get(f"{API_BASE_URL}/api/memos")
        response.raise_for_status()
        memos = response.json()
        for m in sorted(memos, key=lambda x: x['created_at'], reverse=True):
            if m['date'] == today:
                return m['content']
        return ""
    except:
        return ""

def get_date_memos():
    today = datetime.now().strftime('%Y-%m-%d')
    try:
        response = requests.get(f"{API_BASE_URL}/api/memos")
        response.raise_for_status()
        memos = response.json()
        future_memos = [m for m in memos if m['date'] and m['date'] >= today]
        result = {}
        for m in future_memos:
            if m['date'] not in result:
                result[m['date']] = []
            result[m['date']].append(m['content'])
        return {k: ' | '.join(v) for k, v in result.items()}
    except:
        return {}