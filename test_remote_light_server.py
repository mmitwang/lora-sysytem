#!/usr/bin/env python3
# 测试向远程地址192.168.0.80:10125发送光照模块问询帧
# 每隔30秒发送一次，显示问询帧和封装的IP帧

import socket
import time
import struct

def create_ip_header(src_ip, dst_ip, protocol, data_length):
    """创建IP头部"""
    version = 4
    ihl = 5
    version_ihl = (version << 4) | ihl
    tos = 0
    total_length = 20 + data_length  # IP头部20字节 + 数据长度
    identification = 0
    flags_offset = 0
    ttl = 64
    protocol = protocol
    header_checksum = 0  # 暂时设为0，后续计算
    src_ip = socket.inet_aton(src_ip)
    dst_ip = socket.inet_aton(dst_ip)
    
    # 构建IP头部
    ip_header = struct.pack('!BBHHHBBH4s4s', 
                          version_ihl, tos, total_length, 
                          identification, flags_offset, ttl, 
                          protocol, header_checksum, src_ip, dst_ip)
    
    return ip_header

def create_tcp_header(src_port, dst_port, data_length):
    """创建TCP头部"""
    seq_num = 0
    ack_num = 0
    data_offset = 5
    reserved = 0
    flags = 0x02  # SYN标志
    window = socket.htons(8192)
    checksum = 0
    urgent_pointer = 0
    
    # 构建TCP头部
    tcp_header = struct.pack('!HHLLBBHHH', 
                           src_port, dst_port, seq_num, 
                           ack_num, (data_offset << 4) | reserved, 
                           flags, window, checksum, urgent_pointer)
    
    return tcp_header

def print_frame_details(frame, frame_type):
    """打印帧的详细信息"""
    print(f"{frame_type}:")
    print(f"  长度: {len(frame)}字节")
    print(f"  内容: {' '.join([f'{b:02X}' for b in frame])}")
    print()

def test_remote_light_server():
    """测试向远程服务器发送光照模块问询帧"""
    print("开始测试向远程服务器192.168.0.80:10125发送光照模块问询帧...")
    print("每隔30秒发送一次，按Ctrl+C停止测试")
    print("=" * 80)
    
    # 服务器配置
    server_ip = "192.168.0.80"
    server_port = 10125
    
    # 光照模块问询帧：56 78 01 03 00 00 00 08 44 0C
    # 其中 56 78 是LoRa目标地址，01 03 00 00 00 08 44 0C 是Modbus-RTU问询帧
    query_frame = bytes.fromhex("5678010300000008440C")
    
    print(f"服务器地址: {server_ip}:{server_port}")
    print(f"基础问询帧: {' '.join([f'{b:02X}' for b in query_frame])}")
    print()
    
    try:
        while True:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 准备发送问询帧...")
            
            try:
                # 创建TCP套接字
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    # 设置超时
                    sock.settimeout(10)  # 10秒超时
                    
                    print("正在连接服务器...")
                    # 连接服务器
                    sock.connect((server_ip, server_port))
                    print("连接成功！")
                    
                    # 获取本地和远程地址信息
                    local_addr = sock.getsockname()
                    remote_addr = sock.getpeername()
                    print(f"本地地址: {local_addr[0]}:{local_addr[1]}")
                    print(f"远程地址: {remote_addr[0]}:{remote_addr[1]}")
                    
                    # 打印问询帧详情
                    print_frame_details(query_frame, "问询帧")
                    
                    # 模拟IP帧封装（仅用于显示）
                    ip_header = create_ip_header(local_addr[0], server_ip, socket.IPPROTO_TCP, len(query_frame))
                    tcp_header = create_tcp_header(local_addr[1], server_port, len(query_frame))
                    
                    # 打印封装的IP帧（仅用于显示）
                    print("封装的IP帧结构（模拟）:")
                    print(f"  IP头部: {' '.join([f'{b:02X}' for b in ip_header])}")
                    print(f"  TCP头部: {' '.join([f'{b:02X}' for b in tcp_header])}")
                    print(f"  数据部分: {' '.join([f'{b:02X}' for b in query_frame])}")
                    print()
                    
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
                    print_frame_details(response_data, "应答帧")
                    
                    # 验证应答帧
                    if len(response_data) > 0:
                        print("✅ 测试成功：收到了应答帧")
                        
                        # 检查应答帧格式是否正确
                        if len(response_data) >= 21:  # 标准Modbus应答帧长度
                            print("✅ 应答帧长度符合标准")
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
            print("等待30秒后再次发送...")
            print("=" * 80)
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n测试已停止")
    
    print("测试完成！")

if __name__ == '__main__':
    test_remote_light_server()
