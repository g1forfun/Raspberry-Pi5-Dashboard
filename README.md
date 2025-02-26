# 📊 Raspberry Pi System Monitoring Dashboard

## 🚀 Features

### **📊 Real-Time System Monitoring**
- **CPU Usage (%)**
- **RAM Usage (%)**
- **Disk Usage (%)**
- **CPU Temperature (°C)**
- **Uptime**
- **CPU Speed (MHz)**
- **GPU Speed (MHz)** (NEW!)
  
### **📜 Persistent Data Storage (SQLite)**
- Stores **last 1000 records** in an SQLite database
- Data persists even after system reboots
- Graphs now **retain historical data** after page refresh

### **📡 Live Dashboard with Dynamic Charts**
- Uses **Chart.js** for real-time graphs
- Supports **dark mode/light mode**
- **Progress bars** for visualizing system usage
- **Auto-scaling charts** for different screen sizes

### **🛠️ Customizable Features**
- Adjustable **refresh interval** (1-10 seconds) via slider
- **Dark Mode Toggle** with saved preference
- **Pause Monitoring** feature to stop updates

## 📌 Prerequisites
Before running the dashboard, ensure your **Raspberry Pi OS** is set up with the required dependencies.

### 1️⃣ Update System Packages
```sh
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip -y
```

### 2️⃣ Install Required Python Libraries
```sh
pip install flask flask-cors psutil
```

### 3️⃣ Set Up the Project Directory
```sh
mkdir -p ~/rpi-dashboard/static
cd ~/rpi-dashboard
```

### 4️⃣ Clone the Repository
```sh
git clone https://github.com/g1forfun/rpi-dashboard.git .
```

### 5️⃣ Start the Flask Server
```sh
python3 app.py
```

The dashboard will be accessible at:
```sh
http://<your-pi-ip>:5000
```

To find your Raspberry Pi’s IP address:
```sh
hostname -I
```

---

## 📜 Running the Dashboard on Boot
To ensure the dashboard runs automatically on startup:

### 1️⃣ Create a systemd Service
```sh
sudo nano /etc/systemd/system/rpi-dashboard.service
```

Paste the following configuration:
```ini
[Unit]
Description=Raspberry Pi Dashboard
After=network.target

[Service]
User=<your-pi-username>
WorkingDirectory=/home/<your-pi-username>/rpi-dashboard
ExecStart=/usr/bin/python3 /home/<your-pi-username>/rpi-dashboard/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 2️⃣ Enable & Start the Service
```sh
sudo systemctl enable rpi-dashboard
sudo systemctl start rpi-dashboard
```

The dashboard will now start automatically whenever the Raspberry Pi boots.

---

## 🎮 Dashboard Controls
- 🎛 **Adjustable Update Interval**: Use the slider to change how often stats refresh.  
- ⏸ **Start/Pause Monitoring**: Click the button to pause or resume system updates.  
- 🌙 **Dark Mode Toggle**: Switch between light and dark themes instantly.  

---

## 🔧 Troubleshooting

### 🚫 Port 5000 Not Accessible?
```sh
sudo ss -tulnp | grep 5000
```
If Flask is not running, restart the service:
```sh
sudo systemctl restart rpi-dashboard
```

### 🛑 Python Module Errors?
Reinstall dependencies:
```sh
pip install --force-reinstall flask flask-cors psutil
```

### 🔄 Restart Flask Manually
If needed, restart the Flask server manually:
```sh
cd ~/rpi-dashboard
python3 app.py
```

---

## 📝 License
This project is licensed under the **GNU GENERAL PUBLIC LICENSE v3.0**.  
See the [LICENSE](https://www.gnu.org/licenses/gpl-3.0.en.html) file for more details.
