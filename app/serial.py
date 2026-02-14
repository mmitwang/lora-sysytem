"""串口服务模块"""

import serial
import threading
import time
import serial.tools.list_ports
from app.config import Config
from app.modbus import build_modbus_query, parse_modbus_response, parse_temperature_response, parse_frequency_response, parse_velocity_response, parse_acceleration_response, parse_light_gas_response, calculate_amplitude
from app.database import save_sensor_data, save_vibration_data, save_air_quality_data


class SerialService:
    """串口服务类"""
    
    def __init__(self):
        """初始化串口服务"""
        self.serial_port = None
        self.serial_thread = None
        self.stop_thread = False
        self.query_running = False
        self.query_interval = Config.DEFAULT_QUERY_INTERVAL
        self.serial_config = Config.DEFAULT_SERIAL_CONFIG.copy()
        self.frame_data = {"query": "", "response": ""}
        self.sensor_data = {"temperature": 0, "humidity": 0, "timestamp": 0}
        self.vibration_data = {
            "temperature": 0,
            "frequency_x": 0,
            "frequency_y": 0,
            "frequency_z": 0,
            "velocity_x": 0,
            "velocity_y": 0,
            "velocity_z": 0,
            "acceleration_x": 0,
            "acceleration_y": 0,
            "acceleration_z": 0,
            "amplitude_peak": 0,
            "amplitude_rms": 0,
            "status": "A",
            "status_text": "良好",
            "timestamp": 0
        }
        self.air_quality_data = {"aqi": 0, "pm25": 0, "pm10": 0, "co2": 0, "voc": 0, "timestamp": 0}
        self.light_gas_data = {
            "status": None,
            "temperature": None,
            "humidity": None,
            "co2": None,
            "pressure": None,
            "light": None,
            "timestamp": 0
        }
        
        # 设备振动标准配置（ISO2372）
        self.device_class = 1  # 默认设备分类
        self.vibration_limits = {
            1: { # Class I
                "A": 0.71,
                "B": 1.12,
                "C": 1.8,
                "D": 1.8
            },
            2: { # Class II
                "A": 1.12,
                "B": 1.8,
                "C": 2.8,
                "D": 2.8
            },
            3: { # Class III
                "A": 1.8,
                "B": 2.8,
                "C": 4.5,
                "D": 4.5
            },
            4: { # Class IV
                "A": 2.8,
                "B": 4.5,
                "C": 7.1,
                "D": 7.1
            }
        }
    
    def get_available_ports(self):
        """获取可用的串口端口列表"""
        ports = []
        try:
            print("开始扫描可用串口...")
            port_list = list(serial.tools.list_ports.comports())
            print(f"扫描到 {len(port_list)} 个串口")
            for port in port_list:
                print(f"串口: {port.device} - {port.description}")
                ports.append({
                    'device': port.device,
                    'description': port.description
                })
        except Exception as e:
            print(f"获取串口列表失败: {e}")
        return ports
    
    def open_serial(self, config=None):
        """打开串口"""
        try:
            # 关闭之前的串口
            self.close_serial()
            
            # 使用新配置
            if config:
                self.serial_config.update(config)
            
            # 打开新的串口
            self.serial_port = serial.Serial(
                port=self.serial_config['port'],
                baudrate=self.serial_config['baudrate'],
                parity=self.serial_config['parity'],
                stopbits=self.serial_config['stopbits'],
                bytesize=self.serial_config['bytesize'],
                timeout=1
            )
            
            # 启动读取线程
            self.stop_thread = False
            self.serial_thread = threading.Thread(target=self.read_serial_data)
            self.serial_thread.daemon = True
            self.serial_thread.start()
            
            return True, "串口已打开"
        except Exception as e:
            return False, f"串口打开失败: {str(e)}"
    
    def close_serial(self):
        """关闭串口"""
        try:
            self.stop_thread = True
            if self.serial_thread:
                self.serial_thread.join(timeout=1)
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
            self.serial_port = None
            return True, "串口已关闭"
        except Exception as e:
            return False, f"串口关闭失败: {str(e)}"
    
    def read_serial_data(self):
        """从串口读取数据"""
        while not self.stop_thread:
            try:
                if self.serial_port and self.serial_port.is_open:
                    try:
                        # 只有当问询状态为True时才发送问询
                        if self.query_running:
                            # 读取光照气体数据
                            # 构建与用户提供格式一致的问询帧: 01 03 00 00 00 08 44 0C
                            light_gas_query = build_modbus_query(
                                slave_id=0x01,         # 地址码: 01H
                                function_code=0x03,     # 功能码: 03H
                                start_address=0x0000,   # 起始寄存器: 0000H
                                register_count=0x0008    # 寄存器个数: 0008H
                            )
                            light_gas_query_str = ' '.join([f'{b:02X}' for b in light_gas_query])
                            print(f"发送光照气体问询帧: {light_gas_query_str}")
                            self.serial_port.write(light_gas_query)
                            time.sleep(0.1)
                            light_gas_response = self.serial_port.read(21)  # 读取21字节以获取完整的应答帧
                            
                            # 解析光照气体数据
                            timestamp = time.time()
                            
                            # 解析光照气体应答帧
                            print(f"收到光照气体应答帧长度: {len(light_gas_response)}")
                            print(f"光照气体应答帧内容: {[f'{b:02X}' for b in light_gas_response]}")
                            
                            # 检查应答帧长度是否符合预期（21字节）
                            if len(light_gas_response) >= 21:
                                light_gas_result = parse_light_gas_response(light_gas_response)
                                if light_gas_result:
                                    # 更新光照气体数据
                                    self.light_gas_data = {
                                        "status": light_gas_result["status"],
                                        "temperature": light_gas_result["temperature"],
                                        "humidity": light_gas_result["humidity"],
                                        "co2": light_gas_result["co2"],
                                        "pressure": light_gas_result["pressure"],
                                        "light": light_gas_result["light"],
                                        "timestamp": timestamp
                                    }
                                    print(f"解析到光照气体数据: {self.light_gas_data}")
                                else:
                                    print("光照气体解析失败，保持之前的数据")
                                    # 只更新时间戳，保持其他数据不变
                                    self.light_gas_data["timestamp"] = timestamp
                            else:
                                print(f"光照气体应答帧长度不足，保持之前的数据，长度: {len(light_gas_response)}")
                                # 只更新时间戳，保持其他数据不变
                                self.light_gas_data["timestamp"] = timestamp
                            
                            # 保存帧数据（只显示十六进制字节）
                            light_gas_query_str = ' '.join([f'{b:02X}' for b in light_gas_query])
                            light_gas_response_str = ' '.join([f'{b:02X}' for b in light_gas_response])
                            
                            # 保存所有问询帧和应答帧
                            self.frame_data["query"] = light_gas_query_str
                            self.frame_data["response"] = light_gas_response_str
                        else:
                            print("问询未运行，跳过发送问询帧")
                            self.frame_data["query"] = "问询未运行"
                            self.frame_data["response"] = "问询未运行"
                    except Exception as e:
                        print(f"Modbus通信失败: {e}")
                        self.frame_data["response"] = f"Modbus通信失败: {str(e)}"
                time.sleep(self.query_interval)  # 根据设置的问询周期发送一次问询
            except Exception as e:
                print(f"串口读取失败: {e}")
                time.sleep(1)
    
    def start_query(self):
        """启动问询"""
        self.query_running = True
        return True, "问询已启动"
    
    def stop_query(self):
        """停止问询"""
        self.query_running = False
        return True, "问询已停止"
    
    def update_query_interval(self, interval):
        """更新问询周期"""
        if interval < Config.MIN_QUERY_INTERVAL:
            interval = Config.MIN_QUERY_INTERVAL
        elif interval > Config.MAX_QUERY_INTERVAL:
            interval = Config.MAX_QUERY_INTERVAL
        self.query_interval = interval
        return True, f"问询周期已更新为 {interval} 秒"
    
    def get_serial_status(self):
        """获取串口状态"""
        return {
            "is_open": self.serial_port is not None and self.serial_port.is_open,
            "query_running": self.query_running,
            "query_interval": self.query_interval,
            "serial_config": self.serial_config
        }
    
    def get_frame_data(self):
        """获取帧数据"""
        return self.frame_data
    
    def get_sensor_data(self):
        """获取传感器数据"""
        return self.sensor_data
    
    def get_vibration_data(self):
        """获取温振数据"""
        return self.vibration_data
    
    def get_air_quality_data(self):
        """获取空气质量数据"""
        return self.air_quality_data
    
    def get_light_gas_data(self):
        """获取光照气体数据"""
        return self.light_gas_data
    
    def update_device_class(self, device_class):
        """更新设备分类"""
        if device_class in [1, 2, 3, 4]:
            self.device_class = device_class
            return True, f"设备分类已更新为 Class {device_class}"
        else:
            return False, "设备分类无效，必须是1-4之间的整数"
    
    def get_device_class(self):
        """获取设备分类"""
        return self.device_class
    
    def evaluate_vibration_status(self, velocity_data):
        """根据ISO2372标准评估设备振动状态"""
        # 获取振动速度有效值（RMS）的最大值（XYZ三个轴）
        velocity_rms = max(
            velocity_data.get("velocity_x", 0),
            velocity_data.get("velocity_y", 0),
            velocity_data.get("velocity_z", 0)
        )
        
        # 根据设备分类和ISO2372标准评估设备状态
        limits = self.vibration_limits[self.device_class]
        status = "A"
        status_text = "良好"
        
        if velocity_rms <= limits["A"]:
            status = "A"
            status_text = "良好"
        elif velocity_rms <= limits["B"]:
            status = "B"
            status_text = "可接受"
        elif velocity_rms <= limits["C"]:
            status = "C"
            status_text = "注意"
        else:
            status = "D"
            status_text = "不允许"
        
        return status, status_text


# 创建全局串口服务实例
serial_service = SerialService()
