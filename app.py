from flask import Flask, jsonify, send_from_directory
import psutil
import time
import sqlite3
import subprocess  # Import subprocess to execute shell commands

app = Flask(__name__, static_url_path='', static_folder='static')

# Database setup
DB_NAME = "stats.db"
TABLE_NAME = "system_stats"

def init_db():
    """Initialize the SQLite database and create table if not exists"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            cpu_usage REAL,
            ram_usage REAL,
            disk_usage REAL,
            temperature REAL,
            cpu_speed REAL,
            gpu_speed REAL dEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def save_stats(cpu, ram, disk, temp, speed, gpu_speed):
    """Save system stats to SQLite database"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f'''
        INSERT INTO {TABLE_NAME} (timestamp, cpu_usage, ram_usage, disk_usage, temperature, cpu_speed, gpu_speed)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (time.strftime("%Y-%m-%d %H:%M:%S"), cpu, ram, disk, temp, speed, gpu_speed))  # Now includes 7 values

    # Keep only the last 1000 records
    cursor.execute(f"""
        DELETE FROM {TABLE_NAME} WHERE id NOT IN (
            SELECT id FROM {TABLE_NAME} ORDER BY id DESC LIMIT 1000
        )
    """)

    conn.commit()
    conn.close()

def get_system_uptime():
    """Fetches system uptime using 'uptime -p'"""
    try:
        uptime_output = subprocess.run(["uptime", "-p"], capture_output=True, text=True)
        return uptime_output.stdout.strip()
    except Exception as e:
        return f"Error retrieving uptime: {str(e)}"

def get_cpu_speed():
    """Fetches the current CPU clock speed in MHz"""
    try:
        return psutil.cpu_freq().current
    except Exception as e:
        return "N/A"

def get_gpu_speed():
    """Fetches the current GPU clock speed in MHz for Raspberry Pi"""

    try:
        gpu_speed_output = subprocess.run(["vcgencmd", "measure_clock", "core"], capture_output=True, text=True)
        gpu_speed = int(gpu_speed_output.stdout.split("=")[1]) // 1000000  # Convert Hz to MHz
        return gpu_speed
    except Exception as e:
        return "N/A"

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/stats')
def stats():
    """Fetch latest system stats and return history"""
    # Get system stats
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    cpu_speed = get_cpu_speed()
    gpu_speed = get_gpu_speed()

    
    # Get temperature safely
    temps = psutil.sensors_temperatures()
    if "cpu_thermal" in temps and len(temps["cpu_thermal"]) > 0:
        temperature = temps["cpu_thermal"][0].current
    else:
        temperature = "N/A"
    
    # Get uptime
    uptime_formatted = get_system_uptime()
    
    # Store stats in the database
    save_stats(cpu_usage, ram_usage, disk_usage, temperature, cpu_speed, gpu_speed)
    
    # Retrieve last 100 records from database
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f'''
        SELECT timestamp, cpu_usage, ram_usage, disk_usage, temperature, cpu_speed, gpu_speed
        FROM {TABLE_NAME} ORDER BY id DESC LIMIT 100
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    # Format data for JSON response
    timestamps, cpu, ram, disk, temp, speed, gpu = zip(*reversed(rows))  # Reverse to maintain chronological order
    
    return jsonify({
        "cpu_usage": list(cpu),
        "ram_usage": list(ram),
        "disk_usage": list(disk),
        "temperature": list(temp),
        "timestamps": list(timestamps),
        "uptime": uptime_formatted,
        "cpu_speed": list(speed),
	"gpu_speed": list(gpu)
    })

if __name__ == '__main__':
    init_db()  # Ensure database is initialized
    app.run(host='0.0.0.0', port=5000, debug=True)
