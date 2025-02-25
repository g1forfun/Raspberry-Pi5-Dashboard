from flask import Flask, jsonify, send_from_directory
import psutil
import time
from collections import deque

app = Flask(__name__, static_url_path='', static_folder='static')

# Store last 100 data points (adjust as needed)
history = {
    "cpu_usage": deque(maxlen=100),
    "ram_usage": deque(maxlen=100),
    "disk_usage": deque(maxlen=100),
    "temperature": deque(maxlen=100),
    "timestamps": deque(maxlen=100)
}

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/stats')
def stats():
    # Get system stats
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent

    # Get temperature safely
    temps = psutil.sensors_temperatures()
    temperature = temps.get("cpu_thermal", [{}])[0].current if "cpu_thermal" in temps else "N/A"

    # Store data in history
    history["cpu_usage"].append(cpu_usage)
    history["ram_usage"].append(ram_usage)
    history["disk_usage"].append(disk_usage)
    history["temperature"].append(temperature)
    history["timestamps"].append(time.strftime("%H:%M:%S"))  # Store time as HH:MM:SS

    # Return the full history
    return jsonify({
        "cpu_usage": list(history["cpu_usage"]),
        "ram_usage": list(history["ram_usage"]),
        "disk_usage": list(history["disk_usage"]),
        "temperature": list(history["temperature"]),
        "timestamps": list(history["timestamps"])
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
