# Embedded Alarm System with Motion Detection

- An embedded system that uses motion detection to deactivate alarms and display notes on Raspberry Pi System

## 1. Introduction

- This project is designed to create an embedded alarm system that utilizes motion detection to deactivate alarms and display notes on a Raspberry Pi.
- The system is built using Flask for the web interface and PyQt6 for the Raspberry Pi application.
- Lightweight CLI version for low-resource Rsapberry Pi setups
  - (Actually just because my Raspberry 3 didn't work so I had to make an alternative version)

## 2. Features

- Motion detection or manual input to deactivate alarms.
- Display notes on the Raspberry Pi screen.
- Web interface to manage alarms and notes.

## 3. Requirements

- Raspberry Pi 4 or higher
- Python 3.11
- Flask

> [!Warning]
>
> - We've tested using Raspberry Pi 3, but it didn't work while installing the required packages.
>   - The following packages could not be installed :
>     - `PyQt6`
>     - `mediapipe`
> - Therefore, we recommend using Raspberry Pi 4 or higher.

## 4. Installation and Setup

### 4-1. Virtual Environment Setup

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

### 4-2. Install Required Packages

- 3 separate `requirements_*.txt` files are provided for different parts of the project:
  - `requirements_backend.txt`: For the Flask backend server.
  - `requirements_frontendCLI.txt`: For the Raspberry Pi CLI application.
  - `requirements_frontendGUI.txt`: For the Raspberry Pi GUI application.
- You can install the required packages for each part using the following command:

```bash
pip install -r requirements_backend.txt
pip install -r requirements_frontendCLI.txt
pip install -r requirements_frontendGUI.txt
```

### 4-2. Backend Server Setup (Flask)

```bash
FLASK_APP=Backend_Flask/run.py FLASK_ENV=development flask run
```

### 4-3. Raspberry Pi Application Setup (GUI)

```bash
python Frontend_RaspberryPi/main_GUI.py
```

### 4-4. Raspberry Pi Application Setup (CLI)

```bash
python Frontend_RaspberryPi/main_CLI.py
```

## 5. Motion Detection

- GUI (`main_GUI.py`):

  - Uses `mediapipe` for motion detection.
    - Requires :
      - PyQt6
      - mediapipe
      - Camera Access

- CLI (`main_CLI.py`):

  - Uses `OpenCV Heuristic Motion Detection` for motion detection.
  - (Also because of the Raspberry Pi 3 issue...)
  - Computes frame differences to detect motion
    - Requires:
      - OpenCV
      - Camera Access

- Also just a single `Enter` key press can be used to deactivate the alarm

## 6. Notes

- Used Open-Meteo API to get the weather data.
  - https://open-meteo.com/en/docs

## 7. Server IP Configuration (Optional)

- To update the `API_BASE_URL` for clients:

```bash
python set_server_ip.py
```

- This script will update all related files automatically.
  - The files that will be updated are :
    - `Frontend_RaspberryPi/Screens/alarm_set_screen.py`
    - `Frontend_RaspberryPi/Services/alarm_manager.py`
    - `Frontend_RaspberryPi/Services/memo_loader.py`
    - `Frontend_RaspberryPi/Services/weather_api.py`
    - `Frontend_RaspberryPi/main_CLI.py`

## 8. License

- This project is licensed under the MIT License.
- [LICENSE](LICENSE.md)
