"""测试串口扫描功能"""

import requests


def test_serial_scan():
    """测试串口扫描 API 端点"""
    try:
        # 发送请求获取串口列表
        response = requests.get('http://localhost:5000/api/serial/ports')
        
        # 检查响应状态码
        if response.status_code == 200:
            ports = response.json()
            print(f"成功获取串口列表，共 {len(ports)} 个串口:")
            for port in ports:
                print(f"- {port['device']}: {port['description']}")
            return True
        else:
            print(f"获取串口列表失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"测试失败: {e}")
        return False


if __name__ == '__main__':
    test_serial_scan()
