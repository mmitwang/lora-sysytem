#!/usr/bin/env python3
"""
测试TCP+LoRa通信功能的脚本
"""

import requests
import json

# 测试更新通讯配置
def test_update_communication_config():
    print("测试更新通讯配置...")
    url = "http://localhost:5000/api/serial/communication-config"
    data = {
        "communication_mode": "tcp",
        "network_type": "lora",
        "target_address": "5678",
        "config": {
            "tcp_server_ip": "127.0.0.1",
            "tcp_server_port": 10125
        },
        "page": "light"
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        print(f"更新通讯配置响应: {result}")
        return result
    except Exception as e:
        print(f"更新通讯配置失败: {e}")
        return None

# 测试打开TCP通讯
def test_open_tcp():
    print("\n测试打开TCP通讯...")
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

# 测试启动问询
def test_start_query():
    print("\n测试启动问询...")
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

# 测试获取传感器数据
def test_get_sensor_data():
    print("\n测试获取传感器数据...")
    url = "http://localhost:5000/api/sensor/data?page=light"
    
    try:
        response = requests.get(url)
        result = response.json()
        print(f"获取传感器数据响应: {result}")
        return result
    except Exception as e:
        print(f"获取传感器数据失败: {e}")
        return None

# 测试获取帧数据
def test_get_frame_data():
    print("\n测试获取帧数据...")
    url = "http://localhost:5000/api/serial/frames?page=light"
    
    try:
        response = requests.get(url)
        result = response.json()
        print(f"获取帧数据响应: {result}")
        return result
    except Exception as e:
        print(f"获取帧数据失败: {e}")
        return None

# 主函数
def main():
    print("=====================================")
    print("测试TCP+LoRa通信功能")
    print("=====================================")
    
    # 1. 更新通讯配置
    config_result = test_update_communication_config()
    if not config_result or config_result.get("status") != "success":
        print("更新通讯配置失败，退出测试")
        return
    
    # 2. 打开TCP通讯
    open_result = test_open_tcp()
    if not open_result or open_result.get("status") != "success":
        print("打开TCP通讯失败，退出测试")
        return
    
    # 3. 启动问询
    start_result = test_start_query()
    if not start_result or start_result.get("status") != "success":
        print("启动问询失败，退出测试")
        return
    
    # 4. 获取传感器数据
    sensor_data = test_get_sensor_data()
    if sensor_data:
        print("\n传感器数据测试成功!")
    
    # 5. 获取帧数据
    frame_data = test_get_frame_data()
    if frame_data:
        print("\n帧数据测试成功!")
    
    print("\n=====================================")
    print("测试完成")
    print("=====================================")

if __name__ == "__main__":
    main()
