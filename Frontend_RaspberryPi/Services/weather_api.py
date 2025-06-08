import requests

API_BASE_URL = "http://127.0.0.1:5000"

def get_weather():
    try:
        response = requests.get(f"{API_BASE_URL}/api/weather", timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Validate response data and apply default values
        return {
            "weather": data.get("weather", "Unavailable"),
            "temperature": data.get("temperature", "N/A"),
            "dust": data.get("dust", "Unavailable")
        }
    except requests.exceptions.ConnectionError:
        # Flask server is not running
        return {"weather": "Server connection failed", "temperature": "N/A", "dust": "Unavailable"}
    except requests.exceptions.Timeout:
        # Request timeout
        return {"weather": "Request timed out", "temperature": "N/A", "dust": "Unavailable"}
    except requests.exceptions.RequestException:
        # Other network errors
        return {"weather": "Network error", "temperature": "N/A", "dust": "Unavailable"}
    except Exception:
        # Unexpected error
        return {"weather": "Unexpected error", "temperature": "N/A", "dust": "Unexpected error"}