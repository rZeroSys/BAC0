import asyncio
import random
import argparse
import logging
import socket
from datetime import datetime
import pytz

from BAC0 import connect, device, log_level
from BAC0.core.devices.local.factory import (
    ObjectFactory,
    analog_input,
    binary_input,
)
from BAC0.scripts.script_runner import run

bacnet = None

def get_local_ip():
    """Get the local IP address of this machine."""
    try:
        # Connect to a remote address to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Connect to Google's DNS server (doesn't actually send data)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            return local_ip
    except Exception:
        # Fallback to localhost if we can't determine the IP
        return "127.0.0.1"

def add_points(device):
    """Add the number machine points to the device."""
    # Start from fresh
    ObjectFactory.clear_objects()

    # Create random number analog input (0-100 range)
    random_number_objects = analog_input(
        instance=1,
        name="random number",
        description="Random number generator (0-100)",
        presentValue=50.0,  # Start with middle value
        is_commandable=False
    )

    # Create work time binary input (1 during 9am-5pm Mon-Fri Pacific time)
    work_time_objects = binary_input(
        instance=2,
        name="work time",
        description="Work time indicator (1 during 9am-5pm Mon-Fri Pacific)",
        presentValue=0,  # Start with 0 (not work time)
        is_commandable=False
    )

    # Add objects to the device
    random_number_objects.add_objects_to_application(device)
    work_time_objects.add_objects_to_application(device)


def is_work_time():
    """Check if current time is work time (9am-5pm Mon-Fri Pacific)."""
    # Get current time in Pacific timezone
    pacific = pytz.timezone('US/Pacific')
    now = datetime.now(pacific)
    
    # Check if it's Monday-Friday (0=Monday, 6=Sunday)
    if now.weekday() >= 5:  # Saturday or Sunday
        return False
    
    # Check if it's between 9am and 5pm
    hour = now.hour
    return 9 <= hour < 17  # 9am to 4:59pm


async def main():
    # Set to debug for logs
    log_level(log_file=logging.DEBUG, stdout=logging.INFO, stderr=logging.CRITICAL)

    # Get local IP address (use provided IP or auto-detect)
    local_ip = args.ip if args.ip else get_local_ip()
    
    # Connect to BACnet with device ID 52 on port 47808
    async with connect(port=47808, ip=local_ip, localObjName="number-machine", deviceId=52) as bacnet:
        # Add points to the device
        add_points(bacnet)
        
        bacnet._log.info(f"Number Machine simulation started on {local_ip}:47808")
        bacnet._log.info("CTRL-C to exit")

        while True:
            # Update random number (0-100, whole numbers only)
            new_random_number = random.randint(0, 100)
            bacnet['random number'].presentValue = new_random_number
            bacnet._log.info(f"Updated random number to {new_random_number}")

            # Update work time based on current time
            work_time_value = 1 if is_work_time() else 0
            bacnet['work time'].presentValue = work_time_value
            
            # Get current Pacific time for logging
            pacific = pytz.timezone('US/Pacific')
            current_time = datetime.now(pacific)
            
            bacnet._log.info(f"Updated work time to {work_time_value} (Current Pacific time: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')})")

            # Wait 1 minute before updating again
            bacnet._log.info("Sleeping for 1 minute...")
            await asyncio.sleep(60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Run Number Machine BACnet simulation')
    
    parser.add_argument('--ip', type=str, required=False, 
                       help="IP that BACnet network and device will bind to (auto-detected if not provided)")
    args = parser.parse_args()
    run(main, bacnet, args)
