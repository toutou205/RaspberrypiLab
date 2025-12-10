from flask import Flask
from flask_socketio import SocketIO
import time
from threading import Thread
from src.hardware.sense_driver import SenseHatWrapper
from src.hardware.display import LEDDisplay
from src.core.calculator import pressure_to_altitude
from src.core.logger import DataLogger
from src.web.routes import configure_routes
from src.web.socket_handler import configure_socket_handlers

# 初始化Flask App和SocketIO
app = Flask(__name__, template_folder='web_client/templates', static_folder='web_client/static')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# 初始化硬件、日志记录器和LED显示
sense_wrapper = SenseHatWrapper()
logger = DataLogger()
# 确保display模块在有sense对象时才初始化
led_display = LEDDisplay(sense_wrapper.sense) if sense_wrapper.sense else None


# 全局变量来控制后台线程
thread = None
thread_stop_event = True

def data_reading_thread():
    """
    后台线程，用于读取传感器数据，计算，更新LED并发送。
    """
    global logger, led_display, sense_wrapper
    while not thread_stop_event:
        try:
            # 读取所有传感器数据
            temp = sense_wrapper.get_temperature()
            pressure = sense_wrapper.get_pressure()
            humidity = sense_wrapper.get_humidity()
            orientation = sense_wrapper.get_orientation()
            
            pitch = orientation['pitch']
            roll = orientation['roll']
            yaw = orientation['yaw']

            # 更新LED显示
            if led_display:
                led_display.draw_leds(pitch, roll, yaw)

            # 计算海拔
            altitude = pressure_to_altitude(pressure)
            
            # 检查录制状态并记录数据
            if logger.is_running:
                log_payload = {
                    "temperature": temp,
                    "pressure": pressure,
                    "altitude": altitude
                }
                logger.log(log_payload)

            # 通过SocketIO发送完整数据
            socketio.emit('new_data', {
                "temp": f"{temp:.1f}",
                "pressure": f"{pressure:.2f}",
                "humidity": f"{humidity:.1f}",
                "altitude": f"{altitude:.2f}",
                "pitch": f"{pitch:.1f}",
                "roll": f"{roll:.1f}",
                "yaw": f"{yaw:.1f}",
                "recording": logger.is_running
            })
            
        except Exception as e:
            print(f"Error in background thread: {e}")
            
        time.sleep(0.1) # 增加更新频率以获得更流畅的LED效果

def run_app():
    global thread, thread_stop_event
    
    # 配置Flask路由和SocketIO事件处理
    configure_routes(app)
    configure_socket_handlers(socketio, logger)

    # 启动后台线程
    if thread is None or not thread.is_alive():
        thread_stop_event = False
        thread = Thread(target=data_reading_thread)
        thread.daemon = True
        thread.start()

    # 运行Flask应用
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)

if __name__ == '__main__':
    run_app()
