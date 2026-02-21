#!/usr/bin/env python3
"""
持续运行的模拟TCP服务器
用于测试TCP+LoRa通信功能
"""

import socket
import threading
import time

# 配置参数
TCP_SERVER_IP = ''  # 监听所有接口
TCP_SERVER_PORT = 10125

class MockTCPServer:
    """模拟TCP服务器，用于测试客户端通信"""
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.thread = None
    
    def start(self):
        """启动服务器"""
        self.running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()
        print(f"模拟TCP服务器已启动: {self.host}:{self.port}")
        print("服务器将持续运行，等待客户端连接...")
    
    def stop(self):
        """停止服务器"""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        if self.thread:
            self.thread.join(timeout=1)
        print("模拟TCP服务器已停止")
    
    def _run(self):
        """服务器主循环"""
        try:
            # 创建服务器套接字
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            while self.running:
                try:
                    self.server_socket.settimeout(1)
                    client_socket, client_addr = self.server_socket.accept()
                    print(f"\n接收到客户端连接: {client_addr}")
                    
                    # 处理客户端请求
                    self._handle_client(client_socket)
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"服务器错误: {str(e)}")
                    break
        except Exception as e:
            print(f"服务器启动失败: {str(e)}")
    
    def _handle_client(self, client_socket):
        """处理客户端连接"""
        try:
            client_socket.settimeout(2)
            
            # 接收客户端发送的数据
            data = client_socket.recv(1024)
            if data:
                print(f"服务器收到数据: {data.hex(' ')}")
                
                # 检查是否是带有LoRa目标地址的问询帧
                if len(data) >= 8:
                    # 检查是否带有LoRa目标地址前缀
                    # 如果数据长度大于8，可能带有目标地址前缀
                    if len(data) > 8:
                        # 假设前两个字节是LoRa目标地址
                        lora_address = data[:2].hex(' ')
                        print(f"服务器解析到LoRa目标地址: {lora_address}")
                        # 提取实际的问询帧（跳过目标地址前缀）
                        actual_query = data[2:]
                        print(f"服务器提取问询帧: {actual_query.hex(' ')}")
                        
                        # 模拟生成应答帧，并添加相同的LoRa目标地址前缀
                        response_frame = self._generate_response_frame()
                        # 添加LoRa目标地址前缀
                        full_response = data[:2] + response_frame
                        print(f"服务器发送应答帧: {full_response.hex(' ')}")
                        
                        # 发送应答帧给客户端
                        client_socket.sendall(full_response)
                        print("服务器发送应答帧成功")
                    else:
                        # 没有LoRa目标地址前缀
                        print(f"服务器解析到标准问询帧")
                        actual_query = data
                        
                        # 模拟生成应答帧
                        response_frame = self._generate_response_frame()
                        print(f"服务器发送应答帧: {response_frame.hex(' ')}")
                        
                        # 发送应答帧给客户端
                        client_socket.sendall(response_frame)
                        print("服务器发送应答帧成功")
        except Exception as e:
            print(f"处理客户端连接时错误: {str(e)}")
        finally:
            try:
                client_socket.close()
            except:
                pass
    
    def _generate_response_frame(self):
        """生成模拟应答帧"""
        # 模拟光照传感器的应答帧
        # 标准Modbus-RTU应答帧格式
        # 01: 从设备地址
        # 03: 功能码
        # 10: 数据长度（16字节）
        # 00 00: 状态
        # 00 EC: 温度（23.6°C）
        # 00 19: 湿度（25%）
        # 03 00: CO2浓度（768ppm）
        # 00 01 03 FE: 气压（101.4kPa）
        # 00 00 01 A7: 光照强度（423lux）
        # B0 6C: CRC16校验码
        response_frame = bytearray([
            0x01, 0x03, 0x10,  # 地址、功能码、数据长度
            0x00, 0x00,  # 状态
            0x00, 0xEC,  # 温度
            0x00, 0x19,  # 湿度
            0x03, 0x00,  # CO2浓度
            0x00, 0x01, 0x03, 0xFE,  # 气压
            0x00, 0x00, 0x01, 0xA7,  # 光照强度
            0xB0, 0x6C  # CRC16校验码
        ])
        return response_frame

# 主函数
def main():
    """主函数"""
    print("=====================================")
    print("持续运行的模拟TCP服务器")
    print("用于测试TCP+LoRa通信功能")
    print("=====================================")
    print(f"服务器地址: {TCP_SERVER_IP}:{TCP_SERVER_PORT}")
    print("按 Ctrl+C 停止服务器")
    print("=====================================")
    
    # 创建并启动服务器
    server = MockTCPServer(TCP_SERVER_IP, TCP_SERVER_PORT)
    server.start()
    
    try:
        # 持续运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n收到停止信号，正在停止服务器...")
        server.stop()
        print("服务器已停止")

if __name__ == "__main__":
    main()
