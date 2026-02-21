#!/usr/bin/env python3
"""
测试主系统的TCP通信API
"""

import requests
import time

# 测试更新通讯配置为TCP模式
def test_update_communication_config():
    print("测试更新通讯配置为TCP模式...")
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
        return result.get("status") == "success"
    except Exception as e:
        print(f"更新通讯配置失败: {e}")
        return False

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
        return result.get("status") == "success"
    except Exception as e:
        print(f"打开TCP通讯失败: {e}")
        return False

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
        return result.get("status") == "success"
    except Exception as e:
        print(f"启动问询失败: {e}")
        return False

# 测试获取传感器数据
def test_get_sensor_data():
    print("\n测试获取传感器数据...")
    url = "http://localhost:5000/api/sensor/data?page=light"
    
    try:
        response = requests.get(url)
        result = response.json()
        print(f"获取传感器数据响应: {result}")
        return True
    except Exception as e:
        print(f"获取传感器数据失败: {e}")
        return False

# 测试获取帧数据
def test_get_frame_data():
    print("\n测试获取帧数据...")
    url = "http://localhost:5000/api/serial/frames?page=light"
    
    try:
        response = requests.get(url)
        result = response.json()
        print(f"获取帧数据响应: {result}")
        return True
    except Exception as e:
        print(f"获取帧数据失败: {e}")
        return False

# 测试停止问询
def test_stop_query():
    print("\n测试停止问询...")
    url = "http://localhost:5000/api/query/stop"
    data = {
        "page": "light"
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        print(f"停止问询响应: {result}")
        return result.get("status") == "success"
    except Exception as e:
        print(f"停止问询失败: {e}")
        return False

# 主函数
def main():
    print("=====================================")
    print("测试主系统的TCP通信API")
    print("=====================================")
    
    # 1. 更新通讯配置为TCP模式
    if not test_update_communication_config():
        print("更新通讯配置失败，退出测试")
        return
    
    # 2. 打开TCP通讯
    if not test_open_tcp():
        print("打开TCP通讯失败，退出测试")
        return
    
    # 3. 启动问询
    if not test_start_query():
        print("启动问询失败，退出测试")
        return
    
    # 4. 等待几秒钟让数据更新
    print("\n等待5秒钟让数据更新...")
    time.sleep(5)
    
    # 5. 测试获取传感器数据
    test_get_sensor_data()
    
    # 6. 测试获取帧数据
    test_get_frame_data()
    
    # 7. 测试停止问询
    test_stop_query()
    
    print("\n=====================================")
    print("测试完成")
    print("=====================================")

if __name__ == "__main__":
    main()
