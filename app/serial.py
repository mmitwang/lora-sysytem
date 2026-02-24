"""串口服务模块"""

# 导入新的模块结构
from app.serial import serial_service
from app.serial import SerialService

# 导出串口服务实例
__all__ = ['serial_service', 'SerialService']
