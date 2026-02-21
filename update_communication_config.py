#!/usr/bin/env python3
"""
更新通讯配置为TCP模式
"""

import requests

# 更新通讯配置为TCP模式
def update_to_tcp_mode():
    print("更新通讯配置为TCP模式...")
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
        
        # 检查更新是否成功
        if result.get("status") == "success":
            print("通讯配置更新成功!")
            # 验证更新后的状态
            check_status()
        else:
            print("通讯配置更新失败!")
    except Exception as e:
        print(f"更新通讯配置失败: {e}")

# 检查系统状态
def check_status():
    print("\n验证系统状态...")
    url = "http://localhost:5000/api/serial/status?page=light"
    
    try:
        response = requests.get(url)
        result = response.json()
        print(f"系统状态: {result}")
        print(f"通讯模式: {result.get('communication_mode')}")
        print(f"网络类型: {result.get('network_type')}")
        print(f"目标地址: {result.get('target_address')}")
        print(f"TCP服务器IP: {result.get('tcp_server_ip')}")
        print(f"TCP服务器端口: {result.get('tcp_server_port')}")
    except Exception as e:
        print(f"检查系统状态失败: {e}")

# 主函数
def main():
    print("=====================================")
    print("更新通讯配置为TCP模式")
    print("=====================================")
    update_to_tcp_mode()
    print("=====================================")

if __name__ == "__main__":
    main()
