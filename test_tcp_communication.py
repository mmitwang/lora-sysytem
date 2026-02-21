#!/usr/bin/env python3
"""
测试TCP通讯功能
"""

import requests
import time

# 打开TCP通讯
def open_tcp_communication():
    print("打开TCP通讯...")
    url = "http://localhost:5000/api/serial/open-tcp"
    data = {
        "tcp_server_ip": "127.0.0.1",
        "tcp_server_port": 10125,
        "page": "light"
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        print(f"打开TCP通讯响应: {result}")
        return result
    except Exception as e:
        print(f"打开TCP通讯失败: {e}")
        return None

# 启动问询
def start_query():
    print("\n启动问询...")
    url = "http://localhost:5000/api/query/start"
    data = {
        "page": "light"
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        print(f"启动问询响应: {result}")
        return result
    except Exception as e:
        print(f"启动问询失败: {e}")
        return None

# 检查系统状态
def check_status():
    print("\n检查系统状态...")
    url = "http://localhost:5000/api/serial/status?page=light"
    
    try:
        response = requests.get(url)
        result = response.json()
        print(f"系统状态: {result}")
        print(f"通讯模式: {result.get('communication_mode')}")
        print(f"网络类型: {result.get('network_type')}")
        print(f"目标地址: {result.get('target_address')}")
        print(f"问询运行状态: {result.get('query_running')}")
    except Exception as e:
        print(f"检查系统状态失败: {e}")

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
    print("测试TCP通讯功能")
    print("=====================================")
    
    # 1. 打开TCP通讯
    open_result = open_tcp_communication()
    if not open_result or open_result.get("status") != "success":
        print("打开TCP通讯失败，退出测试")
        return
    
    # 2. 启动问询
    start_result = start_query()
    if not start_result or start_result.get("status") != "success":
        print("启动问询失败，退出测试")
        return
    
    # 3. 检查系统状态
    check_status()
    
    # 4. 等待几秒钟让数据更新
    print("\n等待5秒钟让数据更新...")
    time.sleep(5)
    
    # 5. 测试获取传感器数据
    sensor_data = test_sensor_data()
    if sensor_data:
        print("\n传感器数据测试成功!")
    
    # 6. 测试获取帧数据
    frame_data = test_frame_data()
    if frame_data:
        print("\n帧数据测试成功!")
    
    print("\n=====================================")
    print("测试完成")
    print("=====================================")

if __name__ == "__main__":
    main()
