#!/usr/bin/env python3
"""
TCP+LoRa模式测试脚本
用于测试光照问询功能的TCP网络通信
"""

import socket
import time
import struct

# 配置参数
TCP_SERVER_IP = '192.168.0.80'
TCP_SERVER_PORT = 10125
LORA_TARGET_ADDRESS = '5678'  # LoRa目标地址（十六位）

# 构建问询帧（Modbus-RTU格式）
def build_query_frame():
    """构建光照传感器的问询帧"""
    # 标准Modbus-RTU问询帧：01 03 00 00 00 08 44 0C
    # 01: 从设备地址
    # 03: 功能码（读取保持寄存器）
    # 00 00: 起始寄存器地址
    # 00 08: 读取8个寄存器
    # 44 0C: CRC16校验码
    query_frame = bytearray([0x01, 0x03, 0x00, 0x00, 0x00, 0x08, 0x44, 0x0C])
    return query_frame

# 构建带有LoRa目标地址的问询帧
def build_lora_query_frame():
    """构建带有LoRa目标地址的问询帧"""
    # 构建标准问询帧
    query_frame = build_query_frame()
    
    # 添加LoRa目标地址前缀
    # 将十六进制字符串转换为字节
    lora_address_bytes = bytes.fromhex(LORA_TARGET_ADDRESS)
    
    # 构建完整的LoRa问询帧
    lora_query_frame = lora_address_bytes + query_frame
    return lora_query_frame

# 解析应答帧
def parse_response_frame(response_frame):
    """解析应答帧"""
    if len(response_frame) < 5:
        print("应答帧长度不足")
        return None
    
    # 检查从设备地址和功能码
    if response_frame[0] != 0x01 or response_frame[1] != 0x03:
        print("应答帧格式错误")
        return None
    
    # 提取数据长度
    data_length = response_frame[2]
    
    # 检查应答帧长度
    if len(response_frame) != 3 + data_length + 2:  # 地址+功能码+长度+数据+CRC
        print(f"应答帧长度不符合预期: {len(response_frame)} != {3 + data_length + 2}")
        return None
    
    # 提取数据部分
    data = response_frame[3:-2]  # 去掉地址、功能码、长度和CRC
    
    # 解析数据
    parsed_data = {
        "status": (data[0] << 8) | data[1],
        "temperature": (data[2] << 8) | data[3],
        "humidity": data[4],
        "co2": (data[5] << 8) | data[6],
        "pressure": (data[7] << 24) | (data[8] << 16) | (data[9] << 8) | data[10],
        "light": (data[11] << 24) | (data[12] << 16) | (data[13] << 8) | data[14]
    }
    
    # 转换数据格式
    parsed_data["temperature"] = parsed_data["temperature"] / 10.0  # 温度单位转换
    parsed_data["pressure"] = parsed_data["pressure"] / 100.0  # 气压单位转换
    
    return parsed_data

# 测试TCP+LoRa通信
def test_tcp_lora_communication():
    """测试TCP+LoRa模式的通信"""
    print(f"开始测试TCP+LoRa通信...")
    print(f"TCP服务器: {TCP_SERVER_IP}:{TCP_SERVER_PORT}")
    print(f"LoRa目标地址: {LORA_TARGET_ADDRESS}")
    
    try:
        # 创建TCP套接字
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # 连接服务器
            print("连接TCP服务器...")
            s.connect((TCP_SERVER_IP, TCP_SERVER_PORT))
            print("连接成功！")
            
            # 构建带有LoRa目标地址的问询帧
            lora_query_frame = build_lora_query_frame()
            print(f"发送问询帧: {lora_query_frame.hex(' ')}")
            
            # 发送数据
            s.sendall(lora_query_frame)
            print("问询帧发送成功！")
            
            # 接收应答
            print("等待应答帧...")
            response = s.recv(1024)
            
            if response:
                print(f"收到应答帧: {response.hex(' ')}")
                
                # 解析应答帧
                parsed_data = parse_response_frame(response)
                if parsed_data:
                    print("应答帧解析成功！")
                    print("解析结果:")
                    print(f"  状态: {parsed_data['status']}")
                    print(f"  温度: {parsed_data['temperature']} °C")
                    print(f"  湿度: {parsed_data['humidity']} %")
                    print(f"  CO2浓度: {parsed_data['co2']} ppm")
                    print(f"  气压: {parsed_data['pressure']} kPa")
                    print(f"  光照强度: {parsed_data['light']} lux")
                    return True
                else:
                    print("应答帧解析失败！")
                    return False
            else:
                print("未收到应答帧！")
                return False
                
    except ConnectionRefusedError:
        print(f"连接失败：无法连接到 {TCP_SERVER_IP}:{TCP_SERVER_PORT}")
        print("请检查TCP服务器是否运行，IP和端口是否正确")
        return False
    except socket.timeout:
        print("连接超时：TCP服务器无响应")
        return False
    except Exception as e:
        print(f"发生错误：{str(e)}")
        return False

# 主函数
def main():
    """主函数"""
    print("=====================================")
    print("TCP+LoRa模式测试脚本")
    print("=====================================")
    
    # 运行测试
    success = test_tcp_lora_communication()
    
    print("=====================================")
    if success:
        print("测试成功！TCP+LoRa通信正常")
    else:
        print("测试失败！请检查网络连接和服务器配置")
    print("=====================================")

if __name__ == "__main__":
    main()
