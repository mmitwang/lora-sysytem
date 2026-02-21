#!/usr/bin/env python3
# 模拟SSCOM调试器 - TCP客户端模式测试工具
# 支持HEX显示和发送，加时间戳和分包显示

import socket
import time
from datetime import datetime
import threading
import sys

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
        print(f"[{get_timestamp()}] 错误: 无效的十六进制字符串 - {e}")
        return None

def bytes_to_hex(data):
    """将字节流转换为十六进制字符串"""
    return ' '.join([f'{b:02X}' for b in data])

def display_received_data(data, is_hex=True):
    """显示接收到的数据"""
    timestamp = get_timestamp()
    if is_hex:
        hex_data = bytes_to_hex(data)
        print(f"[{timestamp}] [接收] HEX: {hex_data}")
        print(f"[{timestamp}] [接收] 长度: {len(data)}字节")
    else:
        try:
            ascii_data = data.decode('utf-8', errors='replace')
            print(f"[{timestamp}] [接收] ASCII: {ascii_data}")
        except Exception as e:
            print(f"[{timestamp}] [接收] 错误: {e}")
    print()

def receive_data(sock, stop_event, is_hex=True):
    """接收数据线程"""
    while not stop_event.is_set():
        try:
            # 设置超时，以便能够及时响应停止事件
            sock.settimeout(0.5)
            data = sock.recv(1024)
            if data:
                # 分包显示
                if len(data) > 64:
                    # 大数据包分包显示
                    print(f"[{get_timestamp()}] [接收] 大数据包开始，总长度: {len(data)}字节")
                    offset = 0
                    while offset < len(data):
                        chunk_size = min(64, len(data) - offset)
                        chunk = data[offset:offset+chunk_size]
                        display_received_data(chunk, is_hex)
                        offset += chunk_size
                    print(f"[{get_timestamp()}] [接收] 大数据包结束")
                else:
                    # 正常大小数据包直接显示
                    display_received_data(data, is_hex)
        except socket.timeout:
            continue
        except ConnectionResetError:
            print(f"[{get_timestamp()}] [错误] 连接被重置")
            stop_event.set()
            break
        except Exception as e:
            print(f"[{get_timestamp()}] [错误] 接收数据失败: {e}")
            stop_event.set()
            break

def send_data(sock, data):
    """发送数据"""
    try:
        sock.sendall(data)
        timestamp = get_timestamp()
        print(f"[{timestamp}] [发送] HEX: {bytes_to_hex(data)}")
        print(f"[{timestamp}] [发送] 长度: {len(data)}字节")
        print()
        return True
    except Exception as e:
        print(f"[{get_timestamp()}] [错误] 发送数据失败: {e}")
        return False

def sscom_simulator():
    """SSCOM模拟器主函数"""
    print("=====================================")
    print("SSCOM模拟器 - TCP客户端模式")
    print("=====================================")
    print("支持功能:")
    print("  - TCP客户端模式连接")
    print("  - HEX格式发送和显示")
    print("  - 时间戳显示")
    print("  - 分包显示大数据包")
    print("=====================================")
    
    # 获取服务器信息
    server_ip = input("请输入服务器IP地址: ")
    
    # 验证端口号
    while True:
        try:
            server_port = int(input("请输入服务器端口: "))
            if 0 <= server_port <= 65535:
                break
            else:
                print("错误: 端口号必须在0-65535之间")
        except ValueError:
            print("错误: 请输入有效的整数端口号")
    
    print(f"[{get_timestamp()}] 正在连接到 {server_ip}:{server_port}...")
    
    try:
        # 创建TCP套接字
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((server_ip, server_port))
        print(f"[{get_timestamp()}] 连接成功！")
        print(f"[{get_timestamp()}] 本地地址: {sock.getsockname()}")
        print(f"[{get_timestamp()}] 远程地址: {sock.getpeername()}")
        print()
        
        # 创建停止事件
        stop_event = threading.Event()
        
        # 启动接收数据线程
        receive_thread = threading.Thread(target=receive_data, args=(sock, stop_event, True))
        receive_thread.daemon = True
        receive_thread.start()
        
        print("=====================================")
        print("操作说明:")
        print("  - 输入十六进制字符串发送数据（支持空格分隔）")
        print("  - 输入 'exit' 或 'quit' 退出程序")
        print("  - 输入 'clear' 清空屏幕")
        print("  - 输入 'help' 查看帮助")
        print("=====================================")
        print()
        
        # 主循环
        while not stop_event.is_set():
            try:
                # 获取用户输入
                user_input = input("请输入发送数据 (HEX格式): ")
                
                # 处理特殊命令
                if user_input.lower() == 'exit' or user_input.lower() == 'quit':
                    print(f"[{get_timestamp()}] 退出程序...")
                    stop_event.set()
                    break
                elif user_input.lower() == 'clear':
                    if sys.platform == 'win32':
                        import os
                        os.system('cls')
                    else:
                        os.system('clear')
                    continue
                elif user_input.lower() == 'help':
                    print("=====================================")
                    print("操作说明:")
                    print("  - 输入十六进制字符串发送数据（支持空格分隔）")
                    print("  - 输入 'exit' 或 'quit' 退出程序")
                    print("  - 输入 'clear' 清空屏幕")
                    print("  - 输入 'help' 查看帮助")
                    print("=====================================")
                    print()
                    continue
                
                # 转换为字节流
                data = hex_to_bytes(user_input)
                if data:
                    # 发送数据
                    send_data(sock, data)
                
            except KeyboardInterrupt:
                print(f"\n[{get_timestamp()}] 退出程序...")
                stop_event.set()
                break
            except Exception as e:
                print(f"[{get_timestamp()}] 错误: {e}")
                continue
        
    except ConnectionRefusedError:
        print(f"[{get_timestamp()}] 错误: 连接被拒绝，请检查服务器是否运行")
    except Exception as e:
        print(f"[{get_timestamp()}] 错误: {e}")
    finally:
        try:
            if 'sock' in locals():
                sock.close()
                print(f"[{get_timestamp()}] 连接已关闭")
        except Exception as e:
            print(f"[{get_timestamp()}] 错误: {e}")
    
    print(f"[{get_timestamp()}] 程序已退出")

if __name__ == '__main__':
    sscom_simulator()
