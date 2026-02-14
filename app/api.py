"""API路由模块"""

from flask import Blueprint, request, jsonify
import time
from app.serial import serial_service
from app.database import get_history_data, get_config, set_config

# 创建API蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/serial/ports', methods=['GET'])
def get_serial_ports():
    """获取可用的串口端口列表"""
    ports = serial_service.get_available_ports()
    return jsonify(ports)


@api_bp.route('/serial/open', methods=['POST'])
def open_serial():
    """打开串口"""
    data = request.json
    config = data.get('config', {})
    success, message = serial_service.open_serial(config)
    return jsonify({"status": "success" if success else "error", "message": message})


@api_bp.route('/serial/close', methods=['POST'])
def close_serial():
    """关闭串口"""
    success, message = serial_service.close_serial()
    return jsonify({"status": "success" if success else "error", "message": message})


@api_bp.route('/serial/config', methods=['GET'])
def get_serial_config():
    """获取串口配置"""
    status = serial_service.get_serial_status()
    return jsonify(status['serial_config'])


@api_bp.route('/serial/status', methods=['GET'])
def get_serial_status():
    """获取串口状态"""
    status = serial_service.get_serial_status()
    return jsonify(status)


@api_bp.route('/serial/frames', methods=['GET'])
def get_frame_data():
    """获取问询帧和应答帧数据"""
    frame_data = serial_service.get_frame_data()
    return jsonify(frame_data)


@api_bp.route('/query/start', methods=['POST'])
def start_query():
    """启动问询"""
    success, message = serial_service.start_query()
    return jsonify({"status": "success" if success else "error", "message": message})


@api_bp.route('/query/stop', methods=['POST'])
def stop_query():
    """停止问询"""
    success, message = serial_service.stop_query()
    return jsonify({"status": "success" if success else "error", "message": message})


@api_bp.route('/query/status', methods=['GET'])
def get_query_status():
    """获取问询状态"""
    status = serial_service.get_serial_status()
    return jsonify({"status": "success", "running": status['query_running']})


@api_bp.route('/serial/interval', methods=['POST'])
def update_query_interval():
    """更新问询周期"""
    data = request.json
    interval = data.get('interval', 2)
    success, message = serial_service.update_query_interval(interval)
    return jsonify({"status": "success" if success else "error", "message": message})


@api_bp.route('/query/interval', methods=['GET'])
def get_query_interval():
    """获取问询周期"""
    status = serial_service.get_serial_status()
    return jsonify({"status": "success", "interval": status['query_interval']})


@api_bp.route('/vibration/device-class', methods=['POST'])
def update_device_class():
    """更新设备分类"""
    data = request.json
    device_class = data.get('device_class', 1)
    success, message = serial_service.update_device_class(device_class)
    return jsonify({"status": "success" if success else "error", "message": message})


@api_bp.route('/vibration/device-class', methods=['GET'])
def get_device_class():
    """获取设备分类"""
    device_class = serial_service.get_device_class()
    return jsonify({"status": "success", "device_class": device_class})


@api_bp.route('/sensor/data', methods=['GET'])
def get_sensor_data():
    """获取传感器数据"""
    # 获取光照气体数据
    light_gas_data = serial_service.get_light_gas_data()
    # 如果有光照气体数据，则返回光照气体数据
    if light_gas_data:
        return jsonify(light_gas_data)
    # 否则返回传统传感器数据
    sensor_data = serial_service.get_sensor_data()
    return jsonify(sensor_data)


@api_bp.route('/light/data', methods=['GET'])
def get_light_data():
    """获取光照气体数据"""
    light_gas_data = serial_service.get_light_gas_data()
    return jsonify(light_gas_data)


@api_bp.route('/vibration/data', methods=['GET'])
def get_vibration_data():
    """获取温振数据"""
    vibration_data = serial_service.get_vibration_data()
    return jsonify(vibration_data)


@api_bp.route('/air/data', methods=['GET'])
def get_air_quality_data():
    """获取空气质量数据"""
    air_quality_data = serial_service.get_air_quality_data()
    return jsonify(air_quality_data)


@api_bp.route('/history/data', methods=['GET'])
def get_history():
    """获取历史数据，支持不同时间范围"""
    try:
        range_type = request.args.get('range', 'day')  # 默认获取当天数据
        end_time = time.time()
        start_time = 0
        table = request.args.get('table', 'sensor_history')  # 默认获取温湿度数据
        
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
        data = get_history_data(start_time, end_time, table)
        
        return jsonify({
            "status": "success",
            "data": data,
            "range_type": range_type,
            "start_time": start_time,
            "end_time": end_time
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"获取历史数据失败: {str(e)}"})


@api_bp.route('/config/get', methods=['GET'])
def get_config_value():
    """获取配置值"""
    key = request.args.get('key')
    default = request.args.get('default')
    value = get_config(key, default)
    return jsonify({"status": "success", "key": key, "value": value})


@api_bp.route('/config/set', methods=['POST'])
def set_config_value():
    """设置配置值"""
    data = request.json
    key = data.get('key')
    value = data.get('value')
    if not key:
        return jsonify({"status": "error", "message": "缺少key参数"})
    set_config(key, value)
    return jsonify({"status": "success", "message": f"配置 {key} 已更新"})


@api_bp.route('/system/status', methods=['GET'])
def get_system_status():
    """获取系统状态"""
    serial_status = serial_service.get_serial_status()
    system_status = {
        "serial": {
            "is_open": serial_status['is_open'],
            "port": serial_status['serial_config']['port']
        },
        "query": {
            "running": serial_status['query_running'],
            "interval": serial_status['query_interval']
        },
        "timestamp": time.time()
    }
    return jsonify({"status": "success", "data": system_status})
