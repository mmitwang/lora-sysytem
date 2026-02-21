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
    page = data.get('page', 'light')
    success, message = serial_service.open_serial(config, page)
    return jsonify({"status": "success" if success else "error", "message": message})


@api_bp.route('/serial/close', methods=['POST'])
def close_serial():
    """关闭串口"""
    data = request.json
    page = data.get('page', 'light')
    success, message = serial_service.close_serial(page)
    return jsonify({"status": "success" if success else "error", "message": message})


@api_bp.route('/serial/open-tcp', methods=['POST'])
def open_tcp():
    """打开TCP通讯"""
    data = request.json
    tcp_server_ip = data.get('tcp_server_ip', '127.0.0.1')
    tcp_server_port = data.get('tcp_server_port', 502)
    page = data.get('page', 'light')
    success, message = serial_service.open_tcp(tcp_server_ip, tcp_server_port, page)
    return jsonify({"status": "success" if success else "error", "message": message})


@api_bp.route('/serial/close-tcp', methods=['POST'])
def close_tcp():
    """关闭TCP通讯"""
    data = request.json
    page = data.get('page', 'light')
    success, message = serial_service.close_tcp(page)
    return jsonify({"status": "success" if success else "error", "message": message})


@api_bp.route('/serial/config', methods=['GET'])
def get_serial_config():
    """获取串口配置"""
    page = request.args.get('page', 'light')
    status = serial_service.get_serial_status(page)
    return jsonify(status['serial_config'])


@api_bp.route('/serial/status', methods=['GET'])
def get_serial_status():
    """获取串口状态"""
    page = request.args.get('page', 'light')
    status = serial_service.get_serial_status(page)
    return jsonify(status)


@api_bp.route('/serial/frames', methods=['GET'])
def get_frame_data():
    """获取问询帧和应答帧数据"""
    page = request.args.get('page', 'light')
    frame_data = serial_service.get_frame_data(page)
    return jsonify(frame_data)


@api_bp.route('/query/start', methods=['POST'])
def start_query():
    """启动问询"""
    data = request.json
    page = data.get('page', 'light')
    success, message = serial_service.start_query(page)
    return jsonify({"status": "success" if success else "error", "message": message})


@api_bp.route('/query/stop', methods=['POST'])
def stop_query():
    """停止问询"""
    data = request.json
    page = data.get('page', 'light')
    success, message = serial_service.stop_query(page)
    return jsonify({"status": "success" if success else "error", "message": message})


@api_bp.route('/query/status', methods=['GET'])
def get_query_status():
    """获取问询状态"""
    page = request.args.get('page', 'light')
    status = serial_service.get_serial_status(page)
    return jsonify({"status": "success", "running": status['query_running']})


@api_bp.route('/serial/interval', methods=['POST'])
def update_query_interval():
    """更新问询周期"""
    data = request.json
    interval = data.get('interval', 2)
    page = data.get('page', 'light')
    success, message = serial_service.update_query_interval(interval, page)
    return jsonify({"status": "success" if success else "error", "message": message})


@api_bp.route('/query/interval', methods=['GET'])
def get_query_interval():
    """获取问询周期"""
    page = request.args.get('page', 'light')
    status = serial_service.get_serial_status(page)
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
    page = request.args.get('page', 'temperature')
    if page == 'light':
        # 获取光照气体数据
        light_gas_data = serial_service.get_light_gas_data()
        return jsonify(light_gas_data)
    else:
        # 返回传统传感器数据
        sensor_data = serial_service.get_sensor_data(page)
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
    # 简化处理，返回默认数据
    return jsonify({"aqi": 0, "pm25": 0, "pm10": 0, "co2": 0, "voc": 0, "timestamp": time.time()})


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
    page = request.args.get('page', 'light')
    serial_status = serial_service.get_serial_status(page)
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


@api_bp.route('/serial/network-config', methods=['GET'])
def get_network_config():
    """获取网络配置"""
    page = request.args.get('page', 'light')
    status = serial_service.get_serial_status(page)
    return jsonify({
        "network_type": status.get('network_type', 'modbus'),
        "target_address": status.get('target_address', '5678')
    })


@api_bp.route('/serial/network-config', methods=['POST'])
def update_network_config():
    """更新网络配置"""
    data = request.json
    network_type = data.get('network_type', 'modbus')
    target_address = data.get('target_address', '5678')
    page = data.get('page', 'light')
    success, message = serial_service.update_network_config(network_type, target_address, page)
    return jsonify({"status": "success" if success else "error", "message": message})


@api_bp.route('/serial/tcp-config', methods=['GET'])
def get_tcp_config():
    """获取TCP配置"""
    page = request.args.get('page', 'light')
    status = serial_service.get_serial_status(page)
    return jsonify({
        "tcp_server_ip": status.get('tcp_server_ip', '127.0.0.1'),
        "tcp_server_port": status.get('tcp_server_port', 502)
    })


@api_bp.route('/serial/tcp-config', methods=['POST'])
def update_tcp_config():
    """更新TCP配置"""
    data = request.json
    tcp_server_ip = data.get('tcp_server_ip', '127.0.0.1')
    tcp_server_port = data.get('tcp_server_port', 502)
    page = data.get('page', 'light')
    success, message = serial_service.update_tcp_config(tcp_server_ip, tcp_server_port, page)
    return jsonify({"status": "success" if success else "error", "message": message})


@api_bp.route('/serial/communication-config', methods=['POST'])
def update_communication_config():
    """更新通讯配置"""
    data = request.json
    communication_mode = data.get('communication_mode', 'serial')
    network_type = data.get('network_type', 'modbus')
    target_address = data.get('target_address', '5678')
    config = data.get('config', {})
    page = data.get('page', 'light')
    success, message = serial_service.update_communication_config(communication_mode, network_type, target_address, config, page)
    return jsonify({"status": "success" if success else "error", "message": message})


@api_bp.route('/serial/lora-config', methods=['GET'])
def get_lora_config():
    """获取LoRa配置"""
    page = request.args.get('page', 'light')
    status = serial_service.get_serial_status(page)
    return jsonify({
        "network_type": status.get('network_type', 'modbus'),
        "target_address": status.get('target_address', '5678')
    })


@api_bp.route('/serial/lora-config', methods=['POST'])
def update_lora_config():
    """更新LoRa配置"""
    data = request.json
    network_type = data.get('network_type', 'modbus')
    target_address = data.get('target_address', '5678')
    page = data.get('page', 'light')
    success, message = serial_service.update_lora_config(network_type, target_address, page)
    return jsonify({"status": "success" if success else "error", "message": message})
