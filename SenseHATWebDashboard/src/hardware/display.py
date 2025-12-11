# -*- coding: utf-8 -*-
"""Manages the Sense HAT 8x8 LED matrix display.

This module provides a collection of functions for rendering different
visualizations on the LED matrix, such as a spirit level or special effects.
"""

import math
import random
import time
from typing import Any, Dict, List, Optional, Tuple

# Type alias for a SenseHat-like object to avoid circular imports and allow for mocks.
SenseHatDevice = Any


def _clamp(value: float, min_value: int = 0, max_value: int = 7) -> int:
    """Clamps a numeric value to be within the 0-7 range for LED coordinates."""
    return max(min_value, min(int(value), max_value))


class LEDDisplay:
    """
    Controls the rendering of visualizations on the Sense HAT's 8x8 LED matrix.

    This class is stateless. It receives all necessary information, including the
    hardware driver, current mode, and sensor data, via the `update_display`
    method. It then calls the appropriate internal drawing function.
    """

    def __init__(self, sense_device: Optional[SenseHatDevice]) -> None:
        """
        Initializes the LEDDisplay.

        Args:
            sense_device: An initialized Sense HAT driver object (like SenseHatWrapper)
                          or None if no hardware is present.
        """
        self._sense = sense_device
        self._last_mode_id = -1
        # Maps mode IDs to their corresponding drawing functions.
        self._draw_functions = {
            0: self._draw_monitor_mode,
            1: self._draw_spirit_level,
            2: self._draw_rainbow_wave,
            3: self._draw_fire_effect,
        }
        if self._sense:
            self._sense.clear()

    def update_display(
        self,
        mode: int,
        is_on: bool,
        orientation: Dict[str, float],
    ) -> None:
        """
        Updates the LED matrix based on the current state and sensor data.

        This is the main entry point for this class, called by the main loop.

        Args:
            mode: The ID of the current display mode.
            is_on: True if the display should be active, False otherwise.
            orientation: A dictionary with 'pitch' and 'roll' for drawing.
        """
        if not self._sense:
            return  # No hardware, nothing to draw

        if not is_on:
            self._sense.clear()
            return

        # If mode has changed, clear the screen once before drawing the new mode
        if mode != self._last_mode_id:
            time.sleep(0.8)  # Brief pause to avoid visual glitches
            self._sense.clear()
            self._last_mode_id = mode

        # Execute the drawing function for the current mode
        draw_function = self._draw_functions.get(mode)
        if draw_function:
            draw_function(orientation)

    def _draw_monitor_mode(self, orientation: Dict[str, float]) -> None:
        """Draws a 'breathing' green square. (Mode 0)"""
        t = time.time()
        intensity = int(150 + 100 * math.sin(t * 3))
        color: Tuple[int, int, int] = (0, intensity, 0)
        pixels = [(0, 0, 0)] * 64
        pixels[27] = color  # (3, 3)
        pixels[28] = color  # (4, 3)
        pixels[35] = color  # (3, 4)
        pixels[36] = color  # (4, 4)
        self._sense.set_pixels(pixels)

    def _draw_spirit_level(self, orientation: Dict[str, float]) -> None:
        """Draws a single pixel that moves based on pitch and roll. (Mode 1)"""
        pitch = orientation.get("pitch", 0.0)
        roll = orientation.get("roll", 0.0)

        # Map pitch and roll to LED coordinates
        y = 3.5 + (roll / 20.0) * 3.5
        x = 3.5 + (-pitch / 20.0) * 3.5
        
        target_x, target_y = _clamp(x), _clamp(y)

        # Color the pixel green if centered, red otherwise
        is_centered = 3 <= target_x <= 4 and 3 <= target_y <= 4
        color: Tuple[int, int, int] = (0, 255, 0) if is_centered else (255, 0, 0)
        
        self._sense.clear()
        self._sense.set_pixel(target_x, target_y, color)

    def _draw_rainbow_wave(self, orientation: Dict[str, float]) -> None:
        """Draws a dynamic, colorful wave. (Mode 2)"""
        pixels: List[Tuple[int, int, int]] = []
        t = time.time() * 2
        for i in range(64):
            x, y = i % 8, i // 8
            r = int(128 + 127 * math.sin(x / 2.0 + t))
            g = int(128 + 127 * math.sin(y / 2.0 + t))
            b = int(128 + 127 * math.sin((x + y) / 2.0 + t))
            pixels.append((r, g, b))
        self._sense.set_pixels(pixels)

    def _draw_fire_effect(self, orientation: Dict[str, float]) -> None:
        """Draws a simple, randomized fire effect. (Mode 3)"""
        pixels: List[Tuple[int, int, int]] = [
            (random.randint(150, 255), random.randint(0, 100), 0)
            for _ in range(64)
        ]
        self._sense.set_pixels(pixels)
