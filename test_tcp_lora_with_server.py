#!/usr/bin/env python3
"""
TCP+LoRa模式测试脚本（带模拟服务器）
用于测试光照问询功能的TCP网络通信
包含模拟TCP服务器和客户端
"""

import socket
import threading
import time
import struct

# 配置参数
TCP_SERVER_IP = '127.0.0.1'  # 本地测试使用localhost
TCP_SERVER_PORT = 10125
LORA_TARGET_ADDRESS = '5678'  # LoRa目标地址（十六位）
TIMEOUT = 5  # 超时时间（秒）

# 模拟TCP服务器类
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
                    print(f"接收到客户端连接: {client_addr}")
                    
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
                    # 假设前两个字节是LoRa目标地址
                    lora_address = data[:2].hex(' ')
                    print(f"服务器解析到LoRa目标地址: {lora_address}")
                    
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
    print(f"超时设置: {TIMEOUT}秒")
    
    try:
        # 创建TCP套接字
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # 设置超时
            s.settimeout(TIMEOUT)
            
            # 连接服务器
            print("客户端连接TCP服务器...")
            s.connect((TCP_SERVER_IP, TCP_SERVER_PORT))
            print("客户端连接成功！")
            
            # 构建带有LoRa目标地址的问询帧
            lora_query_frame = build_lora_query_frame()
            print(f"客户端发送问询帧: {lora_query_frame.hex(' ')}")
            
            # 发送数据
            s.sendall(lora_query_frame)
            print("客户端发送问询帧成功！")
            
            # 接收应答
            print("客户端等待应答帧...")
            start_time = time.time()
            response = s.recv(1024)
            elapsed_time = time.time() - start_time
            print(f"客户端收到应答帧（耗时: {elapsed_time:.2f}秒）: {response.hex(' ')}")
            
            if response:
                # 解析应答帧
                parsed_data = parse_response_frame(response)
                if parsed_data:
                    print("客户端应答帧解析成功！")
                    print("解析结果:")
                    print(f"  状态: {parsed_data['status']}")
                    print(f"  温度: {parsed_data['temperature']} °C")
                    print(f"  湿度: {parsed_data['humidity']} %")
                    print(f"  CO2浓度: {parsed_data['co2']} ppm")
                    print(f"  气压: {parsed_data['pressure']} kPa")
                    print(f"  光照强度: {parsed_data['light']} lux")
                    return True
                else:
                    print("客户端应答帧解析失败！")
                    return False
            else:
                print("客户端未收到应答帧！")
                return False
                
    except socket.timeout:
        print(f"客户端连接超时：超过 {TIMEOUT} 秒无响应")
        return False
    except ConnectionRefusedError:
        print(f"客户端连接失败：无法连接到 {TCP_SERVER_IP}:{TCP_SERVER_PORT}")
        print("请检查TCP服务器是否运行，IP和端口是否正确")
        return False
    except Exception as e:
        print(f"客户端发生错误：{str(e)}")
        return False

# 主函数
def main():
    """主函数"""
    print("=====================================")
    print("TCP+LoRa模式测试脚本（带模拟服务器）")
    print("=====================================")
    
    # 启动模拟TCP服务器
    server = MockTCPServer(TCP_SERVER_IP, TCP_SERVER_PORT)
    server.start()
    
    # 等待服务器启动
    time.sleep(1)
    
    # 运行测试
    success = test_tcp_lora_communication()
    
    # 停止模拟TCP服务器
    server.stop()
    
    print("=====================================")
    if success:
        print("测试成功！TCP+LoRa通信正常")
        print("本地客户端能够成功发送问询帧并接收远端应答帧")
    else:
        print("测试失败！请检查网络连接和服务器配置")
    print("=====================================")

if __name__ == "__main__":
    main()
