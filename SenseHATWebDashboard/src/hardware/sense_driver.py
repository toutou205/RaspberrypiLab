# -*- coding: utf-8 -*-
"""A wrapper class for the Sense HAT hardware.

Provides a simplified interface for accessing sensor data and handles cases
where the hardware is not present by providing mock data.
"""
import math
import threading
import time
from typing import Callable, Dict, Optional, Any

from .. import config

try:
    from sense_hat import ACTION_HELD, ACTION_PRESSED, SenseHat
except (ImportError, OSError):
    SenseHat = None  # type: ignore
    ACTION_PRESSED = None
    ACTION_HELD = None


class SenseHatWrapper:
    """A wrapper for the Sense HAT hardware.

    This class initializes the Sense HAT, provides methods to read sensor
    data, and listens for joystick events in a background thread. If the
    hardware is not detected, it switches to a mock mode and returns dynamic,
    simulated data.

    Attributes:
        sense: The SenseHat instance if available, otherwise None.
        is_mock: True if the wrapper is using mock data, False otherwise.
    """

    def __init__(self) -> None:
        """Initializes the SenseHatWrapper."""
        self.sense: Optional[SenseHat] = None
        self.is_mock: bool = True

        if SenseHat:
            try:
                self.sense = SenseHat()
                self.sense.clear()
                self.is_mock = False
                print("Sense HAT hardware detected and initialized successfully.")
            except OSError as e:
                print(f"Could not initialize Sense HAT: {e}. Using mock data.")
                self.is_mock = True
        else:
            print("Could not import sense_hat library. Using mock data.")
            self.is_mock = True

    def get_temperature(self) -> float:
        """Reads the temperature from the humidity sensor.

        Returns:
            The temperature in degrees Celsius, or a simulated value in mock mode.
        """
        # Reason for change: Added a docstring for clarity.
        if not self.is_mock and self.sense:
            return self.sense.get_temperature()
        return config.DEFAULT_TEMPERATURE + 5.0 * math.sin(time.time() / 60.0)

    def get_pressure(self) -> float:
        """Reads the atmospheric pressure.

        Returns:
            The pressure in hectopascals (hPa), or a simulated value in mock mode.
        """
        # Reason for change: Added a docstring for clarity.
        if not self.is_mock and self.sense:
            return self.sense.get_pressure()
        return config.DEFAULT_PRESSURE + 5.0 * math.cos(time.time() / 30.0)

    def get_humidity(self) -> float:
        """Reads the percentage relative humidity.

        Returns:
            The humidity percentage, or a simulated value in mock mode.
        """
        # Reason for change: Added a docstring for clarity.
        if not self.is_mock and self.sense:
            return self.sense.get_humidity()
        return config.DEFAULT_HUMIDITY + 10.0 * math.sin(time.time() / 45.0)

    def get_orientation(self) -> Dict[str, float]:
        """Reads the orientation from the IMU sensors.

        The pitch and roll values are adjusted to be within the -180 to 180
        degree range, and yaw is 0-360.

        Returns:
            A dictionary containing pitch, roll, and yaw in degrees, or
            simulated values in mock mode.
        """
        # Reason for change: Added a docstring for clarity.
        if not self.is_mock and self.sense:
            o = self.sense.get_orientation_degrees()
            # Normalize pitch and roll to -180 to 180 degrees
            p = (o["pitch"] + 180) % 360 - 180
            r = (o["roll"] + 180) % 360 - 180
            return {"pitch": p, "roll": r, "yaw": o["yaw"] % 360}

        # Return dynamic mock data for orientation
        t = time.time()
        return {
            "pitch": 30.0 * math.sin(t * 0.5),
            "roll": 45.0 * math.cos(t * 0.3),
            "yaw": (t * 15) % 360,
        }

    def set_low_light(self, is_low: bool) -> None:
        """Sets the LED matrix to low light mode.

        Args:
            is_low: True to enable low light mode, False to disable.
        """
        # Reason for change: Added a docstring for clarity.
        if not self.is_mock and self.sense:
            self.sense.low_light = is_low

    def clear(self) -> None:
        """Clears the LED matrix, setting all pixels to off."""
        # Reason for change: Added a docstring for clarity.
        if not self.is_mock and self.sense:
            self.sense.clear()

    def set_pixels(self, pixels: list[tuple[int, int, int]]) -> None:
        """Sets the entire LED matrix from a list of 64 RGB tuples.

        Args:
            pixels: A list of 64 tuples, each representing the RGB color
                    of a pixel.
        """
        # Reason for change: Added a docstring for clarity.
        if not self.is_mock and self.sense:
            self.sense.set_pixels(pixels)

    def show_letter(self, *args: Any, **kwargs: Any) -> None:
        """Shows a single letter on the LED matrix.

        This method is a passthrough to the underlying SenseHat.show_letter,
        accepting the same arguments.
        """
        # Reason for change: Added a docstring for clarity.
        if not self.is_mock and self.sense:
            self.sense.show_letter(*args, **kwargs)

    def _joystick_listener(self, callback: Callable[[str], None]) -> None:
        """Internal method to listen for joystick events."""
        while True:
            if not self.is_mock and self.sense and self.sense.stick:
                event = self.sense.stick.wait_for_event()
                if event.action in (ACTION_PRESSED, ACTION_HELD):
                    callback(event.direction)
            else:
                # In mock mode, this thread does nothing but sleep.
                time.sleep(1)

    def start_joystick_listener(self, callback: Callable[[str], None]) -> None:
        """Starts the joystick listener in a separate daemon thread.

        Args:
            callback: A function to be called when a joystick event occurs.
                      The function will receive the event direction as a string.
        """
        if self.is_mock:
            print("Joystick listener not started (mock mode).")
            return

        listener_thread = threading.Thread(
            target=self._joystick_listener, args=(callback,)
        )
        listener_thread.daemon = True
        listener_thread.start()
        print("Joystick listener started.")
