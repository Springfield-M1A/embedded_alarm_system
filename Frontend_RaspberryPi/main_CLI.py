import os
import datetime
import requests
import cv2
import time

API_BASE_URL = "http://127.0.0.1:5000"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_regular_memo():
    try:
        r = requests.get(f"{API_BASE_URL}/api/memos")
        r.raise_for_status()
        memos = r.json()
        rmemos = [m for m in memos if not m['date']]
        rmemos = sorted(rmemos, key=lambda x: x['created_at'])
        return rmemos[-1]['content'] if rmemos else ""
    except:
        return ""

def get_today_memo():
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    try:
        r = requests.get(f"{API_BASE_URL}/api/memos")
        r.raise_for_status()
        memos = r.json()
        for m in sorted(memos, key=lambda x: x['created_at'], reverse=True):
            if m['date'] == today:
                return m['content']
        return ""
    except:
        return ""

def camera_available():
    cap = cv2.VideoCapture(0)
    available = cap.isOpened()
    cap.release()
    return available

def detect_stretch_motion_with_opencv(min_duration_seconds=1.5, warmup_frames=20, sensitivity=1200000):
    print("[Stretch Detection] Initializing camera...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[Error] Camera could not be opened.")
        return False

    time.sleep(2.0)
    prev_gray = None
    motion_start_time = None
    warmup = warmup_frames

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[Error] Failed to read from camera.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if warmup > 0:
            warmup -= 1
            prev_gray = gray
            continue

        if prev_gray is None:
            prev_gray = gray
            continue

        diff = cv2.absdiff(prev_gray, gray)
        score = diff.sum()
        prev_gray = gray

        print(f"[Motion Score] {score:.2f}")

        if score > sensitivity:
            if motion_start_time is None:
                motion_start_time = time.time()
            elif time.time() - motion_start_time >= min_duration_seconds:
                cap.release()
                print("\n[Success] Stretch confirmed.\n")
                return True
        else:
            motion_start_time = None

    cap.release()
    print("\n[Info] Stretch not detected.\n")
    return False

def display_alarm_screen():
    clear()
    now = datetime.datetime.now()
    print("[Alarm Screen]\n")
    print("##################")
    print("Wake up!")
    print("##################\n")
    print(f"Time: {now.strftime('%H:%M')}")
    print(f"Regular Memo: {get_regular_memo()}")
    print(f"Today's Memo: {get_today_memo()}")

    print("\n[enter / motion]: ", end="")
    choice = input().strip().lower()

    if choice == "enter":
        print("\n[Manual] Alarm deactivated.\n")
    elif choice == "motion":
        if camera_available():
            if detect_stretch_motion_with_opencv():
                print("\n[Motion] Alarm deactivated by stretch.\n")
            else:
                input("\n[Fail] Stretch not detected. Press Enter to dismiss manually.")
        else:
            input("\n[Error] Camera not available. Press Enter to return.")
    else:
        input("\n[Unknown input] Press Enter to return.")

def get_weather():
    try:
        r = requests.get(f"{API_BASE_URL}/api/weather", timeout=5)
        r.raise_for_status()
        d = r.json()
        return {
            "weather": d.get("weather", "N/A"),
            "temperature": d.get("temperature", "N/A"),
            "dust": d.get("dust", "N/A")
        }
    except:
        return {"weather": "N/A", "temperature": "N/A", "dust": "N/A"}

def get_regular_alarms():
    weekday = str(datetime.datetime.now().weekday())
    try:
        r = requests.get(f"{API_BASE_URL}/api/alarms")
        r.raise_for_status()
        alarms = r.json()
        return [(a['time'], a.get('label', "")) for a in alarms if a['is_active'] and not a['specific_date'] and weekday in a.get('days', '')]
    except:
        return []

def get_temp_alarms():
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    try:
        r = requests.get(f"{API_BASE_URL}/api/alarms")
        r.raise_for_status()
        alarms = r.json()
        return [(a['time'], a.get('label', ''), a['specific_date']) for a in alarms if a['is_active'] and a['specific_date'] and a['specific_date'] >= today]
    except:
        return []

def display_clock():
    now = datetime.datetime.now()
    weather = get_weather()
    reg_memo = get_regular_memo()
    today_memo = get_today_memo()
    reg_alarms = get_regular_alarms()
    temp_alarms = get_temp_alarms()

    print(now.strftime('%Y-%m-%d (%a)'))
    print(now.strftime('%H:%M'))
    print(f"Weather: {weather['weather']}, {weather['temperature']} | Fine Dust: {weather['dust']}")
    print(f"Regular Memo: {reg_memo}")
    print(f"Today's Memo: {today_memo}")
    print("Regular Alarms: " + ", ".join([a[0] for a in reg_alarms]) if reg_alarms else "Regular Alarms: None")
    if temp_alarms:
        print("Temporary Alarms: " + ", ".join([f"{a[0]} ({a[2]})" for a in temp_alarms]))
    else:
        print("Temporary Alarms: None")

def display_memo():
    reg_memo = get_regular_memo()
    today_memo = get_today_memo()
    reg_alarms = get_regular_alarms()
    print("Regular Memo:\n" + reg_memo)
    print("\nToday's Memo:\n" + today_memo)
    print("\nRegular Alarms: " + ", ".join([a[0] for a in reg_alarms]) if reg_alarms else "Regular Alarms: None")

def main():
    mode = "clock"
    while True:
        clear()
        if mode == "clock":
            print("[Clock Mode]")
            display_clock()
        elif mode == "memo":
            print("[Memo Mode]")
            display_memo()

        print("\n[1(clock) / 2(memo) / alarm / q]: ", end="")
        command = input().strip().lower()

        if command == "q":
            break
        elif command == "1":
            mode = "clock"
        elif command == "2":
            mode = "memo"
        elif command == "alarm":
            display_alarm_screen()

if __name__ == "__main__":
    main()