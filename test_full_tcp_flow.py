#!/usr/bin/env python3
# 测试完整的TCP模式流程：设置通讯模式、打开通讯、启动问询、获取数据和帧数据

import requests
import time

def test_full_tcp_flow():
    print("开始测试完整的TCP模式流程...")
    
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
    
    # 等待问询执行
    print("\n4. 等待问询执行...")
    for i in range(5):
        time.sleep(1)
        print(f"等待 {i+1} 秒...")
    
    # 5. 获取传感器数据
    print("\n5. 获取传感器数据")
    response = requests.get('http://localhost:5000/api/sensor/data?page=light')
    print(f"获取传感器数据响应: {response.status_code}")
    sensor_data = response.json()
    print(f"获取到的传感器数据: {sensor_data}")
    
    # 6. 获取帧数据
    print("\n6. 获取帧数据")
    response = requests.get('http://localhost:5000/api/serial/frames?page=light')
    print(f"获取帧数据响应: {response.status_code}")
    frame_data = response.json()
    print(f"获取到的帧数据: {frame_data}")
    
    # 打印详细的帧数据
    print("\n7. 详细的帧数据:")
    print(f"问询帧: {frame_data.get('query', '未发送')}")
    print(f"应答帧: {frame_data.get('response', '未接收')}")
    print(f"目标地址: {frame_data.get('target_address', '未设置')}")
    
    # 8. 验证帧数据是否存在
    print("\n8. 验证帧数据:")
    if frame_data.get('query'):
        print("✅ 问询帧存在")
    else:
        print("❌ 问询帧不存在")
    
    if frame_data.get('response'):
        print("✅ 应答帧存在")
    else:
        print("❌ 应答帧不存在")
    
    # 9. 停止问询
    print("\n9. 停止问询")
    response = requests.post('http://localhost:5000/api/query/stop', json={
        'page': 'light'
    })
    print(f"停止问询响应: {response.status_code}")
    print(f"停止问询结果: {response.json()}")
    
    # 10. 关闭TCP通讯
    print("\n10. 关闭TCP通讯")
    response = requests.post('http://localhost:5000/api/serial/close-tcp', json={
        'page': 'light'
    })
    print(f"关闭TCP通讯响应: {response.status_code}")
    print(f"关闭TCP通讯结果: {response.json()}")
    
    print("\n测试完成！")
    
    # 总结
    print("\n=== 测试总结 ===")
    if frame_data.get('query') and frame_data.get('response'):
        print("✅ TCP模式下的帧数据获取功能正常工作")
        print("✅ 后端能够正确保存和返回问询帧和应答帧")
        print("✅ 前端应该能够正常显示这些帧数据")
    else:
        print("❌ TCP模式下的帧数据获取功能存在问题")

if __name__ == '__main__':
    test_full_tcp_flow()
