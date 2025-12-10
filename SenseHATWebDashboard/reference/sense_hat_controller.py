import time
import math
import random
import threading
from sense_hat import SenseHat, ACTION_PRESSED, ACTION_HELD
from data_recorder import DataRecorder

class SenseHatController:
    """
    封装 Sense HAT 的所有功能：传感器读取、LED 显示、摇杆控制和数据记录。
    """
    MODES = [
        {"id": 0, "name": "Monitor Mode", "desc": "显示静态状态指示灯"},
        {"id": 1, "name": "Spirit Level", "desc": "水平仪 (姿态可视化)"},
        {"id": 2, "name": "Rainbow Wave", "desc": "动态彩虹波浪"},
        {"id": 3, "name": "Fire Effect", "desc": "随机火焰粒子"}
    ]
    SEA_LEVEL_PRESSURE = 1013.25  # hPa, 用于计算海拔

    def __init__(self, socketio_instance):
        self.socketio = socketio_instance
        self.data_recorder = DataRecorder()
        self.is_hardware_present = False

        # 状态变量
        self.current_mode = 0
        self.last_mode = -1
        self.is_on = True
        
        try:
            self.sense = SenseHat()
            self.sense.clear()
            self.is_hardware_present = True
            print("Sense HAT 硬件已找到。")
        except (OSError, IOError):
            self.sense = None
            print("警告: 未找到 Sense HAT 硬件。程序将以模拟模式运行。")
            print("提示: 如果您在树莓派上运行，请检查 I2C 接口是否已启用 (sudo raspi-config)。")

    def start_threads(self):
        """启动所有后台线程。"""
        # 主循环线程
        t_main = threading.Thread(target=self._main_loop)
        t_main.daemon = True
        t_main.start()
        # 摇杆监听线程
        t_joy = threading.Thread(target=self._joystick_listener)
        t_joy.daemon = True
        t_joy.start()
        print("后台线程已启动...")

    def _main_loop(self):
        """主循环，负责读取数据、更新LED和通过Socket.IO发送数据。"""
        while True:
            # 1. 读取传感器数据 (如果硬件存在) 或生成模拟数据
            if self.is_hardware_present:
                temp = self.sense.get_temperature()
                humidity = self.sense.get_humidity()
                pressure = self.sense.get_pressure()
                altitude = 44330 * (1 - (pressure / self.SEA_LEVEL_PRESSURE) ** (1 / 5.255))

                orientation = self.sense.get_orientation()
                pitch = orientation['pitch']
                roll = orientation['roll']
                yaw = orientation['yaw']
                
                if pitch > 180: pitch -= 360
                if roll > 180: roll -= 360
            else:
                # 生成平滑变化的模拟数据
                t = time.time()
                temp = 25 + 5 * math.sin(t / 10)
                humidity = 50 + 10 * math.cos(t / 5)
                pressure = 1013 + 2 * math.sin(t / 2)
                altitude = 44330 * (1 - (pressure / self.SEA_LEVEL_PRESSURE) ** (1 / 5.255))
                pitch = 15 * math.sin(t * 0.8)
                roll = 20 * math.cos(t * 0.5)
                yaw = (t * 15) % 360

            # 2. 更新 LED
            self._draw_leds(pitch, roll, yaw)

            # 3. 准备数据包
            data_packet = {
                'env': {
                    'temp': round(temp, 1),
                    'humidity': round(humidity, 1),
                    'pressure': round(pressure, 1),
                    'altitude': round(altitude, 1)
                },
                'imu': {
                    'pitch': round(pitch, 1),
                    'roll': round(roll, 1),
                    'yaw': round(yaw, 1)
                },
                'sys': {
                    'mode_id': self.current_mode,
                    'mode_name': self.MODES[self.current_mode]['name'],
                    'is_on': self.is_on,
                    'is_recording': self.data_recorder.is_recording
                }
            }

            # 4. 发送数据
            self.socketio.emit('sensor_update', data_packet)

            # 5. 记录数据
            self.data_recorder.record(data_packet)

            time.sleep(0.05) # 20Hz

    def _joystick_listener(self):
        """监听摇杆事件。"""
        while True:
            if not self.is_hardware_present:
                time.sleep(1) # 在模拟模式下，此线程无需执行任何操作
                continue

            for event in self.sense.stick.get_events():
                if event.action in (ACTION_PRESSED, ACTION_HELD):
                    if event.direction == "left":
                        self.current_mode = (self.current_mode - 1) % len(self.MODES)
                        self.sense.show_letter(str(self.current_mode), text_colour=[0, 0, 255])
                        time.sleep(0.5)
                    elif event.direction == "right":
                        self.current_mode = (self.current_mode + 1) % len(self.MODES)
                        self.sense.show_letter(str(self.current_mode), text_colour=[0, 0, 255])
                        time.sleep(0.5)
                    elif event.direction == "up":
                        self.sense.low_light = False
                    elif event.direction == "down":
                        self.sense.low_light = True
                    elif event.direction == "middle":
                        self.is_on = not self.is_on
            time.sleep(0.1)

    def _clamp(self, value, min_value=0, max_value=7):
        return max(min_value, min(value, max_value))

    def _draw_leds(self, pitch, roll, yaw):
        """根据当前模式绘制LED矩阵。"""
        if not self.is_hardware_present:
            return # 如果没有硬件，则跳过所有绘制操作

        if self.current_mode != self.last_mode:
            time.sleep(0.5) # 模式切换时短暂延迟以显示模式数字
            self.last_mode = self.current_mode
        
        if not self.is_on:
            self.sense.clear()
            return

        # 模式 0: 监控模式 (呼吸灯)
        if self.current_mode == 0:
            t = time.time()
            intensity = int(150 + 100 * math.sin(t * 3))
            color = (0, intensity, 0)
            self.sense.clear()
            self.sense.set_pixel(3, 3, color)
            self.sense.set_pixel(3, 4, color)
            self.sense.set_pixel(4, 3, color)
            self.sense.set_pixel(4, 4, color)

        # 模式 1: 水平仪
        elif self.current_mode == 1:
            self.sense.clear()
            y = int(3.5 + (roll / 20.0) * 3.5)
            x = int(3.5 + (-pitch / 20.0) * 3.5)
            target_x = self._clamp(x)
            target_y = self._clamp(y)
            col = (0, 255, 0) if (3 <= target_x <= 4 and 3 <= target_y <= 4) else (255, 0, 0)
            self.sense.set_pixel(target_x, target_y, col)

        # 模式 2: 彩虹波浪
        elif self.current_mode == 2:
            pixels = []
            t = time.time() * 2
            for i in range(64):
                x, y = i % 8, i // 8
                r = int(128 + 127 * math.sin(x / 2.0 + t))
                g = int(128 + 127 * math.sin(y / 2.0 + t))
                b = int(128 + 127 * math.sin((x + y) / 2.0 + t))
                pixels.append((r, g, b))
            self.sense.set_pixels(pixels)

        # 模式 3: 火焰效果
        elif self.current_mode == 3:
            pixels = []
            for _ in range(64):
                r = random.randint(150, 255)
                g = random.randint(0, 100)
                pixels.append((r, g, 0))
            self.sense.set_pixels(pixels)

    # --- 公共接口方法 ---
    def toggle_recording(self):
        """切换数据记录状态。"""
        if self.data_recorder.is_recording:
            self.data_recorder.stop()
        else:
            self.data_recorder.start()
        print(f"数据记录状态: {'ON' if self.data_recorder.is_recording else 'OFF'}")