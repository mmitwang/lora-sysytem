"""工具函数模块"""

import time
import datetime
import json
from app.config import Config


def format_timestamp(timestamp):
    """格式化时间戳为可读时间"""
    if not timestamp:
        return "--"
    try:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
    except Exception as e:
        print(f"时间格式化失败: {e}")
        return "--"


def format_datetime(dt):
    """格式化日期时间对象为可读时间"""
    if not dt:
        return "--"
    try:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"日期时间格式化失败: {e}")
        return "--"


def get_current_timestamp():
    """获取当前时间戳"""
    return time.time()


def get_current_datetime():
    """获取当前日期时间对象"""
    return datetime.datetime.now()


def get_current_time_str():
    """获取当前时间字符串"""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def calculate_time_diff(start_time, end_time=None):
    """计算时间差（秒）"""
    if end_time is None:
        end_time = time.time()
    return end_time - start_time


def calculate_time_diff_str(start_time, end_time=None):
    """计算时间差并返回可读字符串"""
    seconds = calculate_time_diff(start_time, end_time)
    if seconds < 60:
        return f"{int(seconds)}秒"
    elif seconds < 3600:
        return f"{int(seconds/60)}分{int(seconds%60)}秒"
    elif seconds < 86400:
        return f"{int(seconds/3600)}小时{int((seconds%3600)/60)}分"
    else:
        return f"{int(seconds/86400)}天{int((seconds%86400)/3600)}小时"


def validate_temperature(temperature):
    """验证温度值是否在合理范围内"""
    if temperature is None:
        return False
    try:
        temp = float(temperature)
        return Config.TEMPERATURE_RANGE[0] <= temp <= Config.TEMPERATURE_RANGE[1]
    except (ValueError, TypeError):
        return False


def validate_humidity(humidity):
    """验证湿度值是否在合理范围内"""
    if humidity is None:
        return False
    try:
        hum = float(humidity)
        return Config.HUMIDITY_RANGE[0] <= hum <= Config.HUMIDITY_RANGE[1]
    except (ValueError, TypeError):
        return False


def validate_query_interval(interval):
    """验证问询周期是否在合理范围内"""
    if interval is None:
        return False
    try:
        intv = float(interval)
        return Config.MIN_QUERY_INTERVAL <= intv <= Config.MAX_QUERY_INTERVAL
    except (ValueError, TypeError):
        return False


def format_bytes_to_hex(bytes_data):
    """将字节数据格式化为十六进制字符串"""
    if not bytes_data:
        return ""
    try:
        return ' '.join([f'{b:02X}' for b in bytes_data])
    except Exception as e:
        print(f"字节格式化失败: {e}")
        return ""


def parse_hex_string(hex_str):
    """将十六进制字符串解析为字节数据"""
    if not hex_str:
        return b''
    try:
        hex_str = hex_str.replace(' ', '')
        if len(hex_str) % 2 != 0:
            hex_str = '0' + hex_str
        return bytes.fromhex(hex_str)
    except Exception as e:
        print(f"十六进制解析失败: {e}")
        return b''


def safe_json_loads(json_str, default=None):
    """安全地解析JSON字符串"""
    if not json_str:
        return default
    try:
        return json.loads(json_str)
    except Exception as e:
        print(f"JSON解析失败: {e}")
        return default


def safe_json_dumps(data, default=None):
    """安全地序列化对象为JSON字符串"""
    try:
        return json.dumps(data, ensure_ascii=False, default=default)
    except Exception as e:
        print(f"JSON序列化失败: {e}")
        return ""


def truncate_string(s, max_length=50):
    """截断字符串到指定长度"""
    if not s:
        return ""
    if len(s) <= max_length:
        return s
    return s[:max_length] + "..."


def calculate_air_quality_level(aqi):
    """根据AQI值计算空气质量等级"""
    if aqi is None:
        return "--"
    try:
        aqi_val = int(aqi)
        if aqi_val <= 50:
            return "优"
        elif aqi_val <= 100:
            return "良"
        elif aqi_val <= 150:
            return "轻度污染"
        elif aqi_val <= 200:
            return "中度污染"
        elif aqi_val <= 300:
            return "重度污染"
        else:
            return "严重污染"
    except (ValueError, TypeError):
        return "--"


def calculate_air_quality_color(aqi):
    """根据AQI值计算空气质量颜色"""
    if aqi is None:
        return "#666666"
    try:
        aqi_val = int(aqi)
        if aqi_val <= 50:
            return "#00e400"
        elif aqi_val <= 100:
            return "#ffff00"
        elif aqi_val <= 150:
            return "#ff7e00"
        elif aqi_val <= 200:
            return "#ff0000"
        elif aqi_val <= 300:
            return "#99004c"
        else:
            return "#7e0023"
    except (ValueError, TypeError):
        return "#666666"


def calculate_vibration_level(vibration):
    """根据振动值计算振动等级"""
    if vibration is None:
        return "--"
    try:
        vib_val = float(vibration)
        if vib_val < 5:
            return "正常"
        elif vib_val < 10:
            return "轻微振动"
        elif vib_val < 20:
            return "中度振动"
        else:
            return "严重振动"
    except (ValueError, TypeError):
        return "--"


def calculate_vibration_color(vibration):
    """根据振动值计算振动颜色"""
    if vibration is None:
        return "#666666"
    try:
        vib_val = float(vibration)
        if vib_val < 5:
            return "#00e400"
        elif vib_val < 10:
            return "#ffff00"
        elif vib_val < 20:
            return "#ff7e00"
        else:
            return "#ff0000"
    except (ValueError, TypeError):
        return "#666666"


def round_to_decimal(value, decimal=1):
    """四舍五入到指定小数位"""
    if value is None:
        return "--"
    try:
        return round(float(value), decimal)
    except (ValueError, TypeError):
        return "--"


def clamp_value(value, min_val, max_val):
    """限制值在指定范围内"""
    if value is None:
        return None
    try:
        val = float(value)
        return max(min_val, min(val, max_val))
    except (ValueError, TypeError):
        return None
