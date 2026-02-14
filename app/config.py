"""应用配置模块"""

import os
from datetime import timedelta


class Config:
    """应用配置类"""
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-for-iot-system'
    DEBUG = True
    
    # 数据库配置
    DATABASE_URL = 'sqlite:///iot_data.db'
    DATABASE_FILE = 'iot_data.db'
    
    # 串口默认配置
    DEFAULT_SERIAL_CONFIG = {
        'port': 'COM3',
        'baudrate': 9600,
        'parity': 'N',
        'stopbits': 1,
        'bytesize': 8
    }
    
    # 问询配置
    DEFAULT_QUERY_INTERVAL = 2  # 默认问询周期（秒）
    MAX_QUERY_INTERVAL = 60  # 最大问询周期（秒）
    MIN_QUERY_INTERVAL = 1  # 最小问询周期（秒）
    
    # 数据处理配置
    MAX_DATA_POINTS = 1000  # 图表最大数据点
    HISTORY_CHART_POINTS = 200  # 历史图表数据点
    
    # Modbus-RTU配置
    MODBUS_SLAVE_ID = 0x01  # 从设备地址
    MODBUS_FUNCTION_CODE = 0x03  # 功能码
    MODBUS_START_ADDRESS = 0x0000  # 起始地址
    MODBUS_REGISTER_COUNT = 0x0008  # 寄存器数量（根据新协议，读取8个寄存器）
    
    # 数据范围验证
    TEMPERATURE_RANGE = (-40, 85)  # 温度范围
    HUMIDITY_RANGE = (0, 100)  # 湿度范围
    
    # 定时任务配置
    SCHEDULER_API_ENABLED = True
    
    # CORS配置
    CORS_HEADERS = 'Content-Type'
