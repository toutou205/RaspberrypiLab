# -*- coding: utf-8 -*-
"""Main entry point for the Sense HAT Web Dashboard application.

This script initializes all components, wires them together, and starts the
Flask-SocketIO web server and the background sensor-reading thread.
"""

from typing import Optional

from flask import Flask
from flask_socketio import SocketIO

from src import config
from src.core.background_thread import SensorDataThread
from src.core.logger import DataLogger
from src.hardware.display import LEDDisplay
from src.hardware.sense_driver import SenseHatWrapper
from src.web.routes import configure_routes
from src.web.socket_handler import configure_socket_handlers

background_thread: Optional[SensorDataThread] = None


def create_app() -> tuple[SocketIO, Flask]:
    """Creates and configures the Flask application and its extensions.

    This factory function handles:
    1. Flask app initialization.
    2. SocketIO initialization.
    3. Hardware and logger setup.
    4. Configuration of web routes and socket handlers.
    5. Creation of the background thread instance.

    Returns:
        A tuple containing the configured SocketIO and Flask app instances.
    """
    global background_thread

    print("Initializing application components...")
    app = Flask(
        __name__,
        template_folder="web_client/templates",
        static_folder="web_client/static",
    )
    app.config["SECRET_KEY"] = config.SECRET_KEY
    socketio = SocketIO(app)

    sense_wrapper = SenseHatWrapper()
    logger = DataLogger(log_dir=config.LOG_DIRECTORY)
    led_display = LEDDisplay(sense_wrapper.sense)

    configure_routes(app)
    configure_socket_handlers(socketio, logger)

    background_thread = SensorDataThread(socketio, sense_wrapper, led_display, logger)

    print("Application initialization complete.")
    return socketio, app


def main() -> None:
    """Main function to run the application.

    It creates the app using the factory, starts the background thread,
    and runs the web server.
    """
    socketio, app = create_app()

    print("Starting background thread...")
    if background_thread:
        background_thread.start()

    print(f"Starting web server on {config.SERVER_HOST}:{config.SERVER_PORT}")
    try:
        socketio.run(
            app,
            host=config.SERVER_HOST,
            port=config.SERVER_PORT,
            debug=config.DEBUG_MODE,
            use_reloader=False,
        )
    except KeyboardInterrupt:
        print("Shutdown signal received.")
    finally:
        if background_thread:
            print("Stopping background thread...")
            background_thread.stop()
            background_thread.join()
        print("Application shut down.")


if __name__ == "__main__":
    main()