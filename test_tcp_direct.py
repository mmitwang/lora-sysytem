#!/usr/bin/env python3
"""
直接测试TCP通信功能的脚本
不依赖于主系统，直接模拟客户端发送数据到服务器
"""

import socket
import time

def test_tcp_communication():
    print("=====================================")
    print("直接测试TCP通信功能")
    print("=====================================")
    
    # 服务器地址和端口
    server_ip = "127.0.0.1"
    server_port = 10125
    
    print(f"尝试连接到服务器: {server_ip}:{server_port}")
    
    try:
        # 创建TCP套接字
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # 设置超时
            sock.settimeout(5)
            
            # 连接服务器
            sock.connect((server_ip, server_port))
            print("TCP连接成功!")
            
            # 构建问询帧（模拟光照传感器的问询帧）
            # 01 03 00 00 00 08 44 0C
            query_frame = bytearray([
                0x01, 0x03, 0x00, 0x00, 0x00, 0x08, 0x44, 0x0C
            ])
            
            print(f"发送问询帧: {query_frame.hex(' ')}")
            
            # 发送问询帧
            sock.sendall(query_frame)
            print("问询帧发送成功!")
            
            # 接收应答帧
            print("等待应答帧...")
            start_time = time.time()
            response_frame = sock.recv(1024)
            elapsed_time = time.time() - start_time
            
            print(f"收到应答帧（耗时: {elapsed_time:.2f}秒）: {response_frame.hex(' ')}")
            print("应答帧接收成功!")
            
            # 解析应答帧
            if len(response_frame) > 0:
                print("\n解析应答帧:")
                print(f"应答帧长度: {len(response_frame)}字节")
                print(f"应答帧内容: {response_frame.hex(' ')}")
    except socket.timeout:
        print("TCP连接超时，未收到应答帧")
    except ConnectionRefusedError:
        print("TCP连接被拒绝，请检查服务器是否运行")
    except Exception as e:
        print(f"TCP通信错误: {str(e)}")
    
    print("\n=====================================")
    print("测试完成")
    print("=====================================")

if __name__ == "__main__":
    test_tcp_communication()
