"""数据库服务模块测试"""

import unittest
import os
import tempfile
import time
from app.database import (
    get_db_connection,
    init_db,
    save_sensor_data,
    save_vibration_data,
    save_air_quality_data,
    get_history_data,
    get_config,
    set_config,
    get_latest_sensor_data,
    get_latest_vibration_data,
    get_latest_air_quality_data
)
from app.config import Config


class TestDatabase(unittest.TestCase):
    """数据库服务模块测试类"""
    
    def setUp(self):
        """测试前的设置"""
        # 创建临时数据库文件
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.original_db_file = Config.DATABASE_FILE
        Config.DATABASE_FILE = self.temp_db.name
        
        # 初始化数据库
        init_db()
    
    def tearDown(self):
        """测试后的清理"""
        # 恢复原始数据库文件路径
        Config.DATABASE_FILE = self.original_db_file
        
        # 尝试删除临时数据库文件（添加异常处理）
        try:
            if os.path.exists(self.temp_db.name):
                # 确保所有连接都已关闭
                import gc
                gc.collect()  # 强制垃圾回收，确保所有连接对象被销毁
                time.sleep(0.1)  # 短暂延迟，确保文件锁释放
                os.unlink(self.temp_db.name)
        except Exception as e:
            print(f"删除临时数据库文件失败: {e}")
            # 即使删除失败也继续执行，不影响测试结果
    
    def test_get_db_connection(self):
        """测试获取数据库连接"""
        conn = get_db_connection()
        self.assertIsNotNone(conn)
        conn.close()
    
    def test_init_db(self):
        """测试初始化数据库"""
        # 再次初始化数据库，测试幂等性
        init_db()
        # 检查数据库连接是否正常
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sensor_history'")
        self.assertIsNotNone(cursor.fetchone())
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vibration_history'")
        self.assertIsNotNone(cursor.fetchone())
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='air_quality_history'")
        self.assertIsNotNone(cursor.fetchone())
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='config'")
        self.assertIsNotNone(cursor.fetchone())
        
        conn.close()
    
    def test_save_sensor_data(self):
        """测试保存传感器数据"""
        timestamp = 1620000000
        temperature = 25.5
        humidity = 60.0
        
        save_sensor_data(temperature, humidity, timestamp)
        
        # 验证数据是否保存成功
        data = get_history_data(timestamp - 1, timestamp + 1, 'sensor_history')
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['temperature'], temperature)
        self.assertEqual(data[0]['humidity'], humidity)
        self.assertEqual(data[0]['timestamp'], timestamp)
    
    def test_save_vibration_data(self):
        """测试保存温振数据"""
        timestamp = 1620000000
        temperature = 35.5
        frequency_x = 50.0
        velocity_x = 10.0
        acceleration_x = 1.0

        save_vibration_data(temperature, timestamp, frequency_x=frequency_x, velocity_x=velocity_x, acceleration_x=acceleration_x)

        # 验证数据是否保存成功
        data = get_history_data(timestamp - 1, timestamp + 1, 'vibration_history')
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['temperature'], temperature)
        self.assertEqual(data[0]['frequency_x'], frequency_x)
        self.assertEqual(data[0]['velocity_x'], velocity_x)
        self.assertEqual(data[0]['acceleration_x'], acceleration_x)
        self.assertEqual(data[0]['timestamp'], timestamp)
    
    def test_save_air_quality_data(self):
        """测试保存空气质量数据"""
        timestamp = 1620000000
        aqi = 75
        pm25 = 25.5
        pm10 = 45.0
        co2 = 650.0
        voc = 35.0
        
        save_air_quality_data(aqi, pm25, pm10, co2, voc, timestamp)
        
        # 验证数据是否保存成功
        data = get_history_data(timestamp - 1, timestamp + 1, 'air_quality_history')
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['aqi'], aqi)
        self.assertEqual(data[0]['pm25'], pm25)
        self.assertEqual(data[0]['pm10'], pm10)
        self.assertEqual(data[0]['co2'], co2)
        self.assertEqual(data[0]['voc'], voc)
        self.assertEqual(data[0]['timestamp'], timestamp)
    
    def test_get_config(self):
        """测试获取配置"""
        # 测试获取默认配置
        query_interval = get_config('query_interval')
        self.assertEqual(query_interval, '2')
        
        # 测试获取不存在的配置
        non_existent = get_config('non_existent_key', 'default_value')
        self.assertEqual(non_existent, 'default_value')
    
    def test_set_config(self):
        """测试设置配置"""
        # 设置新配置
        set_config('test_key', 'test_value')
        
        # 验证配置是否设置成功
        value = get_config('test_key')
        self.assertEqual(value, 'test_value')
        
        # 更新配置
        set_config('test_key', 'updated_value')
        value = get_config('test_key')
        self.assertEqual(value, 'updated_value')
    
    def test_get_latest_sensor_data(self):
        """测试获取最新的传感器数据"""
        # 保存多条数据
        save_sensor_data(20.0, 50.0, 1620000000)
        save_sensor_data(25.5, 60.0, 1620000001)  # 最新数据
        
        # 获取最新数据
        latest = get_latest_sensor_data()
        self.assertIsNotNone(latest)
        self.assertEqual(latest['temperature'], 25.5)
        self.assertEqual(latest['humidity'], 60.0)
        self.assertEqual(latest['timestamp'], 1620000001)
    
    def test_get_latest_vibration_data(self):
        """测试获取最新的温振数据"""
        # 保存多条数据
        save_vibration_data(30.0, 1620000000, frequency_x=45.0, velocity_x=8.0)
        save_vibration_data(35.5, 1620000001, frequency_x=50.0, velocity_x=10.0)  # 最新数据

        # 获取最新数据
        latest = get_latest_vibration_data()
        self.assertIsNotNone(latest)
        self.assertEqual(latest['temperature'], 35.5)
        self.assertEqual(latest['frequency_x'], 50.0)
        self.assertEqual(latest['velocity_x'], 10.0)
        self.assertEqual(latest['timestamp'], 1620000001)
    
    def test_get_latest_air_quality_data(self):
        """测试获取最新的空气质量数据"""
        # 保存多条数据
        save_air_quality_data(50, 15.0, 30.0, 500.0, 25.0, 1620000000)
        save_air_quality_data(75, 25.5, 45.0, 650.0, 35.0, 1620000001)  # 最新数据
        
        # 获取最新数据
        latest = get_latest_air_quality_data()
        self.assertIsNotNone(latest)
        self.assertEqual(latest['aqi'], 75)
        self.assertEqual(latest['pm25'], 25.5)
        self.assertEqual(latest['pm10'], 45.0)
        self.assertEqual(latest['co2'], 650.0)
        self.assertEqual(latest['voc'], 35.0)
        self.assertEqual(latest['timestamp'], 1620000001)
    
    def test_get_history_data_with_time_range(self):
        """测试根据时间范围获取历史数据"""
        # 保存测试数据
        save_sensor_data(20.0, 50.0, 1620000000)
        save_sensor_data(22.5, 55.0, 1620000001)
        save_sensor_data(25.0, 60.0, 1620000002)
        
        # 获取时间范围内的数据
        data = get_history_data(1620000000, 1620000001, 'sensor_history')
        self.assertEqual(len(data), 2)
        
        # 获取超出时间范围的数据
        data = get_history_data(1620000003, 1620000004, 'sensor_history')
        self.assertEqual(len(data), 0)


if __name__ == '__main__':
    unittest.main()
