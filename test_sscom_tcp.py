#!/usr/bin/env python3
# SSCOM TCP模式测试脚本
# 模拟SSCOM调试器的TCP Client模式，进行HEX发送和接收测试

import socket
import time
from datetime import datetime

def get_timestamp():
    """获取当前时间戳"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

def hex_to_bytes(hex_str):
    """将十六进制字符串转换为字节流"""
    try:
        # 移除空格
        hex_str = hex_str.replace(' ', '')
        # 检查长度是否为偶数
        if len(hex_str) % 2 != 0:
            hex_str = '0' + hex_str
        # 转换为字节流
        return bytes.fromhex(hex_str)
    except ValueError as e:
        print(f"错误: 无效的十六进制字符串 - {e}")
        return None

def bytes_to_hex(data):
    """将字节流转换为十六进制字符串"""
    return ' '.join([f'{b:02X}' for b in data])

def test_tcp_client():
    """测试TCP客户端模式"""
    # 测试参数
    server_ip = "127.0.0.1"
    server_port = 10125
    test_query = "56 78 01 03 00 00 00 08 44 0C"
    
    print("=====================================")
    print("SSCOM TCP Client模式测试")
    print("=====================================")
    print(f"测试时间: {get_timestamp()}")
    print(f"测试服务器: {server_ip}:{server_port}")
    print("测试问询帧: 56 78 01 03 00 00 00 08 44 0C")
    print("=====================================")
    
    # 转换问询帧为字节流
    query_bytes = hex_to_bytes(test_query)
    if not query_bytes:
        print("错误: 无效的问询帧")
        return
    
    print(f"\n[发送] 时间: {get_timestamp()}")
    print(f"[发送] HEX: {test_query}")
    print(f"[发送] 长度: {len(query_bytes)}字节")
    
    try:
        # 创建TCP套接字
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # 设置超时
            sock.settimeout(5)
            
            print(f"\n[连接] 正在连接服务器: {server_ip}:{server_port}")
            # 连接服务器
            sock.connect((server_ip, server_port))
            local_addr = sock.getsockname()
            print(f"[连接] 连接成功！本地地址: {local_addr[0]}:{local_addr[1]}")
            
            # 发送问询帧
            sock.sendall(query_bytes)
            print("[发送] 问询帧发送成功")
            
            # 接收应答帧
            print("[接收] 等待应答帧...")
            start_time = time.time()
            response_data = sock.recv(1024)
            elapsed_time = time.time() - start_time
            
            if response_data:
                response_hex = bytes_to_hex(response_data)
                print(f"[接收] 时间: {get_timestamp()}")
                print(f"[接收] HEX: {response_hex}")
                print(f"[接收] 长度: {len(response_data)}字节")
                print(f"[接收] 耗时: {elapsed_time:.2f}秒")
                
                # 检查是否包含LoRa目标地址前缀
                if len(response_data) >= 23 and response_data[:2] == b'\x56\x78':
                    print("[解析] 检测到LoRa目标地址前缀: 56 78")
                    modbus_data = response_data[2:]
                else:
                    modbus_data = response_data
                
                # 尝试解析传感器数据
                if len(modbus_data) == 21 and modbus_data[0] == 0x01 and modbus_data[1] == 0x03 and modbus_data[2] == 0x10:
                    print("[解析] 识别为光照模块的应答帧")
                    
                    # 解析数据
                    try:
                        # 状态（2字节）
                        status = (modbus_data[3] << 8) | modbus_data[4]
                        status_text = "正常" if status == 0 else "异常"
                        
                        # 温度（2字节，0.1°C单位）
                        temperature = (modbus_data[5] << 8) | modbus_data[6]
                        if temperature > 32767:
                            temperature = (temperature - 65536) / 10.0
                        else:
                            temperature = temperature / 10.0
                        
                        # 湿度（2字节，%单位）
                        humidity = (modbus_data[7] << 8) | modbus_data[8]
                        
                        # CO2浓度（2字节，ppm单位）
                        co2 = (modbus_data[9] << 8) | modbus_data[10]
                        
                        # 气压（4字节，hPa单位）
                        pressure = (modbus_data[11] << 24) | (modbus_data[12] << 16) | (modbus_data[13] << 8) | modbus_data[14]
                        
                        # 光照强度（4字节，Lux单位）
                        light = (modbus_data[15] << 24) | (modbus_data[16] << 16) | (modbus_data[17] << 8) | modbus_data[18]
                        
                        print("[解析] 解析成功:")
                        print(f"[解析]   状态: {status} ({status_text})")
                        print(f"[解析]   温度: {temperature:.1f} °C")
                        print(f"[解析]   湿度: {humidity} %")
                        print(f"[解析]   CO2浓度: {co2} ppm")
                        print(f"[解析]   气压: {pressure} hPa")
                        print(f"[解析]   光照强度: {light} Lux")
                    except Exception as e:
                        print(f"[解析] 解析传感器数据失败: {e}")
                else:
                    print("[解析] 不是光照模块的应答帧")
            else:
                print("[接收] 未收到应答帧")
                
    except ConnectionRefusedError:
        print(f"[错误] 连接被拒绝，请检查服务器是否运行")
    except socket.timeout:
        print(f"[错误] 连接超时，未收到应答帧")
    except Exception as e:
        print(f"[错误] TCP通信错误: {str(e)}")
    
    print("\n=====================================")
    print("测试完成")
    print("=====================================")

if __name__ == '__main__':
    test_tcp_client()
