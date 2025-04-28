import asyncio
import random
import argparse
import logging

import BAC0
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

    # Supplemental with more details, for demonstration
    _new_objects = analog_value(
        name="Lu-T2-ZN",
        properties={"units": "degreesCelsius"},
        description="Luis Floor 2 Zone Temperature",
        presentValue=22.5,
        is_commandable=True
    )

    states = make_state_text(["Normal", "Alarm", "Super Emergency"])
    _new_objects = multistate_value(
        description="An Alarm Value",
        properties={"stateText": states},
        name="BIG-ALARM",
        is_commandable=False,
    )

    _new_objects.add_objects_to_application(device)


async def main():
    # set to debug for logs
    BAC0.log_level(log_file=logging.DEBUG, stdout=logging.INFO, stderr=logging.CRITICAL)

    # We'll use 3 devices plus our main instance
    async with BAC0.start(port=47808, ip=args.ip, localObjName="bacnet-pi", deviceId=7) as bacnet:
        async with BAC0.start(port=47809, ip=args.ip, localObjName="DevicePi-1", deviceId=17) as device_app:
            # add points to instantiated bacnet sensor 
            add_points(device_app)
            
            # connect to device using main network
            test_device = await BAC0.device(
                f"{device_app.localIPAddr.addrTuple[0]}:47809", device_app.Boid, bacnet, poll=10
            )

            bacnet._log.info("CTRL-C to exit")

            while True:
                # Simulate a small random temperature drift
                current_temp = await test_device['Lu-T2-ZN'].value
                bacnet._log.info(current_temp)
                new_temp = round(current_temp + random.uniform(-0.5, 0.5), 1)
                # Write new temperature
                await test_device['Lu-T2-ZN'].write(new_temp, priority=8)

                bacnet._log.info(f"Updated RoomTempSensor presentValue to {new_temp} °C")

                # Wait before updating again
                await asyncio.sleep(15)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Run bacnet object simulations')
    
    parser.add_argument('--ip', type=str, required=True, help="IP that bacnet network and device will bind to")
    args = parser.parse_args()
    run(main, bacnet, args)
    
