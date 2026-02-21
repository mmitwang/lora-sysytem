#!/usr/bin/env python3
# 测试向192.168.0.116服务器发送问询帧并获取应答

import socket
import time

def test_tcp_server_response():
    print("开始测试向192.168.0.116服务器发送问询帧...")
    
    # 服务器配置
    server_ip = "192.168.0.116"
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
            sock.settimeout(10)  # 10秒超时
            
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
            elapsed_time = time.time() - start_time
            
            print(f"收到应答帧（耗时: {elapsed_time:.2f}秒）")
            print(f"应答帧长度: {len(response_data)}字节")
            print(f"应答帧内容: {' '.join([f'{b:02X}' for b in response_data])}")
            
            # 验证应答帧
            if len(response_data) > 0:
                print("✅ 测试成功：收到了应答帧")
            else:
                print("❌ 测试失败：未收到应答帧")
                
    except socket.timeout:
        print("❌ 测试失败：连接超时，未收到应答帧")
    except ConnectionRefusedError:
        print("❌ 测试失败：连接被拒绝，请检查服务器是否运行")
    except Exception as e:
        print(f"❌ 测试失败：{str(e)}")
    
    print("测试完成！")

if __name__ == '__main__':
    test_tcp_server_response()
