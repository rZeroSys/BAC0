# Number Machine BACnet Simulation - Raspberry Pi Installation

This guide will help you install and run the Number Machine BACnet simulation on a Raspberry Pi running Debian Bookworm.

## Prerequisites

- Raspberry Pi running Debian Bookworm (Raspberry Pi OS)
- Network connectivity
- Python 3.9 or higher

## Installation Steps

### 1. Update System Packages

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Install Python and pip

```bash
sudo apt install python3 python3-pip python3-venv -y
```

### 3. Clone or Copy BAC0 Repository

If you have the BAC0 repository:

```bash
cd ~
git clone <your-bac0-repo-url>
cd BAC0
```

Or if you're copying files, ensure you have the complete BAC0 directory structure.

### 4. Create Virtual Environment

```bash
cd BAC0
python3 -m venv venv
source venv/bin/activate
```

### 5. Install BAC0 Dependencies

```bash
pip install -e .
```

This will install all required dependencies including:
- BACpypes3
- colorama
- python-dotenv
- pytz
- aiosqlite

## Running the Simulation

### 1. Activate Virtual Environment

```bash
cd BAC0
source venv/bin/activate
```

### 2. Run the Number Machine Simulation

The simulation will automatically detect your Pi's IP address, so you can simply run:

```bash
python simulations/manual_create_number_machine.py
```

Or if you want to specify a particular IP address:

```bash
python simulations/manual_create_number_machine.py --ip 192.168.1.100
```

## What the Simulation Does

The Number Machine creates a BACnet device with:

- **Device ID:** 52
- **Port:** 47808
- **Two Points:**
  - **"random number"** (Analog Input): Generates whole numbers 0-100 every minute
  - **"work time"** (Binary Input): Shows 1 during 9am-5pm Monday-Friday Pacific time, 0 otherwise

## Stopping the Simulation

Press `Ctrl+C` to stop the simulation.

## Troubleshooting

### Permission Issues with Port 47808

If you get permission errors, you may need to run with elevated privileges:

```bash
sudo python simulations/manual_create_number_machine.py
```

### Network Interface Issues

If the simulation can't bind to the network interface, try:

1. Check your IP address: `ip addr show`
2. Use `0.0.0.0` instead of your specific IP: `--ip 0.0.0.0`

### Dependencies Issues

If you encounter import errors, ensure the virtual environment is activated and dependencies are installed:

```bash
source venv/bin/activate
pip install -e .
```

## Auto-start on Boot (Optional)

To automatically start the simulation when the Pi boots:

### 1. Create a systemd service file

```bash
sudo nano /etc/systemd/system/number-machine.service
```

### 2. Add the following content:

```ini
[Unit]
Description=Number Machine BACnet Simulation
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/BAC0
Environment=PATH=/home/pi/BAC0/venv/bin
ExecStart=/home/pi/BAC0/venv/bin/python simulations/manual_create_number_machine.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 3. Replace paths and IP address as needed, then enable:

```bash
sudo systemctl daemon-reload
sudo systemctl enable number-machine.service
sudo systemctl start number-machine.service
```

### 4. Check status:

```bash
sudo systemctl status number-machine.service
```

## BACnet Client Testing

You can test the simulation using BACnet discovery tools or clients that can connect to your Pi's IP address on port 47808 to discover device ID 52 and its points.

## Support

For issues with the BAC0 library itself, refer to the main BAC0 documentation and repository.
