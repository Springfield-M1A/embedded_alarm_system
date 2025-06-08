import re
import os
import sys

if getattr(sys, 'frozen', False):
    SCRIPT_DIR = os.path.dirname(sys.executable)
else:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

FILES_TO_UPDATE = [
    os.path.join(SCRIPT_DIR, "Frontend_RaspberryPi/Screens/alarm_set_screen.py"),
    os.path.join(SCRIPT_DIR, "Frontend_RaspberryPi/Services/alarm_manager.py"),
    os.path.join(SCRIPT_DIR, "Frontend_RaspberryPi/Services/memo_loader.py"),
    os.path.join(SCRIPT_DIR, "Frontend_RaspberryPi/Services/weather_api.py"),
    os.path.join(SCRIPT_DIR, "Frontend_RaspberryPi/main_CLI.py"),
]

def select_ip():
    print("Choose the server address:")
    print("1) http://localhost:5000")
    print("2) http://127.0.0.1:5000")
    print("3) Enter manually")
    option = input("Enter option number (1/2/3): ").strip()

    if option == "1":
        return "http://localhost:5000"
    elif option == "2":
        return "http://127.0.0.1:5000"
    elif option == "3":
        return input("Enter the server address (e.g. http://192.168.0.23:5000): ").strip()
    else:
        print("[Error] Invalid option.")
        exit(1)

def update_file(file_path, new_url):
    if not os.path.exists(file_path):
        print(f"[Warning] File not found: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content, count = re.subn(
        r'API_BASE_URL\s*=\s*["\'].*?["\']',
        f'API_BASE_URL = "{new_url}"',
        content
    )

    if count > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"[Updated] {file_path}")
    else:
        print(f"[Warning] No API_BASE_URL found in: {file_path}")

def main():
    new_ip = select_ip()
    print()

    for path in FILES_TO_UPDATE:
        update_file(path, new_ip)

    print("\n[Success] API_BASE_URL has been updated.")

if __name__ == "__main__":
    main()