from flask import Flask, jsonify, send_from_directory
import psutil
import time
import subprocess  # Import subprocess to execute shell commands
from collections import deque

app = Flask(__name__, static_url_path='', static_folder='static')

# Store last 100 data points (adjust as needed)
history = {
    "cpu_usage": deque(maxlen=100),
    "ram_usage": deque(maxlen=100),
    "disk_usage": deque(maxlen=100),
    "temperature": deque(maxlen=100),
    "timestamps": deque(maxlen=100),
    "cpu_speed": deque(maxlen=100)
}

def get_system_uptime():
    """Fetches system uptime using 'uptime -p'"""
    try:
        uptime_output = subprocess.run(["uptime", "-p"], capture_output=True, text=True)
        return uptime_output.stdout.strip()  # Return formatted uptime
    except Exception as e:
        return f"Error retrieving uptime: {str(e)}"

def get_cpu_speed():
    """Fetches the current CPU clock speed in MHz"""
    try:
        return psutil.cpu_freq().current  # Returns the current CPU frequency in MHz
    except Exception as e:
        return "N/A"

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/stats')
def stats():
    # Get system stats
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    cpu_speed = get_cpu_speed()

    # Get temperature safely
    temps = psutil.sensors_temperatures()
    if "cpu_thermal" in temps and len(temps["cpu_thermal"]) > 0:
        temperature = temps["cpu_thermal"][0].current
    else:
        temperature = "N/A"

    # Get uptime from system command
    uptime_formatted = get_system_uptime()

    # Store data in history
    history["cpu_usage"].append(cpu_usage)
    history["ram_usage"].append(ram_usage)
    history["disk_usage"].append(disk_usage)
    history["temperature"].append(temperature)
    history["timestamps"].append(time.strftime("%H:%M:%S"))  # Store time as HH:MM:SS
    history["cpu_speed"].append(cpu_speed)

    # Return the full history + latest uptime
    return jsonify({
        "cpu_usage": list(history["cpu_usage"]),
        "ram_usage": list(history["ram_usage"]),
        "disk_usage": list(history["disk_usage"]),
        "temperature": list(history["temperature"]),
        "timestamps": list(history["timestamps"]),
        "uptime": uptime_formatted,  # Correct system uptime from 'uptime -p'
        "cpu_speed": list(history["cpu_speed"])
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
