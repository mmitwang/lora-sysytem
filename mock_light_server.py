#!/usr/bin/env python3
# 模拟光照模块TCP服务器，能够响应问询帧并返回正常的应答帧

import socket
import threading
import time

def handle_client(client_socket, client_address):
    """处理客户端连接"""
    print(f"\n新客户端连接: {client_address}")
    
    try:
        while True:
            # 接收问询帧
            data = client_socket.recv(1024)
            if not data:
                break
            
            print(f"收到问询帧: {' '.join([f'{b:02X}' for b in data])}")
            
            # 检查是否是光照模块的问询帧
            # 问询帧格式: 56 78 01 03 00 00 00 08 44 0C
            # 或者: 01 03 00 00 00 08 44 0C (不含LoRa目标地址)
            
            # 提取Modbus部分（去除可能的LoRa目标地址前缀）
            modbus_frame = data
            if len(data) > 8 and data[:2] == b'\x56\x78':
                # 有LoRa目标地址前缀
                modbus_frame = data[2:]
                print("检测到LoRa目标地址前缀: 56 78")
            
            # 检查是否是读取保持寄存器的问询帧 (功能码03)
            if len(modbus_frame) == 8 and modbus_frame[0] == 0x01 and modbus_frame[1] == 0x03:
                print("识别为读取保持寄存器的问询帧")
                
                # 模拟光照模块的应答帧
                # 应答帧格式: 01 03 10 00 00 00 EC 00 19 03 00 00 01 03 FE 00 00 01 A7 B0 6C
                # 包含：状态、温度、湿度、CO2、气压、光照强度等数据
                response_frame = bytes.fromhex("010310000000EC00190300000103FE000001A7B06C")
                
                # 如果原始问询帧包含LoRa目标地址，应答帧也需要包含
                if len(data) > 8 and data[:2] == b'\x56\x78':
                    response_frame = b'\x56\x78' + response_frame
                    print("添加LoRa目标地址前缀到应答帧")
                
                print(f"发送应答帧: {' '.join([f'{b:02X}' for b in response_frame])}")
                client_socket.sendall(response_frame)
                print("应答帧发送成功！")
            else:
                print("未知的问询帧格式")
                # 发送错误应答
                error_response = bytes.fromhex("018302")  # 功能码错误
                if len(data) > 8 and data[:2] == b'\x56\x78':
                    error_response = b'\x56\x78' + error_response
                client_socket.sendall(error_response)
                print(f"发送错误应答: {' '.join([f'{b:02X}' for b in error_response])}")
            
            # 短暂延迟，模拟设备处理时间
            time.sleep(0.1)
            
    except Exception as e:
        print(f"处理客户端连接时出错: {e}")
    finally:
        print(f"客户端断开连接: {client_address}")
        client_socket.close()

def start_server():
    """启动模拟TCP服务器"""
    server_ip = "0.0.0.0"  # 监听所有网络接口
    server_port = 10125
    
    # 创建TCP套接字
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        # 绑定地址和端口
        server_socket.bind((server_ip, server_port))
        # 开始监听
        server_socket.listen(5)
        
        print("=====================================")
        print("模拟光照模块TCP服务器")
        print("=====================================")
        print(f"服务器地址: {server_ip}:{server_port}")
        print("按 Ctrl+C 停止服务器")
        print("=====================================")
        print("服务器已启动，等待客户端连接...")
        
        while True:
            # 接受客户端连接
            client_socket, client_address = server_socket.accept()
            # 创建线程处理客户端
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.daemon = True
            client_thread.start()
            
    except KeyboardInterrupt:
        print("\n服务器正在停止...")
    except Exception as e:
        print(f"服务器启动失败: {e}")
    finally:
        server_socket.close()
        print("服务器已停止")

if __name__ == '__main__':
    start_server()
