#!/usr/bin/env python3
# 测试向本地服务器发送问询帧并获取应答

import socket
import time
import threading

def start_mock_server():
    """启动本地模拟TCP服务器"""
    def server_thread():
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("127.0.0.1", 10125))
        server.listen(1)
        print("本地模拟服务器已启动: 127.0.0.1:10125")
        
        try:
            while True:
                conn, addr = server.accept()
                print(f"接收到来自 {addr} 的连接")
                
                try:
                    # 接收问询帧
                    data = conn.recv(1024)
                    print(f"收到问询帧: {' '.join([f'{b:02X}' for b in data])}")
                    
                    # 模拟应答帧（包含LoRa目标地址前缀）
                    # 应答帧: 56 78 01 03 10 00 00 00 EC 00 19 03 00 00 01 03 FE 00 00 01 A7 B0 6C
                    response_frame = bytes.fromhex("5678010310000000EC00190300000103FE000001A7B06C")
                    print(f"发送应答帧: {' '.join([f'{b:02X}' for b in response_frame])}")
                    
                    # 发送应答帧
                    conn.sendall(response_frame)
                finally:
                    conn.close()
        except:
            pass
        finally:
            server.close()
    
    # 启动服务器线程
    thread = threading.Thread(target=server_thread, daemon=True)
    thread.start()
    time.sleep(1)  # 等待服务器启动

def test_local_tcp_response():
    print("开始测试向本地服务器发送问询帧...")
    
    # 启动本地模拟服务器
    start_mock_server()
    
    # 服务器配置
    server_ip = "127.0.0.1"
    server_port = 10125
    
    # 问询帧：56 78 01 03 00 00 00 08 44 0C
    # 其中 56 78 是LoRa目标地址，01 03 00 00 00 08 44 0C 是Modbus-RTU问询帧
    query_frame = bytes.fromhex("5678010300000008440C")
    
    print(f"服务器地址: {server_ip}:{server_port}")
    print(f"发送的问询帧: {' '.join([f'{b:02X}' for b in query_frame])}")
    
    try:
        # 创建TCP套接字
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # 设置超时
            sock.settimeout(5)  # 5秒超时
            
            print("正在连接服务器...")
            # 连接服务器
            sock.connect((server_ip, server_port))
            print("连接成功！")
            
            # 发送问询帧
            print("发送问询帧...")
            sock.sendall(query_frame)
            print("问询帧发送成功！")
            
            # 等待并接收应答帧
            print("等待应答帧...")
            start_time = time.time()
            response_data = sock.recv(1024)
