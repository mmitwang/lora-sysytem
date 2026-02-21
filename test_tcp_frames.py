#!/usr/bin/env python3
# 测试TCP模式下的帧数据获取功能

import requests
import time

# 测试步骤：
# 1. 设置通讯模式为TCP
# 2. 打开TCP通讯
# 3. 启动问询
# 4. 获取帧数据
# 5. 打印帧数据

def test_tcp_frames():
    print("开始测试TCP模式下的帧数据获取功能...")
    
    # 1. 设置通讯模式为TCP
    print("\n1. 设置通讯模式为TCP")
    response = requests.post('http://localhost:5000/api/serial/communication-config', json={
        'communication_mode': 'tcp',
        'network_type': 'lora',
        'target_address': '5678',
        'config': {
            'tcp_server_ip': '127.0.0.1',
            'tcp_server_port': 10125
        },
        'page': 'light'
    })
    print(f"设置通讯模式响应: {response.status_code}")
    print(f"设置通讯模式结果: {response.json()}")
    
    # 2. 打开TCP通讯
    print("\n2. 打开TCP通讯")
    response = requests.post('http://localhost:5000/api/serial/open-tcp', json={
        'tcp_server_ip': '127.0.0.1',
        'tcp_server_port': 10125,
        'page': 'light'
    })
    print(f"打开TCP通讯响应: {response.status_code}")
    print(f"打开TCP通讯结果: {response.json()}")
    
    # 3. 启动问询
    print("\n3. 启动问询")
    response = requests.post('http://localhost:5000/api/query/start', json={
        'page': 'light'
    })
    print(f"启动问询响应: {response.status_code}")
    print(f"启动问询结果: {response.json()}")
    
    # 等待一段时间，让问询执行
    print("\n4. 等待问询执行...")
    time.sleep(3)
    
    # 5. 获取帧数据
    print("\n5. 获取帧数据")
    response = requests.get('http://localhost:5000/api/serial/frames?page=light')
    print(f"获取帧数据响应: {response.status_code}")
    frame_data = response.json()
    print(f"获取到的帧数据: {frame_data}")
    
    # 打印详细的帧数据
    print("\n6. 详细的帧数据:")
    print(f"问询帧: {frame_data.get('query', '未发送')}")
    print(f"应答帧: {frame_data.get('response', '未接收')}")
    print(f"目标地址: {frame_data.get('target_address', '未设置')}")
    
    # 7. 停止问询
    print("\n7. 停止问询")
    response = requests.post('http://localhost:5000/api/query/stop', json={
        'page': 'light'
    })
    print(f"停止问询响应: {response.status_code}")
    print(f"停止问询结果: {response.json()}")
    
    # 8. 关闭TCP通讯
    print("\n8. 关闭TCP通讯")
    response = requests.post('http://localhost:5000/api/serial/close-tcp', json={
        'page': 'light'
    })
    print(f"关闭TCP通讯响应: {response.status_code}")
    print(f"关闭TCP通讯结果: {response.json()}")
    
    print("\n测试完成！")

if __name__ == '__main__':
    test_tcp_frames()
