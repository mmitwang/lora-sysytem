"""配置管理模块测试"""

import unittest
from app.config import Config


class TestConfig(unittest.TestCase):
    """配置管理模块测试类"""
    
    def test_config_initialization(self):
        """测试配置初始化"""
        # 检查配置类是否正确初始化
        self.assertTrue(hasattr(Config, 'SECRET_KEY'))
        self.assertTrue(hasattr(Config, 'DEBUG'))
        self.assertTrue(hasattr(Config, 'DATABASE_URL'))
        self.assertTrue(hasattr(Config, 'DEFAULT_SERIAL_CONFIG'))
        self.assertTrue(hasattr(Config, 'DEFAULT_QUERY_INTERVAL'))
        self.assertTrue(hasattr(Config, 'MODBUS_SLAVE_ID'))
        self.assertTrue(hasattr(Config, 'TEMPERATURE_RANGE'))
        self.assertTrue(hasattr(Config, 'HUMIDITY_RANGE'))
    
    def test_default_serial_config(self):
        """测试默认串口配置"""
        default_config = Config.DEFAULT_SERIAL_CONFIG
        self.assertIsInstance(default_config, dict)
        self.assertIn('port', default_config)
        self.assertIn('baudrate', default_config)
        self.assertIn('parity', default_config)
        self.assertIn('stopbits', default_config)
        self.assertIn('bytesize', default_config)
        self.assertEqual(default_config['port'], 'COM3')
        self.assertEqual(default_config['baudrate'], 9600)
        self.assertEqual(default_config['parity'], 'N')
        self.assertEqual(default_config['stopbits'], 1)
        self.assertEqual(default_config['bytesize'], 8)
    
    def test_query_interval_config(self):
        """测试问询周期配置"""
        self.assertEqual(Config.DEFAULT_QUERY_INTERVAL, 2)
        self.assertEqual(Config.MIN_QUERY_INTERVAL, 1)
        self.assertEqual(Config.MAX_QUERY_INTERVAL, 60)
    
    def test_modbus_config(self):
        """测试Modbus配置"""
        self.assertEqual(Config.MODBUS_SLAVE_ID, 0x01)
        self.assertEqual(Config.MODBUS_FUNCTION_CODE, 0x03)
        self.assertEqual(Config.MODBUS_START_ADDRESS, 0x0000)
        self.assertEqual(Config.MODBUS_REGISTER_COUNT, 0x0002)
    
    def test_temperature_range(self):
        """测试温度范围配置"""
        self.assertEqual(Config.TEMPERATURE_RANGE, (-40, 85))
    
    def test_humidity_range(self):
        """测试湿度范围配置"""
        self.assertEqual(Config.HUMIDITY_RANGE, (0, 100))
    
    def test_database_config(self):
        """测试数据库配置"""
        self.assertEqual(Config.DATABASE_URL, 'sqlite:///iot_data.db')
        self.assertEqual(Config.DATABASE_FILE, 'iot_data.db')
    
    def test_data_processing_config(self):
        """测试数据处理配置"""
        self.assertEqual(Config.MAX_DATA_POINTS, 1000)
        self.assertEqual(Config.HISTORY_CHART_POINTS, 200)


if __name__ == '__main__':
    unittest.main()
