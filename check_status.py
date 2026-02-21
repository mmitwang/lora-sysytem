#!/usr/bin/env python3
"""
检查系统状态并测试TCP通信功能
"""

import requests
import time

# 检查系统状态
def check_status():
    print("检查系统状态...")
    url = "http://localhost:5000/api/serial/status?page=light"
    
    try:
        response = requests.get(url)
        result = response.json()
        print(f"系统状态: {result}")
        return result
    except Exception as e:
        print(f"检查系统状态失败: {e}")
        return None

# 测试获取传感器数据
def test_sensor_data():
    print("\n测试获取传感器数据...")
    url = "http://localhost:5000/api/sensor/data?page=light"
    
    try:
        response = requests.get(url)
        result = response.json()
        print(f"传感器数据: {result}")
        return result
    except Exception as e:
        print(f"获取传感器数据失败: {e}")
        return None

# 测试获取帧数据
def test_frame_data():
    print("\n测试获取帧数据...")
    url = "http://localhost:5000/api/serial/frames?page=light"
    
    try:
        response = requests.get(url)
        result = response.json()
        print(f"帧数据: {result}")
        return result
    except Exception as e:
        print(f"获取帧数据失败: {e}")
        return None

# 主函数
def main():
    print("=====================================")
    print("检查系统状态并测试TCP通信")
    print("=====================================")
    
    # 检查系统状态
    status = check_status()
    
    # 等待几秒钟让数据更新
    print("\n等待3秒钟让数据更新...")
    time.sleep(3)
    
    # 测试获取传感器数据
    sensor_data = test_sensor_data()
    
    # 测试获取帧数据
    frame_data = test_frame_data()
    
    print("\n=====================================")
    print("检查完成")
    print("=====================================")

if __name__ == "__main__":
    main()
