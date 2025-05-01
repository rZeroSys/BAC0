import asyncio
import random
import argparse
import logging

from BAC0 import connect, device, log_level
from BAC0.core.devices.local.factory import (
    ObjectFactory,
    analog_input,
    analog_value,
    binary_input,
    binary_output,
    binary_value,
    character_string,
    date_value,
    datetime_value,
    make_state_text,
    multistate_input,
    multistate_output,
    multistate_value,
)
from BAC0.scripts.script_runner import run

bacnet = None

def add_points(device):
    # Start from fresh
    ObjectFactory.clear_objects()

    # Create state list
    states = make_state_text(["Normal", "Alarm", "Super Emergency"])
    multistate_value(
        description="An Alarm Value",
        properties={"stateText": states},
        name="BIG-ALARM",
        is_commandable=False,
    )
    analog_input(presentValue=99.9)

    # Supplemental with more details, for demonstration
    _new_objects = analog_value(
        instance=100,
        name="Lu-T2-ZN",
        properties={"units": "degreesCelsius"},
        description="Luis Floor 2 Zone Temperature",
        presentValue=22.5,
        is_commandable=True
    )

    _new_objects.add_objects_to_application(device)


async def main():
    # set to debug for logs
    log_level(log_file=logging.DEBUG, stdout=logging.INFO, stderr=logging.CRITICAL)

    # We'll use 3 devices plus our main instance
    async with connect(port=47808, ip=args.ip, localObjName="bacnet-pi-device") as bacnet:
            # add points to instantiated bacnet sensor 
            add_points(bacnet)
            
            # connect to device using main network
            #device = await device(
            #    f"{args.ip}:47808", bacnet_device.Boid, bacnet_device, poll=10
            #)

            bacnet._log.info("CTRL-C to exit")

            while True:
                # Simulate a small random temperature drift
                current_temp = bacnet['Lu-T2-ZN'].presentValue
                bacnet._log.info(current_temp)
                new_temp = round(current_temp + random.uniform(-0.5, 0.5), 1)
                # Write new temperature
                bacnet['Lu-T2-ZN'].presentValue = new_temp
                #device1._log.info(f"Updated RoomTempSensor presentValue to {new_temp} °C")

                # Wait before updating again
                print("Sleep every 7 seconds.")
                await asyncio.sleep(7)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Run bacnet object simulations')
    
    parser.add_argument('--ip', type=str, required=True, help="IP that bacnet network and device will bind to")
    args = parser.parse_args()
    run(main, bacnet, args)
    
