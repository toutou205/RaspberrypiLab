# -*- coding: utf-8 -*-
"""Defines SocketIO event handlers for real-time web communication."""

from flask_socketio import SocketIO, emit

from src.core.logger import DataLogger


def configure_socket_handlers(socketio: SocketIO, logger: DataLogger) -> None:
    """Configures handlers for SocketIO events.

    This function registers handlers for events sent from the client-side,
    such as controlling the data logger.

    Args:
        socketio: The Flask-SocketIO instance.
        logger: The application's DataLogger instance.
    """

    @socketio.on("toggle_recording")
    def handle_toggle_recording(data: dict = None) -> None:
        """Handles the 'toggle_recording' event from the client.

        Starts or stops the data logger based on its current state. After
        changing the state, it broadcasts the new recording status to all
        connected clients.

        Args:
            data: The data payload from the client (not used).
        """
        if logger.is_recording:
            logger.stop()
        else:
            logger.start()

        emit("recording_status", {"is_recording": logger.is_recording}, broadcast=True)