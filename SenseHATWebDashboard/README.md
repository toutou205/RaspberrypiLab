# 🍓 Sense HAT Web Dashboard / Sense HAT 网页仪表盘

## 📖 Description / 项目描述

**English**:  
This project is a real-time environment and attitude monitoring system based on Raspberry Pi and Sense HAT. It displays sensor data from the Sense HAT via a web dashboard, including temperature, humidity, pressure, attitude angles, and calculated altitude. Users can view data in real-time via a web page and control whether to log this data to a local CSV file. It also supports switching LED matrix display modes via the physical joystick.

**中文**:  
该项目是一个基于 Raspberry Pi 和 Sense HAT 的实时环境与姿态监控系统。它通过一个 Web 仪表盘展示来自 Sense HAT 的传感器数据，包括温度、湿度、气压、姿态角以及计算出的海拔高度。用户可以通过网页实时查看数据，并控制是否将这些数据记录到本地 CSV 文件中。同时，它也支持通过物理摇杆切换 LED 矩阵的显示模式。

  ![Image](https://github.com/user-attachments/assets/c0f1b46d-fe87-4998-92de-02d72137f999)

## ✨ Key Features / 主要功能

- 📊 **Real-time Monitoring / 实时监控**  
  Push sensor data to the dashboard in real-time via WebSockets.  
  通过 WebSockets 将传感器数据实时推送到前端仪表盘。

- 🌡️ **Environment Data / 环境数据**  
  Temperature, Humidity, Pressure, Altitude.  
  温度、湿度、气压、海拔高度。

- 🧭 **IMU Data / 姿态数据**  
  Pitch, Roll, Yaw.  
  俯仰角、横滚角、航向角。

- 💾 **Data Logging / 数据记录**  
  Control data recording via the web interface. Data is saved as CSV in the `logs` directory.  
  用户可以通过网页控制数据记录，数据以 CSV 格式保存在 `logs` 目录下。

- 💡 **Multi-mode LED / 多模式 LED**  
  Switch between various display modes (Monitor, Spirit Level, Rainbow, Fire) using the physical joystick.  
  通过物理摇杆切换多种显示模式（如监控、水平仪、彩虹、火焰等）。

- 🌐 **Web Interface / Web 界面**  
  Built with Flask & Socket.IO (Backend) and HTML/Bootstrap 5 (Frontend).  
  使用 Flask 和 Socket.IO 构建后端，前端采用 HTML, Bootstrap 5 和 JavaScript 实现。

- 🛠️ **Mock Mode / 模拟模式**  
  Runs without hardware by generating simulated data for debugging.  
  在没有 Sense HAT 硬件的环境下也能运行，并生成模拟数据用于调试。

## 📂 File Structure / 文件结构

```text
SenseHATWebDashboard/
├── .gitignore              # Git ignore configuration / Git 忽略文件配置
├── README.md               # Project documentation / 项目说明文档
├── requirements.txt        # Python dependencies / Python 依赖库列表
├── rules.md                # AI coding rules / AI 编码规则
├── run.py                  # Main application entry point / 应用主入口
│
├── docs/                   # Project documentation / 项目文档
│   ├── PRD.md
│   ├── TECH_SPEC.md
│   └── TODO.md             # Project TODO list / 项目待办事项
│
├── logs/                   # Data log files / 数据记录文件
│
├── reference/              # Reference code / 参考代码
│
├── src/                    # Core source code / 核心源代码
│   ├── config.py           # Configuration / 配置文件
│   ├── core/               # Core logic / 核心逻辑
│   │   ├── background_thread.py # Sensor thread / 传感器线程
│   │   ├── calculator.py   # Calculations / 计算逻辑
│   │   └── logger.py       # Data logging / 数据记录
│   ├── hardware/           # Hardware drivers / 硬件驱动
│   │   ├── display.py      # LED display / LED 显示
│   │   └── sense_driver.py # Sense HAT driver / 驱动封装
│   └── web/                # Web server logic / Web 服务逻辑
│       ├── __init__.py
│       ├── routes.py       # Routes / 路由
│       └── socket_handler.py # SocketIO handlers / SocketIO 处理
│
└── web_client/             # Frontend files / 前端文件
    ├── static/             # Static assets / 静态资源
    └── templates/          # HTML templates / HTML 模板
        └── index.html      # Main dashboard / 主仪表盘
```

## 技术栈

- **硬件**:
  - Raspberry Pi (3B or newer recommended)
  - Sense HAT
- **后端**:
  - Python
  - Flask
  - Flask-SocketIO
- **前端**:
  - HTML5
  - Bootstrap 5
  - JavaScript
  - Socket.IO Client
- **Python 库**:
  - `sense-hat`

## 如何运行

1. **准备文件**:
   将项目文件放置在树莓派的某个目录下。

2. **安装依赖**:
   在项目根目录下，使用 `pip` 安装所有必要的库。
   ```bash
   pip install -r requirements.txt
   ```

3. **运行应用**:
   确保您在项目根目录下，然后运行 `run.py`。
   ```bash
   python3 run.py
   ```

4. **访问仪表盘**:
   在同一局域网下的任何设备上，打开浏览器并访问 `http://<你的树莓派IP地址>:5000` 即可看到实时数据。
   您可以在树莓派终端中使用 `hostname -I` 命令来查找其 IP 地址。

## 注意事项 (Notes)

### 虚拟环境与依赖 (Virtual Environment & Dependencies)

The `sense-hat` library relies on underlying system libraries (RTIMULib, etc.), and direct installation via pip in a clean virtual environment may fail. It's recommended to use the `--system-site-packages` argument when creating the virtual environment to reuse the Raspberry Pi's pre-installed libraries.

**Recommended setup steps / 推荐的设置步骤**:

```bash
# 1. Create a virtual environment with access to system packages / 创建带系统包权限的虚拟环境
python3 -m venv --system-site-packages venv

# 2. 激活环境
source venv/bin/activate

# 3. 安装其他 Python 依赖 (Flask 等)
pip install -r requirements.txt
```

如果是在非树莓派环境（如 Windows/Mac）开发，程序会自动检测并进入**模拟模式 (Mock Mode)**，生成模拟数据以供测试。

---

**Developer**: Alex
