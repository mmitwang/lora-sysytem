"""工具函数模块测试"""

import unittest
import time
import datetime
from app.helpers import (
    format_timestamp,
    format_datetime,
    get_current_timestamp,
    get_current_datetime,
    get_current_time_str,
    calculate_time_diff,
    calculate_time_diff_str,
    validate_temperature,
    validate_humidity,
    validate_query_interval,
    format_bytes_to_hex,
    parse_hex_string,
    safe_json_loads,
    safe_json_dumps,
    truncate_string,
    calculate_air_quality_level,
    calculate_air_quality_color,
    calculate_vibration_level,
    calculate_vibration_color,
    round_to_decimal,
    clamp_value
)


class TestHelpers(unittest.TestCase):
    """工具函数模块测试类"""
    
    def test_format_timestamp(self):
        """测试时间戳格式化"""
        # 测试有效的时间戳
        timestamp = 1620000000  # 2021-05-03 08:00:00
        formatted = format_timestamp(timestamp)
        self.assertEqual(formatted, "2021-05-03 08:00:00")
        
        # 测试无效的时间戳
        self.assertEqual(format_timestamp(None), "--")
        self.assertEqual(format_timestamp("invalid"), "--")
    
    def test_format_datetime(self):
        """测试日期时间对象格式化"""
        # 测试有效的日期时间对象
        dt = datetime.datetime(2021, 5, 3, 8, 0, 0)
        formatted = format_datetime(dt)
        self.assertEqual(formatted, "2021-05-03 08:00:00")
        
        # 测试无效的日期时间对象
        self.assertEqual(format_datetime(None), "--")
    
    def test_get_current_timestamp(self):
        """测试获取当前时间戳"""
        timestamp = get_current_timestamp()
        self.assertIsInstance(timestamp, float)
        self.assertTrue(timestamp > 0)
    
    def test_get_current_datetime(self):
        """测试获取当前日期时间对象"""
        dt = get_current_datetime()
        self.assertIsInstance(dt, datetime.datetime)
    
    def test_get_current_time_str(self):
        """测试获取当前时间字符串"""
        time_str = get_current_time_str()
        self.assertIsInstance(time_str, str)
        self.assertTrue(len(time_str) > 0)
    
    def test_calculate_time_diff(self):
        """测试计算时间差"""
        start_time = time.time()
        time.sleep(0.1)  # 等待0.1秒
        diff = calculate_time_diff(start_time)
        self.assertIsInstance(diff, float)
        self.assertTrue(0.05 < diff < 0.15)  # 允许一定的误差
        
        # 测试指定结束时间
        end_time = start_time + 1.0
        diff = calculate_time_diff(start_time, end_time)
        self.assertAlmostEqual(diff, 1.0)
    
    def test_calculate_time_diff_str(self):
        """测试计算时间差并返回可读字符串"""
        # 测试秒级时间差
        start_time = time.time() - 30
        diff_str = calculate_time_diff_str(start_time, start_time + 30)
        self.assertEqual(diff_str, "30秒")
        
        # 测试分钟级时间差
        start_time = time.time() - 90
        diff_str = calculate_time_diff_str(start_time, start_time + 90)
        self.assertEqual(diff_str, "1分30秒")
        
        # 测试小时级时间差
        start_time = time.time() - 3660
        diff_str = calculate_time_diff_str(start_time, start_time + 3660)
        self.assertEqual(diff_str, "1小时1分")
        
        # 测试天级时间差
        start_time = time.time() - 90000
        diff_str = calculate_time_diff_str(start_time, start_time + 90000)
        self.assertEqual(diff_str, "1天1小时")
    
    def test_validate_temperature(self):
        """测试温度值验证"""
        # 测试有效的温度值
        self.assertTrue(validate_temperature(25.5))
        self.assertTrue(validate_temperature(0))
        self.assertTrue(validate_temperature(-40))
        self.assertTrue(validate_temperature(85))
        
        # 测试无效的温度值
        self.assertFalse(validate_temperature(None))
        self.assertFalse(validate_temperature("invalid"))
        self.assertFalse(validate_temperature(-41))  # 低于最低值
        self.assertFalse(validate_temperature(86))   # 高于最高值
    
    def test_validate_humidity(self):
        """测试湿度值验证"""
        # 测试有效的湿度值
        self.assertTrue(validate_humidity(50.0))
        self.assertTrue(validate_humidity(0))
        self.assertTrue(validate_humidity(100))
        
        # 测试无效的湿度值
        self.assertFalse(validate_humidity(None))
        self.assertFalse(validate_humidity("invalid"))
        self.assertFalse(validate_humidity(-1))   # 低于最低值
        self.assertFalse(validate_humidity(101))  # 高于最高值
    
    def test_validate_query_interval(self):
        """测试问询周期验证"""
        # 测试有效的问询周期
        self.assertTrue(validate_query_interval(1))
        self.assertTrue(validate_query_interval(2))
        self.assertTrue(validate_query_interval(60))
        
        # 测试无效的问询周期
        self.assertFalse(validate_query_interval(None))
        self.assertFalse(validate_query_interval("invalid"))
        self.assertFalse(validate_query_interval(0.5))  # 低于最小值
        self.assertFalse(validate_query_interval(61))   # 高于最大值
    
    def test_format_bytes_to_hex(self):
        """测试字节数据格式化"""
        # 测试有效的字节数据
        bytes_data = b'\x01\x03\x00\x00\x00\x02'
        hex_str = format_bytes_to_hex(bytes_data)
        self.assertEqual(hex_str, "01 03 00 00 00 02")
        
        # 测试无效的字节数据
        self.assertEqual(format_bytes_to_hex(None), "")
        self.assertEqual(format_bytes_to_hex(b''), "")
    
    def test_parse_hex_string(self):
        """测试十六进制字符串解析"""
        # 测试有效的十六进制字符串
        hex_str = "01 03 00 00 00 02"
        bytes_data = parse_hex_string(hex_str)
        self.assertEqual(bytes_data, b'\x01\x03\x00\x00\x00\x02')
        
        # 测试不带空格的十六进制字符串
        hex_str = "010300000002"
        bytes_data = parse_hex_string(hex_str)
        self.assertEqual(bytes_data, b'\x01\x03\x00\x00\x00\x02')
        
        # 测试长度为奇数的十六进制字符串
        hex_str = "0103000002"
        bytes_data = parse_hex_string(hex_str)
        self.assertEqual(bytes_data, b'\x01\x03\x00\x00\x02')
        
        # 测试无效的十六进制字符串
        self.assertEqual(parse_hex_string(None), b'')
        self.assertEqual(parse_hex_string(""), b'')
    
    def test_safe_json_loads(self):
        """测试安全地解析JSON字符串"""
        # 测试有效的JSON字符串
        json_str = '{"temperature": 25.5, "humidity": 60.0}'
        data = safe_json_loads(json_str)
        self.assertIsInstance(data, dict)
        self.assertEqual(data['temperature'], 25.5)
        self.assertEqual(data['humidity'], 60.0)
        
        # 测试无效的JSON字符串
        json_str = '{"temperature": 25.5, "humidity": 60.0}'  # 有效的
        data = safe_json_loads(json_str, {})
        self.assertIsInstance(data, dict)
        
        json_str = '{invalid json}'  # 无效的
        data = safe_json_loads(json_str, {"default": "value"})
        self.assertEqual(data, {"default": "value"})
        
        # 测试空字符串
        self.assertEqual(safe_json_loads(""), None)
        self.assertEqual(safe_json_loads("", "default"), "default")
    
    def test_safe_json_dumps(self):
        """测试安全地序列化对象为JSON字符串"""
        # 测试有效的对象
        data = {"temperature": 25.5, "humidity": 60.0}
        json_str = safe_json_dumps(data)
        self.assertIsInstance(json_str, str)
        self.assertTrue('"temperature": 25.5' in json_str)
        self.assertTrue('"humidity": 60.0' in json_str)
        
        # 测试包含非序列化对象的情况
        class TestClass:
            pass
        
        data = {"object": TestClass()}
        json_str = safe_json_dumps(data)
        self.assertEqual(json_str, "")
    
    def test_truncate_string(self):
        """测试截断字符串"""
        # 测试不需要截断的字符串
        s = "hello"
        truncated = truncate_string(s, 10)
        self.assertEqual(truncated, s)
        
        # 测试需要截断的字符串
        s = "Hello, World! This is a long string."
        truncated = truncate_string(s, 20)
        self.assertEqual(truncated, "Hello, World! This i...")
        
        # 测试空字符串
        self.assertEqual(truncate_string(""), "")
        self.assertEqual(truncate_string(None), "")
    
    def test_calculate_air_quality_level(self):
        """测试根据AQI值计算空气质量等级"""
        # 测试各等级的AQI值
        self.assertEqual(calculate_air_quality_level(25), "优")
        self.assertEqual(calculate_air_quality_level(75), "良")
        self.assertEqual(calculate_air_quality_level(125), "轻度污染")
        self.assertEqual(calculate_air_quality_level(175), "中度污染")
        self.assertEqual(calculate_air_quality_level(250), "重度污染")
        self.assertEqual(calculate_air_quality_level(350), "严重污染")
        
        # 测试无效的AQI值
        self.assertEqual(calculate_air_quality_level(None), "--")
        self.assertEqual(calculate_air_quality_level("invalid"), "--")
    
    def test_calculate_air_quality_color(self):
        """测试根据AQI值计算空气质量颜色"""
        # 测试各等级的AQI值对应的颜色
        self.assertEqual(calculate_air_quality_color(25), "#00e400")  # 优
        self.assertEqual(calculate_air_quality_color(75), "#ffff00")  # 良
        self.assertEqual(calculate_air_quality_color(125), "#ff7e00")  # 轻度污染
        self.assertEqual(calculate_air_quality_color(175), "#ff0000")  # 中度污染
        self.assertEqual(calculate_air_quality_color(250), "#99004c")  # 重度污染
        self.assertEqual(calculate_air_quality_color(350), "#7e0023")  # 严重污染
        
        # 测试无效的AQI值
        self.assertEqual(calculate_air_quality_color(None), "#666666")
        self.assertEqual(calculate_air_quality_color("invalid"), "#666666")
    
    def test_calculate_vibration_level(self):
        """测试根据振动值计算振动等级"""
        # 测试各等级的振动值
        self.assertEqual(calculate_vibration_level(2), "正常")
        self.assertEqual(calculate_vibration_level(7), "轻微振动")
        self.assertEqual(calculate_vibration_level(15), "中度振动")
        self.assertEqual(calculate_vibration_level(25), "严重振动")
        
        # 测试无效的振动值
        self.assertEqual(calculate_vibration_level(None), "--")
        self.assertEqual(calculate_vibration_level("invalid"), "--")
    
    def test_calculate_vibration_color(self):
        """测试根据振动值计算振动颜色"""
        # 测试各等级的振动值对应的颜色
        self.assertEqual(calculate_vibration_color(2), "#00e400")  # 正常
        self.assertEqual(calculate_vibration_color(7), "#ffff00")  # 轻微振动
        self.assertEqual(calculate_vibration_color(15), "#ff7e00")  # 中度振动
        self.assertEqual(calculate_vibration_color(25), "#ff0000")  # 严重振动
        
        # 测试无效的振动值
        self.assertEqual(calculate_vibration_color(None), "#666666")
        self.assertEqual(calculate_vibration_color("invalid"), "#666666")
    
    def test_round_to_decimal(self):
        """测试四舍五入到指定小数位"""
        # 测试正常情况
        self.assertEqual(round_to_decimal(25.123), 25.1)
        self.assertEqual(round_to_decimal(25.123, 2), 25.12)
        self.assertEqual(round_to_decimal(25.126, 2), 25.13)
        
        # 测试无效值
        self.assertEqual(round_to_decimal(None), "--")
        self.assertEqual(round_to_decimal("invalid"), "--")
    
    def test_clamp_value(self):
        """测试限制值在指定范围内"""
        # 测试在范围内的值
        self.assertEqual(clamp_value(5, 0, 10), 5)
        
        # 测试低于最小值的值
        self.assertEqual(clamp_value(-5, 0, 10), 0)
        
        # 测试高于最大值的值
        self.assertEqual(clamp_value(15, 0, 10), 10)
        
        # 测试无效值
        self.assertEqual(clamp_value(None, 0, 10), None)
        self.assertEqual(clamp_value("invalid", 0, 10), None)


if __name__ == '__main__':
    unittest.main()
