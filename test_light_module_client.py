#!/usr/bin/env python3
# 测试光照模块客户端：向192.168.0.80:10125发送问询帧并接收应答帧
# 本地地址：192.168.0.193

import socket
import time
import struct

def print_frame_details(frame, frame_type):
    """打印帧的详细信息"""
    print(f"{frame_type}:")
    print(f"  长度: {len(frame)}字节")
    print(f"  内容: {' '.join([f'{b:02X}' for b in frame])}")
    print()

def test_light_module_client():
    """测试光照模块客户端"""
    print("开始测试光照模块客户端...")
    print("=" * 80)
    
    # 网络配置
    local_ip = "192.168.0.193"  # 本地客户端地址
    server_ip = "192.168.0.80"  # 远程服务器地址
    server_port = 10125         # 远程服务器端口
    
    # 光照模块问询帧：56 78 01 03 00 00 00 08 44 0C
    # 其中 56 78 是LoRa目标地址，01 03 00 00 00 08 44 0C 是Modbus-RTU问询帧
    query_frame = bytes.fromhex("5678010300000008440C")
    
    print(f"本地地址: {local_ip}")
    print(f"远程服务器: {server_ip}:{server_port}")
    print(f"问询帧: {' '.join([f'{b:02X}' for b in query_frame])}")
    print()
    
    try:
        # 创建TCP套接字
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # 绑定本地地址（可选）
            sock.bind((local_ip, 0))  # 0表示自动分配端口
            print(f"已绑定本地地址: {sock.getsockname()}")
            
            # 设置超时
            sock.settimeout(10)  # 10秒超时
            
            print("正在连接远程服务器...")
            # 连接服务器
            sock.connect((server_ip, server_port))
            print(f"连接成功！远程地址: {sock.getpeername()}")
            print()
            
            # 打印问询帧详情
            print_frame_details(query_frame, "发送的问询帧")
            
            # 发送问询帧
            print("发送问询帧...")
            start_time = time.time()
            sock.sendall(query_frame)
            send_time = time.time() - start_time
            print(f"问询帧发送成功！耗时: {send_time:.4f}秒")
            print()
            
            # 等待并接收应答帧
            print("等待应答帧...")
            start_time = time.time()
            response_data = sock.recv(1024)
            receive_time = time.time() - start_time
            
            print(f"收到应答帧！耗时: {receive_time:.4f}秒")
            print_frame_details(response_data, "收到的应答帧")
            
            # 验证应答帧
            if len(response_data) > 0:
                print("✅ 测试成功：收到了应答帧")
                
                # 检查应答帧格式是否正确
                if len(response_data) >= 21:  # 标准Modbus应答帧长度
                    print("✅ 应答帧长度符合标准")
                    
                    # 解析应答帧数据
                    print("应答帧数据解析:")
                    print(f"  设备地址: {response_data[0]:02X}H")
                    print(f"  功能码: {response_data[1]:02X}H")
                    print(f"  数据长度: {response_data[2]:02X}H")
                    
                    # 状态（2字节）
                    status = (response_data[3] << 8) | response_data[4]
                    print(f"  状态: {status:04X}H {'正常' if status == 0 else '异常'}")
                    
                    # 温度（2字节，0.1°C单位）
                    temperature = (response_data[5] << 8) | response_data[6]
                    if temperature > 32767:
                        temperature = (temperature - 65536) / 10.0
                    else:
                        temperature = temperature / 10.0
                    print(f"  温度: {temperature:.1f}°C")
                    
                    # 湿度（2字节，%单位）
                    humidity = (response_data[7] << 8) | response_data[8]
                    print(f"  湿度: {humidity}%")
                    
                    # CO2浓度（2字节，ppm单位）
                    co2 = (response_data[9] << 8) | response_data[10]
                    print(f"  CO2浓度: {co2}ppm")
                    
                    # 气压（4字节，hPa单位）
                    pressure = (response_data[11] << 24) | (response_data[12] << 16) | (response_data[13] << 8) | response_data[14]
                    print(f"  气压: {pressure}hPa")
                    
                    # 光照强度（4字节，Lux单位）
                    light = (response_data[15] << 24) | (response_data[16] << 16) | (response_data[17] << 8) | response_data[18]
                    print(f"  光照强度: {light}Lux")
                    
                else:
                    print("⚠️  应答帧长度可能不完整")
            else:
                print("❌ 测试失败：未收到应答帧")
                
    except socket.timeout:
        print("❌ 测试失败：连接超时，未收到应答帧")
    except ConnectionRefusedError:
        print("❌ 测试失败：连接被拒绝，请检查服务器是否运行")
    except Exception as e:
        print(f"❌ 测试失败：{str(e)}")
    
    print("=" * 80)
    print("测试完成！")

if __name__ == '__main__':
    test_light_module_client()
