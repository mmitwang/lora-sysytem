"""数据库服务模块"""

import sqlite3
import os
from app.config import Config


def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(Config.DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库，创建必要的表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 创建历史数据表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            timestamp INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建温振监控数据表（支持频率、振幅、速度、加速度）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vibration_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL NOT NULL,
            frequency_x REAL,
            frequency_y REAL,
            frequency_z REAL,
            velocity_x REAL,
            velocity_y REAL,
            velocity_z REAL,
            acceleration_x REAL,
            acceleration_y REAL,
            acceleration_z REAL,
            amplitude_peak REAL,
            amplitude_rms REAL,
            timestamp INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建空气质量监控数据表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS air_quality_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aqi INTEGER NOT NULL,
            pm25 REAL NOT NULL,
            pm10 REAL NOT NULL,
            co2 REAL NOT NULL,
            voc REAL NOT NULL,
            timestamp INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建配置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL
        )
    ''')
    
    # 插入默认配置
    default_configs = [
        ('query_interval', str(Config.DEFAULT_QUERY_INTERVAL)),
        ('serial_port', Config.DEFAULT_SERIAL_CONFIG['port']),
        ('baudrate', str(Config.DEFAULT_SERIAL_CONFIG['baudrate'])),
        ('parity', Config.DEFAULT_SERIAL_CONFIG['parity']),
        ('stopbits', str(Config.DEFAULT_SERIAL_CONFIG['stopbits'])),
        ('bytesize', str(Config.DEFAULT_SERIAL_CONFIG['bytesize']))
    ]
    
    for key, value in default_configs:
        cursor.execute('''
            INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)
        ''', (key, value))
    
    conn.commit()
    conn.close()


def save_sensor_data(temperature, humidity, timestamp):
    """保存传感器数据到数据库"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO sensor_history (temperature, humidity, timestamp)
        VALUES (?, ?, ?)
    ''', (temperature, humidity, timestamp))
    
    conn.commit()
    conn.close()


def save_vibration_data(temperature, timestamp, frequency_x=None, frequency_y=None, frequency_z=None, velocity_x=None, velocity_y=None, velocity_z=None, acceleration_x=None, acceleration_y=None, acceleration_z=None, amplitude_peak=None, amplitude_rms=None):
    """保存温振数据到数据库"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO vibration_history (
            temperature, frequency_x, frequency_y, frequency_z, 
            velocity_x, velocity_y, velocity_z, 
            acceleration_x, acceleration_y, acceleration_z, 
            amplitude_peak, amplitude_rms, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        temperature, frequency_x, frequency_y, frequency_z, 
        velocity_x, velocity_y, velocity_z, 
        acceleration_x, acceleration_y, acceleration_z, 
        amplitude_peak, amplitude_rms, timestamp
    ))
    
    conn.commit()
    conn.close()


def save_air_quality_data(aqi, pm25, pm10, co2, voc, timestamp):
    """保存空气质量数据到数据库"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO air_quality_history (aqi, pm25, pm10, co2, voc, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (aqi, pm25, pm10, co2, voc, timestamp))
    
    conn.commit()
    conn.close()


def get_history_data(start_time, end_time, table='sensor_history'):
    """获取指定时间范围内的历史数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if table == 'sensor_history':
        cursor.execute('''
            SELECT temperature, humidity, timestamp
            FROM sensor_history
            WHERE timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp ASC
        ''', (start_time, end_time))
        
        data = cursor.fetchall()
        conn.close()
        
        return [{
            "temperature": row[0],
            "humidity": row[1],
            "timestamp": row[2]
        } for row in data]
    
    elif table == 'vibration_history':
        cursor.execute('''
            SELECT 
                temperature, frequency_x, frequency_y, frequency_z, 
                velocity_x, velocity_y, velocity_z, 
                acceleration_x, acceleration_y, acceleration_z, 
                amplitude_peak, amplitude_rms, timestamp
            FROM vibration_history
            WHERE timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp ASC
        ''', (start_time, end_time))
        
        data = cursor.fetchall()
        conn.close()
        
        return [{
            "temperature": row[0],
            "frequency_x": row[1],
            "frequency_y": row[2],
            "frequency_z": row[3],
            "velocity_x": row[4],
            "velocity_y": row[5],
            "velocity_z": row[6],
            "acceleration_x": row[7],
            "acceleration_y": row[8],
            "acceleration_z": row[9],
            "amplitude_peak": row[10],
            "amplitude_rms": row[11],
            "timestamp": row[12]
        } for row in data]
    
    elif table == 'air_quality_history':
        cursor.execute('''
            SELECT aqi, pm25, pm10, co2, voc, timestamp
            FROM air_quality_history
            WHERE timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp ASC
        ''', (start_time, end_time))
        
        data = cursor.fetchall()
        conn.close()
        
        return [{
            "aqi": row[0],
            "pm25": row[1],
            "pm10": row[2],
            "co2": row[3],
            "voc": row[4],
            "timestamp": row[5]
        } for row in data]
    
    conn.close()
    return []


def get_config(key, default=None):
    """获取配置值"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT value FROM config WHERE key = ?
    ''', (key,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return result[0]
    return default


def set_config(key, value):
    """设置配置值"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)
    ''', (key, value))
    
    conn.commit()
    conn.close()


def get_latest_sensor_data():
    """获取最新的传感器数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT temperature, humidity, timestamp
        FROM sensor_history
        ORDER BY timestamp DESC
        LIMIT 1
    ''')
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            "temperature": result[0],
            "humidity": result[1],
            "timestamp": result[2]
        }
    return None


def get_latest_vibration_data():
    """获取最新的温振数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            temperature, frequency_x, frequency_y, frequency_z, 
            velocity_x, velocity_y, velocity_z, 
            acceleration_x, acceleration_y, acceleration_z, 
            amplitude_peak, amplitude_rms, timestamp
        FROM vibration_history
        ORDER BY timestamp DESC
        LIMIT 1
    ''')
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            "temperature": result[0],
            "frequency_x": result[1],
            "frequency_y": result[2],
            "frequency_z": result[3],
            "velocity_x": result[4],
            "velocity_y": result[5],
            "velocity_z": result[6],
            "acceleration_x": result[7],
            "acceleration_y": result[8],
            "acceleration_z": result[9],
            "amplitude_peak": result[10],
            "amplitude_rms": result[11],
            "timestamp": result[12]
        }
    return None


def get_latest_air_quality_data():
    """获取最新的空气质量数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT aqi, pm25, pm10, co2, voc, timestamp
        FROM air_quality_history
        ORDER BY timestamp DESC
        LIMIT 1
    ''')
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            "aqi": result[0],
            "pm25": result[1],
            "pm10": result[2],
            "co2": result[3],
            "voc": result[4],
            "timestamp": result[5]
        }
    return None
