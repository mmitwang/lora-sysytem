#!/usr/bin/env python3
"""
持续运行的模拟TCP服务器
用于测试TCP+LoRa通信功能
"""

import socket
import threading
import time
import struct

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
                    lora_address = b""
                    actual_query = data
                    
                    if len(data) > 8:
                        # 假设前两个字节是LoRa目标地址
                        lora_address = data[:2]
                        print(f"服务器解析到LoRa目标地址: {lora_address.hex(' ')}")
                        # 提取实际的问询帧（跳过目标地址前缀）
                        actual_query = data[2:]
                        print(f"服务器提取问询帧: {actual_query.hex(' ')}")
                    else:
                        print(f"服务器解析到标准问询帧")
                    
                    # 根据问询帧内容判断模块类型并生成相应的应答帧
                    response_frame = self._generate_response_frame(actual_query)
                    
                    # 添加LoRa目标地址前缀（如果有）
                    if len(lora_address) > 0:
                        full_response = lora_address + response_frame
                    else:
                        full_response = response_frame
                    
                    print(f"服务器发送应答帧: {full_response.hex(' ')}")
                    
                    # 发送应答帧给客户端
                    client_socket.sendall(full_response)
                    print("服务器发送应答帧成功")
        except Exception as e:
            print(f"处理客户端连接时错误: {str(e)}")
        finally:
            try:
                client_socket.close()
            except:
                pass
    
    def _generate_response_frame(self, query_frame):
        """根据问询帧生成模拟应答帧"""
        import random
        
        # 判断问询帧类型
        if len(query_frame) >= 8 and query_frame[1] == 0x03:
            # Modbus-RTU查询帧
            register_count = (query_frame[4] << 8) | query_frame[5]
            
            if register_count == 0x0001:
                # 温振模块（1个寄存器 - 仅温度）
                temperature = random.randint(200, 350)
                
                # 计算CRC16校验
                data_without_crc = bytearray([0x01, 0x03, 0x02, (temperature >> 8) & 0xFF, temperature & 0xFF])
                crc = self._calculate_crc16(data_without_crc)
                
                response_frame = bytearray([
                    0x01, 0x03, 0x02,  # 地址、功能码、数据长度
                    (temperature >> 8) & 0xFF, temperature & 0xFF,  # 温度
                    crc & 0xFF, (crc >> 8) & 0xFF  # CRC16校验码（小端序）
                ])
                
                print(f"服务器生成温振数据（仅温度）: 温度={temperature/10:.1f}°C")
            
            elif register_count == 0x0002:
                # 温湿度模块（2个寄存器）
                temperature = random.randint(200, 350)
                humidity = random.randint(30, 70)
                
                # 计算CRC16校验
                data_without_crc = bytearray([0x01, 0x03, 0x04, (temperature >> 8) & 0xFF, temperature & 0xFF, (humidity >> 8) & 0xFF, humidity & 0xFF])
                crc = self._calculate_crc16(data_without_crc)
                
                response_frame = bytearray([
                    0x01, 0x03, 0x04,  # 地址、功能码、数据长度
                    (temperature >> 8) & 0xFF, temperature & 0xFF,  # 温度
                    (humidity >> 8) & 0xFF, humidity & 0xFF,  # 湿度
                    crc & 0xFF, (crc >> 8) & 0xFF  # CRC16校验码（小端序）
                ])
                
                print(f"服务器生成温湿度数据: 温度={temperature/10:.1f}°C, 湿度={humidity}%")
            
            elif register_count == 0x0008:
                # 光照气体模块（8个寄存器）
                temperature = random.randint(200, 350)
                humidity = random.randint(30, 70)
                co2 = random.randint(400, 1000)
                pressure = random.randint(98000, 103000)
                light = random.randint(100, 5000)
                
                # 计算CRC16校验
                data_without_crc = bytearray([
                    0x01, 0x03, 0x10,  # 地址、功能码、数据长度
                    0x00, 0x00,  # 状态
                    (temperature >> 8) & 0xFF, temperature & 0xFF,  # 温度
                    (humidity >> 8) & 0xFF, humidity & 0xFF,  # 湿度
                    (co2 >> 8) & 0xFF, co2 & 0xFF,  # CO2浓度
                    (pressure >> 24) & 0xFF, (pressure >> 16) & 0xFF, (pressure >> 8) & 0xFF, pressure & 0xFF,  # 气压
                    (light >> 24) & 0xFF, (light >> 16) & 0xFF, (light >> 8) & 0xFF, light & 0xFF  # 光照强度
                ])
                crc = self._calculate_crc16(data_without_crc)
                
                response_frame = bytearray([
                    0x01, 0x03, 0x10,  # 地址、功能码、数据长度
                    0x00, 0x00,  # 状态
                    (temperature >> 8) & 0xFF, temperature & 0xFF,  # 温度
                    (humidity >> 8) & 0xFF, humidity & 0xFF,  # 湿度
                    (co2 >> 8) & 0xFF, co2 & 0xFF,  # CO2浓度
                    (pressure >> 24) & 0xFF, (pressure >> 16) & 0xFF, (pressure >> 8) & 0xFF, pressure & 0xFF,  # 气压
                    (light >> 24) & 0xFF, (light >> 16) & 0xFF, (light >> 8) & 0xFF, light & 0xFF,  # 光照强度
                    crc & 0xFF, (crc >> 8) & 0xFF  # CRC16校验码（小端序）
                ])
                
                print(f"服务器生成光照气体数据: 温度={temperature/10:.1f}°C, 湿度={humidity}%, CO2={co2}ppm, 气压={pressure}Pa, 光照={light}Lux")
                
            elif register_count == 0x0026:
                # 温振模块（38个寄存器，0000-0025）
                # 寄存器映射：
                # 0000: 温度 (扩大10倍)
                # 0001: 速度X (扩大10倍)
                # 0002: 速度Y (扩大10倍)
                # 0003: 速度Z (扩大10倍)
                # 0004: 位移X (扩大10倍)
                # 0005: 位移Y (扩大10倍)
                # 0006: 位移Z (扩大10倍)
                # 0007-0008: 保留
                # 0009: 版本号
                # 000A: 加速度X (扩大10倍)
                # 000B: 加速度Y (扩大10倍)
                # 000C: 加速度Z (扩大10倍)
                # 000D-0020: 保留
                # 0021: X轴振动频率 (float)
                # 0022: 保留
                # 0023: Y轴振动频率 (float)
                # 0024: 保留
                # 0025: Z轴振动频率 (float)
                
                temperature = random.randint(200, 350)
                velocity_x = random.randint(0, 50)
                velocity_y = random.randint(0, 50)
                velocity_z = random.randint(0, 50)
                displacement_x = random.randint(0, 200)
                displacement_y = random.randint(0, 200)
                displacement_z = random.randint(0, 200)
                version = 0x0101
                acceleration_x = random.randint(0, 50)
                acceleration_y = random.randint(0, 50)
                acceleration_z = random.randint(0, 50)
                freq_x = random.uniform(10.0, 100.0)
                freq_y = random.uniform(10.0, 100.0)
                freq_z = random.uniform(10.0, 100.0)
                
                # 计算CRC16校验
                data_without_crc = bytearray([
                    0x01, 0x03, 0x4C,  # 地址、功能码、数据长度（76字节）
                    (temperature >> 8) & 0xFF, temperature & 0xFF,  # 温度 (0000)
                    (velocity_x >> 8) & 0xFF, velocity_x & 0xFF,  # 速度X (0001)
                    (velocity_y >> 8) & 0xFF, velocity_y & 0xFF,  # 速度Y (0002)
                    (velocity_z >> 8) & 0xFF, velocity_z & 0xFF,  # 速度Z (0003)
                    (displacement_x >> 8) & 0xFF, displacement_x & 0xFF,  # 位移X (0004)
                    (displacement_y >> 8) & 0xFF, displacement_y & 0xFF,  # 位移Y (0005)
                    (displacement_z >> 8) & 0xFF, displacement_z & 0xFF,  # 位移Z (0006)
                    0x00, 0x00,  # 保留 (0007)
                    0x00, 0x00,  # 保留 (0008)
                    (version >> 8) & 0xFF, version & 0xFF,  # 版本号 (0009)
                    (acceleration_x >> 8) & 0xFF, acceleration_x & 0xFF,  # 加速度X (000A)
                    (acceleration_y >> 8) & 0xFF, acceleration_y & 0xFF,  # 加速度Y (000B)
                    (acceleration_z >> 8) & 0xFF, acceleration_z & 0xFF,  # 加速度Z (000C)
                ])
                
                # 000D-0020: 保留 (20个寄存器，40字节)
                data_without_crc.extend([0x00] * 40)
                
                # 0021-0022: X轴振动频率 (float, 4字节，占用2个寄存器)
                freq_x_bytes = struct.pack('>f', freq_x)
                data_without_crc.extend(freq_x_bytes)
                
                # 0023-0024: Y轴振动频率 (float, 4字节，占用2个寄存器)
                freq_y_bytes = struct.pack('>f', freq_y)
                data_without_crc.extend(freq_y_bytes)
                
                # 0025-0026: Z轴振动频率 (float, 4字节，占用2个寄存器)
                freq_z_bytes = struct.pack('>f', freq_z)
                data_without_crc.extend(freq_z_bytes)
                
                # 0027-0028: 保留 (4字节)
                data_without_crc.extend([0x00, 0x00, 0x00, 0x00])
                
                # 计算CRC
                crc = self._calculate_crc16(data_without_crc)
                
                # 构建完整应答帧
                response_frame = bytearray(data_without_crc)
                response_frame.extend([crc & 0xFF, (crc >> 8) & 0xFF])
                
                print(f"服务器生成温振数据: 温度={temperature/10:.1f}°C, 速度X={velocity_x/10:.1f}mm/s, 速度Y={velocity_y/10:.1f}mm/s, 速度Z={velocity_z/10:.1f}mm/s")
                print(f"  频率X={freq_x:.2f}Hz, 频率Y={freq_y:.2f}Hz, 频率Z={freq_z:.2f}Hz")
            
            else:
                # 未知模块类型，返回错误响应
                response_frame = bytearray([0x01, 0x83, 0x02])  # 异常码：非法数据地址
                print(f"服务器收到未知问询帧类型，返回异常响应")
        else:
            # 未知问询帧格式，返回错误响应
            response_frame = bytearray([0x01, 0x83, 0x02])  # 异常码：非法数据地址
            print(f"服务器收到未知问询帧格式，返回异常响应")
        
        return response_frame
    
    def _calculate_crc16(self, data):
        """计算Modbus RTU CRC16校验"""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return crc

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
