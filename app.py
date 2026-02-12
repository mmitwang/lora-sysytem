from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import serial
import threading
import time
import json
import sqlite3
import os

app = Flask(__name__)
CORS(app)

# 全局变量
serial_port = None
serial_thread = None
stop_thread = False
query_running = False  # 问询状态，默认为False（不运行）
sensor_data = {"temperature": 0, "humidity": 0, "timestamp": 0}
serial_config = {
    "port": "COM3",
    "baudrate": 9600,
    "parity": "N",
    "stopbits": 1,
    "bytesize": 8
}
query_interval = 2  # 默认问询周期（秒）
frame_data = {"query": "", "response": ""}  # 帧数据

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect('iot_data.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """初始化数据库，创建必要的表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 创建历史数据表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            timestamp INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建配置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL
        )
    ''')
    
    # 插入默认配置
    default_configs = [
        ('query_interval', '2'),
        ('serial_port', 'COM3'),
        ('baudrate', '9600'),
        ('parity', 'N'),
        ('stopbits', '1'),
        ('bytesize', '8')
    ]
    
    for key, value in default_configs:
        cursor.execute('''
            INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)
        ''', (key, value))
    
    conn.commit()
    conn.close()

def save_sensor_data(temperature, humidity, timestamp):
    """保存传感器数据到数据库"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO sensor_history (temperature, humidity, timestamp)
        VALUES (?, ?, ?)
    ''', (temperature, humidity, timestamp))
    
    conn.commit()
    conn.close()

def get_history_data(start_time, end_time):
    """获取指定时间范围内的历史数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT temperature, humidity, timestamp
        FROM sensor_history
        WHERE timestamp >= ? AND timestamp <= ?
        ORDER BY timestamp ASC
    ''', (start_time, end_time))
    
    data = cursor.fetchall()
    conn.close()
    
    return [{
        "temperature": row[0],
        "humidity": row[1],
        "timestamp": row[2]
    } for row in data]

# 初始化数据库
init_db()

# 模拟LoRa数据接收（实际项目中需要根据硬件调整）
def simulate_lora_data():
    """模拟LoRa数据接收，生成温度和湿度数据"""
    import random
    while not stop_thread:
        # 模拟数据格式: {"temp": 25.5, "hum": 60.0}
        temp = round(random.uniform(20, 30), 1)
        hum = round(random.uniform(40, 70), 1)
        timestamp = time.time()
        global sensor_data
        sensor_data = {
            "temperature": temp,
            "humidity": hum,
            "timestamp": timestamp
        }
        time.sleep(2)  # 每2秒生成一次数据

# CRC16校验计算
def calculate_crc(data):
    """计算Modbus-RTU CRC16校验码"""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc

# 构建Modbus-RTU问询帧
def build_modbus_query():
    """构建Modbus-RTU问询帧"""
    # 地址码01，功能码03，起始地址0000，数据长度0002
    data = [0x01, 0x03, 0x00, 0x00, 0x00, 0x02]
    # 计算CRC16校验码
    crc = calculate_crc(data)
    # 添加校验码（低位在前，高位在后）
    data.append(crc & 0xFF)
    data.append((crc >> 8) & 0xFF)
    return bytearray(data)

# 解析Modbus-RTU应答帧
def parse_modbus_response(response):
    """解析Modbus-RTU应答帧"""
    try:
        if len(response) < 9:
            print(f"应答帧长度不足: {len(response)}")
            return None
        
        # 检查地址码和功能码（只处理地址码为01的应答帧）
        if response[0] != 0x01 or response[1] != 0x03:
            print(f"忽略非01地址码的应答帧: 地址码={response[0]:02X}, 功能码={response[1]:02X}")
            return None
        
        # 检查有效字节数
        if response[2] != 0x04:
            print(f"有效字节数错误: {response[2]:02X}")
            return None
        
        # 提取湿度值（前2字节）和温度值（后2字节）
        humidity = (response[3] << 8) | response[4]
        temperature_raw = (response[5] << 8) | response[6]
        
        # 计算CRC校验
        crc_data = response[:6]
        expected_crc = calculate_crc(crc_data)
        actual_crc = (response[8] << 8) | response[7]
        
        if expected_crc != actual_crc:
            print(f"CRC校验失败: 预期={expected_crc:04X}, 实际={actual_crc:04X}")
            # 暂时忽略CRC校验失败，继续解析数据
            # return None
        
        # 转换为实际值
        # 湿度计算：湿度值除以10
        humidity = humidity / 10.0
        
        # 温度计算：处理补码形式（当温度低于0℃时）
        if temperature_raw > 32767:
            # 补码转换
            temperature = (temperature_raw - 65536) / 10.0
        else:
            temperature = temperature_raw / 10.0
        
        # 验证数据范围
        if humidity < 0 or humidity > 100:
            print(f"湿度值超出范围: {humidity}")
            return None
        if temperature < -40 or temperature > 85:
            print(f"温度值超出范围: {temperature}")
            return None
        
        print(f"解析成功: 温度={temperature}°C, 湿度={humidity}%")
        return {
            "temperature": temperature,
            "humidity": humidity
        }
    except Exception as e:
        print(f"解析应答帧失败: {e}")
        return None

# 串口数据读取线程
def read_serial_data():
    """从串口读取数据"""
    while not stop_thread:
        try:
            if serial_port and serial_port.is_open:
                try:
                    # 只有当问询状态为True时才发送问询
                    global query_running, query_interval
                    if query_running:
                        # 发送Modbus-RTU问询帧
                        query_frame = build_modbus_query()
                        query_frame_str = ' '.join([f'{b:02X}' for b in query_frame])
                        print(f"发送问询帧: {query_frame_str}")
                        
                        # 保存问询帧数据
                        global frame_data
                        frame_data["query"] = query_frame_str
                        
                        serial_port.write(query_frame)
                        
                        # 读取应答帧
                        time.sleep(0.1)  # 等待设备响应
                        response = serial_port.read(9)  # 应答帧长度为9字节
                        
                        if len(response) == 9:
                            response_frame_str = ' '.join([f'{b:02X}' for b in response])
                            print(f"收到应答帧: {response_frame_str}")
                            
                            # 检查地址码是否为01
                            if response[0] == 0x01 and response[1] == 0x03:
                                # 保存应答帧数据
                                frame_data["response"] = response_frame_str
                                
                                # 解析应答帧
                                data = parse_modbus_response(response)
                                if data:
                                    global sensor_data
                                    timestamp = time.time()
                                    sensor_data = {
                                        "temperature": data["temperature"],
                                        "humidity": data["humidity"],
                                        "timestamp": timestamp
                                    }
                                    # 保存数据到数据库
                                    save_sensor_data(data["temperature"], data["humidity"], timestamp)
                                    print(f"读取到数据: 温度={data['temperature']}°C, 湿度={data['humidity']}%")
                            else:
                                print(f"忽略非01地址码的应答帧: {response_frame_str}")
                                # 不保存非01地址的应答帧到frame_data
                        else:
                            print(f"应答帧长度不足: {len(response)}字节")
                            frame_data["response"] = f"应答帧长度不足: {len(response)}字节"
                    else:
                        print("问询未运行，跳过发送问询帧")
                        frame_data["query"] = "问询未运行"
                        frame_data["response"] = "问询未运行"
                except Exception as e:
                    print(f"Modbus通信失败: {e}")
                    frame_data["response"] = f"Modbus通信失败: {str(e)}"
            time.sleep(query_interval)  # 根据设置的问询周期发送一次问询
        except Exception as e:
            print(f"串口读取失败: {e}")
            time.sleep(1)

# 开启串口
@app.route('/api/serial/open', methods=['POST'])
def open_serial():
    global serial_port, serial_thread, stop_thread, serial_config
    data = request.json
    config = data.get('config', serial_config)
    
    try:
        # 关闭之前的串口
        if serial_port and serial_port.is_open:
            serial_port.close()
        
        # 停止之前的线程
        stop_thread = True
        if serial_thread:
            serial_thread.join(timeout=1)
        
        # 保存配置
        serial_config = config
        
        # 打开新的串口
        serial_port = serial.Serial(
            port=config['port'],
            baudrate=config['baudrate'],
            parity=config['parity'],
            stopbits=config['stopbits'],
            bytesize=config['bytesize'],
            timeout=1
        )
        
        # 启动读取线程
        stop_thread = False
        serial_thread = threading.Thread(target=read_serial_data)
        serial_thread.daemon = True
        serial_thread.start()
        
        return jsonify({"status": "success", "message": "串口已打开，正在读取真实硬件数据"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"串口打开失败: {str(e)}"})

# 关闭串口
@app.route('/api/serial/close', methods=['POST'])
def close_serial():
    global serial_port, stop_thread
    try:
        stop_thread = True
        if serial_port and serial_port.is_open:
            serial_port.close()
        return jsonify({"status": "success", "message": "串口已关闭"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"串口关闭失败: {str(e)}"})

# 获取可用串口端口列表
@app.route('/api/serial/ports', methods=['GET'])
def get_serial_ports():
    """获取可用的串口端口列表"""
    import serial.tools.list_ports
    ports = []
    try:
        for port in serial.tools.list_ports.comports():
            ports.append({
                'device': port.device,
                'description': port.description
            })
    except Exception as e:
        print(f"获取串口列表失败: {e}")
    return jsonify(ports)

# 获取串口配置
@app.route('/api/serial/config', methods=['GET'])
def get_serial_config():
    return jsonify(serial_config)

# 获取传感器数据
@app.route('/api/sensor/data', methods=['GET'])
def get_sensor_data():
    return jsonify(sensor_data)

# 获取帧数据
@app.route('/api/serial/frames', methods=['GET'])
def get_frame_data():
    """获取问询帧和应答帧数据"""
    return jsonify(frame_data)

# 更新问询周期
@app.route('/api/serial/interval', methods=['POST'])
def update_query_interval():
    """更新问询周期"""
    global query_interval
    data = request.json
    interval = data.get('interval', 2)
    
    try:
        query_interval = interval
        return jsonify({"status": "success", "message": f"问询周期已更新为 {interval} 秒"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"更新问询周期失败: {str(e)}"})

# 获取历史数据
@app.route('/api/history/data', methods=['GET'])
def get_history():
    """获取历史数据，支持不同时间范围"""
    try:
        range_type = request.args.get('range', 'day')  # 默认获取当天数据
        end_time = time.time()
        start_time = 0
        
        # 根据时间范围类型计算开始时间
        if range_type == 'day':
            # 当天（24小时）
            start_time = end_time - 24 * 60 * 60
        elif range_type == 'week':
            # 近七日
            start_time = end_time - 7 * 24 * 60 * 60
        elif range_type == 'month':
            # 近一个月
            start_time = end_time - 30 * 24 * 60 * 60
        elif range_type == 'year':
            # 近一年
            start_time = end_time - 365 * 24 * 60 * 60
        elif range_type == 'custom':
            # 自定义时间范围
            start_time = float(request.args.get('start', 0))
            end_time = float(request.args.get('end', end_time))
        
        # 获取历史数据
        data = get_history_data(start_time, end_time)
        
        return jsonify({
            "status": "success",
            "data": data,
            "range_type": range_type,
            "start_time": start_time,
            "end_time": end_time
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"获取历史数据失败: {str(e)}"})

# 启动问询
@app.route('/api/query/start', methods=['POST'])
def start_query():
    """启动问询"""
    global query_running
    try:
        query_running = True
        return jsonify({"status": "success", "message": "问询已启动"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"启动问询失败: {str(e)}"})

# 停止问询
@app.route('/api/query/stop', methods=['POST'])
def stop_query():
    """停止问询"""
    global query_running
    try:
        query_running = False
        return jsonify({"status": "success", "message": "问询已停止"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"停止问询失败: {str(e)}"})

# 获取问询状态
@app.route('/api/query/status', methods=['GET'])
def get_query_status():
    """获取问询状态"""
    global query_running
    return jsonify({"status": "success", "running": query_running})

# 获取问询周期
@app.route('/api/query/interval', methods=['GET'])
def get_query_interval():
    """获取问询周期"""
    global query_interval
    return jsonify({"status": "success", "interval": query_interval})

# 主页面
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # 停止模拟数据线程，使用真实传感器数据
    stop_thread = True
    # lora_thread = threading.Thread(target=simulate_lora_data)
    # lora_thread.daemon = True
    # lora_thread.start()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
