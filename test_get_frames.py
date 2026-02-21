#!/usr/bin/env python3
# 测试获取帧数据

import requests

def test_get_frames():
    print("测试获取帧数据...")
    
    # 获取帧数据
    response = requests.get('http://localhost:5000/api/serial/frames?page=light')
    print(f"响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        frame_data = response.json()
        print(f"帧数据: {frame_data}")
        print(f"问询帧: {frame_data.get('query', '未发送')}")
        print(f"应答帧: {frame_data.get('response', '未接收')}")
    else:
        print(f"请求失败: {response.text}")

if __name__ == '__main__':
    test_get_frames()
