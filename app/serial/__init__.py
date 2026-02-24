"""串口服务模块"""

import threading
import time
from datetime import datetime
from app.config import Config

# 创建全局串口锁，确保同一时间只有一个页面使用串口
serial_lock = threading.Lock()
from app.database import save_sensor_data, save_vibration_data, save_air_quality_data

# 避免循环导入，在类初始化时导入



class SerialService:
    """串口服务类"""
    
    def __init__(self):
        """初始化串口服务"""
        # 每个页面的独立配置
        self.pages = {
            "light": {
                "serial_port": None,
                "serial_thread": None,
                "stop_thread": False,
                "query_running": False,
                "query_interval": Config.DEFAULT_QUERY_INTERVAL,
                "serial_config": Config.DEFAULT_SERIAL_CONFIG.copy(),
                "communication_mode": "tcp",  # 默认通讯模式
                "network_type": "lora",  # 默认网络类型
                "target_address": "5678",  # 默认LoRa目标地址
                "tcp_server_ip": "192.168.0.80",  # 默认TCP服务器IP
                "tcp_server_port": 10125,  # 默认TCP服务器端口
                "frame_data": {"query": "", "response": "", "frames": []},
                "data": {
                    "status": None,
                    "temperature": None,
                    "humidity": None,
                    "co2": None,
                    "pressure": None,
                    "light": None,
                    "timestamp": 0
                }
            },
            "temperature": {
                "serial_port": None,
                "serial_thread": None,
                "stop_thread": False,
                "query_running": False,
                "query_interval": Config.DEFAULT_QUERY_INTERVAL,
                "serial_config": Config.DEFAULT_SERIAL_CONFIG.copy(),
                "communication_mode": "tcp",  # 默认通讯模式
                "network_type": "serial",  # 默认网络类型
                "target_address": "0002",  # 默认LoRa目标地址
                "tcp_server_ip": "192.168.0.80",  # 默认TCP服务器IP
                "tcp_server_port": 10125,  # 默认TCP服务器端口
                "frame_data": {"query": "", "response": "", "frames": []},
                "data": {
                    "temperature": 0,
                    "humidity": 0,
                    "timestamp": 0
                }
            },
            "vibration": {
                "serial_port": None,
                "serial_thread": None,
                "stop_thread": False,
                "query_running": False,
                "query_interval": Config.DEFAULT_QUERY_INTERVAL,
                "serial_config": Config.DEFAULT_SERIAL_CONFIG.copy(),
                "communication_mode": "tcp",  # 默认通讯模式
                "network_type": "lora",  # 默认网络类型
                "target_address": "0003",  # 默认LoRa目标地址
                "tcp_server_ip": "192.168.0.80",  # 默认TCP服务器IP
                "tcp_server_port": 10125,  # 默认TCP服务器端口
                "frame_data": {"query": "", "response": "", "frames": []},
                "data": {
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
                    "displacement_x": 0,
                    "displacement_y": 0,
                    "displacement_z": 0,
                    "resultant_velocity": 0,
                    "resultant_displacement": 0,
                    "resultant_acceleration": 0,
                    "version": 0,
                    "status": "A",
                    "status_text": "良好",
                    "timestamp": 0
                }
            },
            "config": {
                "serial_port": None,
                "serial_thread": None,
                "stop_thread": False,
                "query_running": False,
                "query_interval": Config.DEFAULT_QUERY_INTERVAL,
                "serial_config": Config.DEFAULT_SERIAL_CONFIG.copy(),
                "communication_mode": "tcp",  # 默认通讯模式
                "network_type": "lora",  # 默认网络类型
                "target_address": "5678",  # 默认LoRa目标地址
                "tcp_server_ip": "192.168.0.80",  # 默认TCP服务器IP
                "tcp_server_port": 10125,  # 默认TCP服务器端口
                "frame_data": {"query": "", "response": "", "frames": []},
                "data": {
                    "timestamp": 0
                }
            },
            "sscom": {
                "serial_port": None,
                "serial_thread": None,
                "stop_thread": False,
                "query_running": False,
                "immediate_query": False,
                "query_interval": Config.DEFAULT_QUERY_INTERVAL,
                "serial_config": Config.DEFAULT_SERIAL_CONFIG.copy(),
                "communication_mode": "tcp",
                "network_type": "lora",
                "target_address": "5678",
                "tcp_server_ip": "192.168.0.80",
                "tcp_server_port": 10125,
                "tcp_socket": None,
                "tcp_connected": False,
                "frame_data": {"query": "", "response": "", "frames": []},
                "data": {
                    "status": None,
                    "temperature": None,
                    "humidity": None,
                    "co2": None,
                    "pressure": None,
                    "light": None,
                    "timestamp": 0
                }
            }
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
        
        # 避免循环导入，在初始化时导入
        from app.serial.serial_port import SerialPortHandler
        from app.serial.tcp import TCPHandler
        from app.serial.frame_handler import FrameHandler
        from app.serial.config import SerialConfig
        
        # 初始化处理器
        self.serial_handler = SerialPortHandler()
        self.tcp_handler = TCPHandler()
        self.frame_handler = FrameHandler()
        self.config = SerialConfig()
    
    def get_available_ports(self):
        """获取可用的串口端口列表"""
        return self.serial_handler.get_available_ports()
    
    def open_serial(self, config=None, page="light"):
        """打开串口"""
        return self.serial_handler.open_serial(self, config, page)
    
    def close_serial(self, page="light"):
        """关闭串口"""
        return self.serial_handler.close_serial(self, page)
    
    def open_tcp(self, tcp_server_ip, tcp_server_port, page="light"):
        """打开TCP通讯"""
        return self.tcp_handler.open_tcp(self, tcp_server_ip, tcp_server_port, page)
    
    def close_tcp(self, page="light"):
        """关闭TCP通讯"""
        return self.tcp_handler.close_tcp(self, page)
    
    def read_serial_data(self, page):
        """从串口或TCP读取数据"""
        print(f"{page}页面: 启动读取线程")
        page_config = self.pages.get(page, self.pages["light"])
        # 不立即发送问询，等待用户点击启动问询
        page_config["immediate_query"] = False
        
        while not page_config["stop_thread"]:
            try:
                # 获取当前通讯模式
                communication_mode = page_config.get("communication_mode", "serial")
                
                # 只在问询运行时发送数据
                if page_config["query_running"]:
                    if communication_mode == "tcp":
                        # TCP网络通讯
                        print(f"{page}页面: 执行TCP通讯")
                        timestamp = time.time()
                        self.tcp_handler.handle_communication(self, page, timestamp)
                    else:
                        # 串口通讯
                        print(f"{page}页面: 进入串口通讯模式")
                        timestamp = time.time()
                        self.serial_handler.handle_communication(self, page, timestamp)
                
                # 等待下一次问询
                time.sleep(Config.DEFAULT_QUERY_INTERVAL)
            except Exception as e:
                print(f"{page}页面: 读取数据错误: {str(e)}")
                time.sleep(1)

    def get_serial_status(self, page="light"):
        """获取串口状态"""
        page_config = self.pages.get(page, self.pages["light"])
        return {
            "is_open": page_config["serial_port"] and page_config["serial_port"].is_open,
            "serial_config": page_config["serial_config"],
            "query_running": page_config["query_running"],
            "query_interval": page_config["query_interval"],
            "network_type": page_config.get("network_type", "serial"),
            "target_address": page_config.get("target_address", "5678"),
            "tcp_server_ip": page_config.get("tcp_server_ip", "192.168.0.80"),
            "tcp_server_port": page_config.get("tcp_server_port", 10125),
            "tcp_connected": page_config.get("tcp_connected", False),
            "communication_mode": page_config.get("communication_mode", "tcp")
        }
    
    def get_frame_data(self, page="light"):
        """获取问询帧和应答帧数据"""
        page_config = self.pages.get(page, self.pages["light"])
        return page_config["frame_data"]
    
    def start_query(self, page="light"):
        """启动问询"""
        try:
            page_config = self.pages.get(page, self.pages["light"])
            page_config["query_running"] = True
            page_config["immediate_query"] = True
            return True, f"{page}页面问询已启动"
        except Exception as e:
            return False, f"启动问询失败: {str(e)}"
    
    def stop_query(self, page="light"):
        """停止问询"""
        try:
            page_config = self.pages.get(page, self.pages["light"])
            page_config["query_running"] = False
            # 清空数据，显示--
            page_config["data"] = {
                "temperature": None,
                "frequency_x": None,
                "frequency_y": None,
                "frequency_z": None,
                "velocity_x": None,
                "velocity_y": None,
                "velocity_z": None,
                "acceleration_x": None,
                "acceleration_y": None,
                "acceleration_z": None,
                "displacement_x": None,
                "displacement_y": None,
                "displacement_z": None,
                "resultant_velocity": None,
                "resultant_displacement": None,
                "resultant_acceleration": None,
                "version": None,
                "status": "A",
                "status_text": "良好",
                "timestamp": 0
            } if page == "vibration" else {
                "temperature": None,
                "humidity": None,
                "timestamp": 0
            } if page == "temperature" else {
                "status": None,
                "temperature": None,
                "humidity": None,
                "co2": None,
                "pressure": None,
                "light": None,
                "timestamp": 0
            }
            return True, f"{page}页面问询已停止，数据已清空"
        except Exception as e:
            return False, f"停止问询失败: {str(e)}"
    
    def update_query_interval(self, interval, page="light"):
        """更新问询周期"""
        try:
            page_config = self.pages.get(page, self.pages["light"])
            page_config["query_interval"] = interval
            return True, f"{page}页面问询周期已更新为 {interval} 秒"
        except Exception as e:
            return False, f"更新问询周期失败: {str(e)}"
    
    def get_light_gas_data(self):
        """获取光照气体数据"""
        page_config = self.pages.get("light", self.pages["light"])
        return page_config["data"]
    
    def get_sensor_data(self, page="temperature"):
        """获取传感器数据"""
        page_config = self.pages.get(page, self.pages["temperature"])
        return page_config["data"]
    
    def get_vibration_data(self):
        """获取温振数据"""
        page_config = self.pages.get("vibration", self.pages["vibration"])
        return page_config["data"]
    
    def update_device_class(self, device_class):
        """更新设备分类"""
        try:
            if device_class in self.vibration_limits:
                self.device_class = device_class
                return True, f"设备分类已更新为 Class {device_class}"
            else:
                return False, "无效的设备分类"
        except Exception as e:
            return False, f"更新设备分类失败: {str(e)}"
    
    def get_device_class(self):
        """获取设备分类"""
        return self.device_class
    
    def update_network_config(self, network_type, target_address, page="light"):
        """更新网络配置"""
        try:
            page_config = self.pages.get(page, self.pages["light"])
            page_config["network_type"] = network_type
            page_config["target_address"] = target_address
            return True, f"网络配置已更新: 网络类型={network_type}, 目标地址={target_address}"
        except Exception as e:
            return False, f"更新网络配置失败: {str(e)}"
    
    def update_communication_config(self, communication_mode, network_type, target_address, config, page="light"):
        """更新通讯配置"""
        try:
            page_config = self.pages.get(page, self.pages["light"])
            page_config["communication_mode"] = communication_mode
            page_config["network_type"] = network_type
            page_config["target_address"] = target_address
            if config:
                page_config["serial_config"].update(config)
            return True, f"通讯配置已更新"
        except Exception as e:
            return False, f"更新通讯配置失败: {str(e)}"
    
    def update_lora_config(self, network_type, target_address, page="light"):
        """更新LoRa配置"""
        try:
            page_config = self.pages.get(page, self.pages["light"])
            page_config["network_type"] = network_type
            page_config["target_address"] = target_address
            return True, f"LoRa配置已更新: 网络类型={network_type}, 目标地址={target_address}"
        except Exception as e:
            return False, f"更新LoRa配置失败: {str(e)}"
    
    def update_tcp_config(self, tcp_server_ip, tcp_server_port, page="light"):
        """更新TCP配置"""
        try:
            page_config = self.pages.get(page, self.pages["light"])
            page_config["tcp_server_ip"] = tcp_server_ip
            page_config["tcp_server_port"] = tcp_server_port
            return True, f"TCP配置已更新: IP={tcp_server_ip}, 端口={tcp_server_port}"
        except Exception as e:
            return False, f"更新TCP配置失败: {str(e)}"
    
    def clear_frame_history(self, page="light"):
        """清空帧数据历史记录"""
        try:
            page_config = self.pages.get(page, self.pages["light"])
            page_config["frame_data"]["frames"] = []
            page_config["frame_data"]["query"] = ""
            page_config["frame_data"]["response"] = ""
            return True, f"{page}页面帧数据历史记录已清空"
        except Exception as e:
            return False, f"清空帧数据历史记录失败: {str(e)}"

# 创建全局串口服务实例
serial_service = SerialService()
