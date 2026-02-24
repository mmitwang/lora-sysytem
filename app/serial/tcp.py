"""TCP通讯处理模块"""

import socket
import time
from datetime import datetime
from app.modbus import build_modbus_query, parse_temperature_response, parse_vibration_response, parse_light_gas_response, parse_vibration_sensor_response
from app.serial.frame_handler import FrameHandler


class TCPHandler:
    """TCP通讯处理器"""
    
    def __init__(self):
        """初始化TCP处理器"""
        self.frame_handler = FrameHandler()
    
    def open_tcp(self, serial_service, tcp_server_ip, tcp_server_port, page="light"):
        """打开TCP通讯"""
        try:
            # 检查是否已经连接
            page_config = serial_service.pages.get(page, serial_service.pages["light"])
            if page_config.get("tcp_connected") and page_config.get("tcp_socket"):
                return False, f"{page}页面已经与TCP服务器 {tcp_server_ip}:{tcp_server_port} 建立连接"
            
            # 关闭之前的连接
            self.close_tcp(serial_service, page)
            
            # 验证IP地址格式
            import re
            ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
            if not re.match(ip_pattern, tcp_server_ip):
                return False, "无效的IP地址格式"
            
            # 验证端口范围
            tcp_server_port = int(tcp_server_port)
            if tcp_server_port < 1 or tcp_server_port > 65535:
                return False, "端口号必须在1-65535之间"
            
            # 更新TCP配置
            page_config["tcp_server_ip"] = tcp_server_ip
            page_config["tcp_server_port"] = tcp_server_port
            
            # 创建TCP套接字并保持连接（类似sscom_gui.py）
            import socket
            page_config["tcp_socket"] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            page_config["tcp_socket"].settimeout(0.5)  # 设置较短的超时，用于接收线程
            page_config["tcp_socket"].connect((tcp_server_ip, tcp_server_port))
            page_config["tcp_connected"] = True
            
            # 启动读取线程
            page_config["stop_thread"] = False
            page_config["serial_thread"] = threading.Thread(target=serial_service.read_serial_data, args=(page,))
            page_config["serial_thread"].daemon = True
            page_config["serial_thread"].start()
            
            local_address = page_config["tcp_socket"].getsockname()
            return True, f"{page}页面TCP通讯已打开: IP={tcp_server_ip}, 端口={tcp_server_port}, 本地地址={local_address}"
        except ValueError:
            return False, "无效的端口号格式"
        except Exception as e:
            return False, f"打开TCP通讯失败: {str(e)}"
    
    def close_tcp(self, serial_service, page="light"):
        """关闭TCP通讯"""
        try:
            page_config = serial_service.pages.get(page, serial_service.pages["light"])
            page_config["stop_thread"] = True
            
            # 关闭TCP套接字
            if page_config.get("tcp_socket"):
                try:
                    page_config["tcp_socket"].close()
                except:
                    pass
                page_config["tcp_socket"] = None
            page_config["tcp_connected"] = False
            
            if page_config["serial_thread"]:
                page_config["serial_thread"].join(timeout=1)
            return True, f"{page}页面TCP通讯已关闭"
        except Exception as e:
            return False, f"关闭TCP通讯失败: {str(e)}"
    
    def handle_communication(self, serial_service, page, timestamp):
        """处理TCP通讯"""
        # 获取页面配置
        page_config = serial_service.pages.get(page, serial_service.pages["light"])
        
        # 获取TCP服务器配置
        tcp_server_ip = page_config.get("tcp_server_ip", "192.168.0.80")
        tcp_server_port = page_config.get("tcp_server_port", 10125)
        
        # 检查TCP连接是否有效
        tcp_socket = page_config.get("tcp_socket")
        if not tcp_socket or not page_config.get("tcp_connected"):
            print(f"【{page}页面】TCP连接未建立，重新连接...")
            # 重新建立连接
            try:
                tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tcp_socket.settimeout(0.5)
                tcp_socket.connect((tcp_server_ip, tcp_server_port))
                page_config["tcp_socket"] = tcp_socket
                page_config["tcp_connected"] = True
                local_address = tcp_socket.getsockname()
                print(f"【{page}页面】TCP连接成功，本地地址: {local_address}")
            except Exception as e:
                print(f"【{page}页面】TCP连接失败: {str(e)}")
                page_config["tcp_connected"] = False
                page_config["immediate_query"] = False
                return
        else:
            local_address = tcp_socket.getsockname()
        
        try:
            # 获取页面的网络类型和目标地址
            network_type = page_config.get("network_type", "lora")
            target_address = page_config.get("target_address", "5678")
            
            if page == "light":
                # 读取光照气体数据
                self._handle_light_gas_communication(serial_service, page, tcp_socket, tcp_server_ip, tcp_server_port, local_address, network_type, target_address, timestamp)
            elif page == "temperature":
                # 读取温湿度数据
                self._handle_temperature_communication(serial_service, page, tcp_socket, tcp_server_ip, tcp_server_port, local_address, network_type, target_address, timestamp)
            elif page == "vibration":
                # 读取温振数据
                self._handle_vibration_communication(serial_service, page, tcp_socket, tcp_server_ip, tcp_server_port, local_address, network_type, target_address, timestamp)
            elif page == "config":
                # 配置页面数据
                self._handle_config_communication(serial_service, page, tcp_socket, tcp_server_ip, tcp_server_port, local_address, network_type, target_address, timestamp)
            elif page == "sscom":
                # SSCOM页面，根据问询帧内容自动判断模块类型
                # 尝试使用保存的问询帧
                sscom_query_to_send = None
                if "serial_config" in page_config and "query_frame" in page_config["serial_config"] and page_config["serial_config"]["query_frame"]:
                    try:
                        hex_frame = page_config["serial_config"]["query_frame"].replace(" ", "")
                        sscom_query_to_send = bytearray.fromhex(hex_frame)
                    except ValueError:
                        print(f"【{page}页面】无效的问询帧格式")
                
                # 根据问询帧长度和内容判断模块类型
                if sscom_query_to_send:
                    # 提取实际的Modbus查询帧（去掉可能的LoRa地址前缀）
                    modbus_frame = sscom_query_to_send
                    if len(sscom_query_to_send) > 8:
                        # 可能包含LoRa地址前缀，尝试提取实际的Modbus帧
                        # 标准Modbus-RTU查询帧长度为8字节
                        if len(sscom_query_to_send) == 10:
                            # 包含2字节LoRa地址前缀
                            modbus_frame = sscom_query_to_send[2:]
                    
                    # 根据Modbus帧的寄存器数量判断模块类型
                    if len(modbus_frame) == 8:
                        register_count = (modbus_frame[4] << 8) | modbus_frame[5]
                        if register_count == 0x0008:
                            # 光照气体模块
                            self._handle_light_gas_communication(serial_service, page, tcp_socket, tcp_server_ip, tcp_server_port, local_address, network_type, target_address, timestamp)
                        elif register_count == 0x0002:
                            # 温湿度模块
                            self._handle_temperature_communication(serial_service, page, tcp_socket, tcp_server_ip, tcp_server_port, local_address, network_type, target_address, timestamp)
                        elif register_count == 0x000D:
                            # 温振模块
                            self._handle_vibration_communication(serial_service, page, tcp_socket, tcp_server_ip, tcp_server_port, local_address, network_type, target_address, timestamp)
                        else:
                            # 未知模块类型，默认使用光照气体模块
                            self._handle_light_gas_communication(serial_service, page, tcp_socket, tcp_server_ip, tcp_server_port, local_address, network_type, target_address, timestamp)
                    else:
                        # 未知帧格式，默认使用光照气体模块
                        self._handle_light_gas_communication(serial_service, page, tcp_socket, tcp_server_ip, tcp_server_port, local_address, network_type, target_address, timestamp)
                else:
                    # 没有保存的问询帧，默认使用光照气体模块
                    self._handle_light_gas_communication(serial_service, page, tcp_socket, tcp_server_ip, tcp_server_port, local_address, network_type, target_address, timestamp)
            
            # 重置立即问询标志
            page_config["immediate_query"] = False
        except Exception as e:
            print(f"【{page}页面】TCP通讯错误: {str(e)}")
            page_config["tcp_connected"] = False
            if page_config.get("tcp_socket"):
                try:
                    page_config["tcp_socket"].close()
                except:
                    pass
                page_config["tcp_socket"] = None
            page_config["immediate_query"] = False
    
    def _handle_light_gas_communication(self, serial_service, page, tcp_socket, tcp_server_ip, tcp_server_port, local_address, network_type, target_address, timestamp):
        """处理光照气体模块的TCP通讯"""
        # 尝试使用保存的问询帧
        light_gas_query_to_send = None
        expected_response_length = 21  # 默认长度（不包含目标地址）
        actual_target_address = ""
        target_bytes = b""
        
        page_config = serial_service.pages.get(page, serial_service.pages["light"])
        
        if page == "sscom" and "serial_config" in page_config and "query_frame" in page_config["serial_config"] and page_config["serial_config"]["query_frame"]:
            # 使用保存的问询帧
            try:
                hex_frame = page_config["serial_config"]["query_frame"].replace(" ", "")
                light_gas_query_to_send = bytearray.fromhex(hex_frame)
                expected_response_length = len(light_gas_query_to_send) + 13  # 估计响应长度
                print(f"【{page}页面】使用保存的问询帧: {page_config['serial_config']['query_frame']}")
            except ValueError:
                print(f"【{page}页面】无效的问询帧格式，使用默认问询帧")
                light_gas_query_to_send = None
        
        if not light_gas_query_to_send:
            # 构建默认问询帧: 01 03 00 00 00 08 44 0C
            light_gas_query = build_modbus_query(
                slave_id=0x01,         # 地址码: 01H
                function_code=0x03,     # 功能码: 03H
                start_address=0x0000,   # 起始寄存器: 0000H
                register_count=0x0008    # 寄存器个数: 0008H
            )
            
            light_gas_query_to_send = light_gas_query
            expected_response_length = 21  # 默认长度（不包含目标地址）

        # 确保问询帧包含LoRa目的地址
        extracted_address = target_address
        if network_type == "lora":
            print(f"【{page}页面】使用LoRa网络，添加目标地址前缀")
            try:
                # 将目标地址转换为字节数组并添加到问询帧前面
                target_bytes = bytearray.fromhex(target_address)
                if len(target_bytes) == 2:
                    # 检查问询帧是否已经包含目标地址
                    if len(light_gas_query_to_send) >= 10 and light_gas_query_to_send[:2] == target_bytes:
                        print(f"【{page}页面】问询帧已包含目标地址，使用现有帧")
                    else:
                        # 添加目标地址前缀
                        light_gas_query_to_send = target_bytes + light_gas_query_to_send
                        print(f"【{page}页面】已添加目标地址前缀: {target_address}")
                    extracted_address = target_address
                else:
                    target_bytes = b""
                    print(f"【{page}页面】目标地址长度错误，应为2字节")
            except ValueError:
                target_bytes = b""
                print(f"【{page}页面】无效的目标地址格式")
        else:
            target_bytes = b""
            print(f"【{page}页面】使用标准网络")
        
        # 如果是LoRa网络，调整预期响应长度以包含目标地址前缀
        if network_type == "lora" and len(target_bytes) == 2:
            expected_response_length += len(target_bytes)
            print(f"【{page}页面】调整预期响应长度为: {expected_response_length} 字节")
        
        light_gas_query_str = ' '.join([f'{b:02X}' for b in light_gas_query_to_send])
        print(f"【{page}页面】发送问询帧: {light_gas_query_str}")
        
        # 发送问询帧
        response_data = b""
        try:
            tcp_socket.sendall(light_gas_query_to_send)
            print(f"【{page}页面】TCP发送问询帧成功")
            
            # 接收应答帧（改进接收逻辑，确保收到完整的应答帧）
            print(f"【{page}页面】等待TCP应答帧...")
            start_time = time.time()
            response_data = b""
            # 多次尝试接收，确保收到完整的应答帧
            while time.time() - start_time < 2:  # 2秒超时
                try:
                    chunk = tcp_socket.recv(1024)
                    if chunk:
                        response_data += chunk
                        # 如果收到了足够长度的数据，停止接收
                        if len(response_data) >= expected_response_length:
                            break
                    else:
                        time.sleep(0.1)
                except socket.timeout:
                    # 超时是正常的，继续等待
                    time.sleep(0.1)
                    continue
            
            elapsed_time = time.time() - start_time
            print(f"【{page}页面】收到TCP应答帧（耗时: {elapsed_time:.2f}秒）: {[f'{b:02X}' for b in response_data]}")
            
        except ConnectionResetError:
            print(f"【{page}页面】TCP连接被重置，尝试重新连接")
            page_config["tcp_connected"] = False
            if page_config.get("tcp_socket"):
                try:
                    page_config["tcp_socket"].close()
                except:
                    pass
                page_config["tcp_socket"] = None
        except ConnectionRefusedError:
            print(f"【{page}页面】TCP连接被拒绝，请检查服务器是否运行")
            page_config["tcp_connected"] = False
        except Exception as e:
            print(f"【{page}页面】TCP通信错误: {str(e)}")
            page_config["tcp_connected"] = False
        
        # 解析光照气体应答帧
        print(f"【{page}页面】收到光照气体应答帧长度: {len(response_data)}")
        print(f"【{page}页面】光照气体应答帧内容: {[f'{b:02X}' for b in response_data]}")
        
        # 检查应答帧长度是否符合预期
        if len(response_data) >= expected_response_length:
            # 检查目标地址是否匹配（如果是LoRa网络）
            target_address_match = True
            if network_type == "lora" and len(response_data) >= len(target_bytes):
                # 提取应答帧中的目标地址
                response_target_bytes = response_data[:len(target_bytes)]
                response_target_address = ''.join([f'{b:02X}' for b in response_target_bytes]).upper()
                actual_target_address = response_target_address
                
                # 检查目标地址是否匹配，使用从问询帧中提取的地址
                if response_target_address != extracted_address.upper():
                    print(f"【{page}页面】目标地址不匹配，预期: {extracted_address.upper()}，实际: {response_target_address}")
                    target_address_match = False
                else:
                    print(f"【{page}页面】目标地址匹配: {response_target_address}")
            
            # 只有当目标地址匹配时才解析数据
            if target_address_match:
                actual_modbus_response = response_data
                
                # 不手动移除LoRa前缀，让parse_light_gas_response函数处理
                # 这样与串口处理保持一致
                print(f"【{page}页面】直接使用完整应答帧进行解析，长度: {len(actual_modbus_response)} 字节")
                
                light_gas_result = parse_light_gas_response(actual_modbus_response)
                if light_gas_result:
                    # 更新光照气体数据
                    page_config["data"] = {
                        "status": light_gas_result["status"],
                        "temperature": light_gas_result["temperature"],
                        "humidity": light_gas_result["humidity"],
                        "co2": light_gas_result["co2"],
                        "pressure": light_gas_result["pressure"],
                        "light": light_gas_result["light"],
                        "timestamp": timestamp
                    }
                    print(f"【{page}页面】解析到光照气体数据: {page_config['data']}")
                    if actual_target_address:
                        print(f"【{page}页面】目标地址: {actual_target_address}")
                else:
                    print(f"【{page}页面】光照气体解析失败，保持之前的数据")
                    # 只更新时间戳，保持其他数据不变
                    page_config["data"]["timestamp"] = timestamp
            else:
                print(f"【{page}页面】目标地址不匹配，跳过解析")
                # 只更新时间戳，保持其他数据不变
                page_config["data"]["timestamp"] = timestamp
        else:
            print(f"【{page}页面】光照气体应答帧长度不足，保持之前的数据，长度: {len(response_data)}")
            # 只更新时间戳，保持其他数据不变
            page_config["data"]["timestamp"] = timestamp
        
        # 保存帧数据
        self.frame_handler.save_frame_data(
            serial_service, page, "tcp", light_gas_query_to_send, response_data,
            network_type, target_address, target_bytes, timestamp, tcp_server_ip, tcp_server_port, local_address
        )
    
    def _handle_temperature_communication(self, serial_service, page, tcp_socket, tcp_server_ip, tcp_server_port, local_address, network_type, target_address, timestamp):
        """处理温湿度模块的TCP通讯"""
        # 尝试使用保存的问询帧
        temp_query_to_send = None
        expected_response_length = 11  # 包含LoRa地址的完整长度
        actual_target_address = ""
        target_bytes = b""
        
        page_config = serial_service.pages.get(page, serial_service.pages["temperature"])
        
        if page == "sscom" and "serial_config" in page_config and "query_frame" in page_config["serial_config"] and page_config["serial_config"]["query_frame"]:
            # 使用保存的问询帧
            try:
                hex_frame = page_config["serial_config"]["query_frame"].replace(" ", "")
                temp_query_to_send = bytearray.fromhex(hex_frame)
                expected_response_length = len(temp_query_to_send) + 5  # 估计响应长度
                print(f"【{page}页面】使用保存的温湿度问询帧: {page_config['serial_config']['query_frame']}")
            except ValueError:
                print(f"【{page}页面】无效的问询帧格式，使用默认问询帧")
                temp_query_to_send = None
        
        if not temp_query_to_send:
            # 构建默认问询帧
            temp_query = build_modbus_query(
                slave_id=0x01,
                function_code=0x03,
                start_address=0x0000,
                register_count=0x0002
            )
            
            temp_query_to_send = temp_query
            expected_response_length = 11  # 包含LoRa地址的完整长度
        
        # 确保问询帧包含LoRa目的地址
        extracted_address = target_address
        if network_type == "lora":
            print(f"【{page}页面】使用LoRa网络，添加目标地址前缀")
            try:
                # 将目标地址转换为字节数组并添加到问询帧前面
                target_bytes = bytearray.fromhex(target_address)
                if len(target_bytes) == 2:
                    # 检查问询帧是否已经包含目标地址
                    if len(temp_query_to_send) >= 10 and temp_query_to_send[:2] == target_bytes:
                        print(f"【{page}页面】问询帧已包含目标地址，使用现有帧")
                    else:
                        # 添加目标地址前缀
                        temp_query_to_send = target_bytes + temp_query_to_send
                        print(f"【{page}页面】已添加目标地址前缀: {target_address}")
                    extracted_address = target_address
                else:
                    target_bytes = b""
                    print(f"【{page}页面】目标地址长度错误，应为2字节")
            except ValueError:
                target_bytes = b""
                print(f"【{page}页面】无效的目标地址格式")
        else:
            target_bytes = b""
            print(f"【{page}页面】使用标准网络")
        
        # 如果是LoRa网络，调整预期响应长度以包含目标地址前缀
        if network_type == "lora" and len(target_bytes) == 2:
            expected_response_length += len(target_bytes)
            print(f"【{page}页面】调整预期响应长度为: {expected_response_length} 字节")
        
        temp_query_str = ' '.join([f'{b:02X}' for b in temp_query_to_send])
        print(f"【{page}页面】发送温湿度问询帧: {temp_query_str}")
        
        # 使用保持的TCP连接发送数据
        response_data = b""
        try:
            tcp_socket.sendall(temp_query_to_send)
            print(f"【{page}页面】TCP发送问询帧成功")
            
            print(f"【{page}页面】等待TCP应答帧...")
            start_time = time.time()
            response_data = b""
            # 多次尝试接收，确保收到完整的应答帧
            while time.time() - start_time < 2:  # 2秒超时
                try:
                    chunk = tcp_socket.recv(1024)
                    if chunk:
                        response_data += chunk
                        # 如果收到了足够长度的数据，停止接收
                        if len(response_data) >= expected_response_length:
                            break
                    else:
                        time.sleep(0.1)
                except socket.timeout:
                    # 超时是正常的，继续等待
                    time.sleep(0.1)
                    continue
            
            elapsed_time = time.time() - start_time
            print(f"【{page}页面】收到TCP应答帧（耗时: {elapsed_time:.2f}秒）: {[f'{b:02X}' for b in response_data]}")
            
        except ConnectionResetError:
            print(f"【{page}页面】TCP连接被重置，尝试重新连接")
            page_config["tcp_connected"] = False
            if page_config.get("tcp_socket"):
                try:
                    page_config["tcp_socket"].close()
                except:
                    pass
                page_config["tcp_socket"] = None
        except ConnectionRefusedError:
            print(f"【{page}页面】TCP连接被拒绝，请检查服务器是否运行")
            page_config["tcp_connected"] = False
        except Exception as e:
            print(f"【{page}页面】TCP通信错误: {str(e)}")
            page_config["tcp_connected"] = False
        
        print(f"【{page}页面】收到温湿度应答帧长度: {len(response_data)}")
        print(f"【{page}页面】温湿度应答帧内容: {[f'{b:02X}' for b in response_data]}")
        
        page_config = serial_service.pages.get(page, serial_service.pages["temperature"])
        if len(response_data) >= expected_response_length:
            target_address_match = True
            if network_type == "lora" and len(response_data) >= len(target_bytes):
                response_target_bytes = response_data[:len(target_bytes)]
                response_target_address = ''.join([f'{b:02X}' for b in response_target_bytes]).upper()
                actual_target_address = response_target_address
                
                if response_target_address != extracted_address.upper():
                    print(f"【{page}页面】目标地址不匹配，预期: {extracted_address.upper()}，实际: {response_target_address}")
                    target_address_match = False
                else:
                    print(f"【{page}页面】目标地址匹配: {response_target_address}")
            
            if target_address_match:
                actual_modbus_response = response_data
                
                # 不手动移除LoRa前缀，让parse_temperature_response函数处理
                # 这样与串口处理保持一致
                print(f"【{page}页面】直接使用完整应答帧进行解析，长度: {len(actual_modbus_response)} 字节")
                
                if len(actual_modbus_response) >= 7:
                    temp_result = parse_temperature_response(actual_modbus_response)
                    if temp_result:
                        page_config["data"] = {
                            "temperature": temp_result["temperature"],
                            "humidity": temp_result["humidity"],
                            "timestamp": timestamp
                        }
                        print(f"【{page}页面】解析到温湿度数据: {page_config['data']}")
                        if actual_target_address:
                            print(f"【{page}页面】目标地址: {actual_target_address}")
                    else:
                        print(f"【{page}页面】温湿度解析失败，保持之前的数据")
                        page_config["data"]["timestamp"] = timestamp
                else:
                    print(f"【{page}页面】温湿度应答帧长度不足，保持之前的数据")
                    page_config["data"]["timestamp"] = timestamp
            else:
                print(f"【{page}页面】目标地址不匹配，跳过解析")
                page_config["data"]["timestamp"] = timestamp
        else:
            print(f"【{page}页面】未收到应答帧，使用默认数据")
            page_config["data"] = {
                "temperature": 25.5,
                "humidity": 60.0,
                "timestamp": timestamp
            }
        
        # 保存帧数据
        self.frame_handler.save_frame_data(
            serial_service, page, "tcp", temp_query_to_send, response_data,
            network_type, target_address, target_bytes, timestamp, tcp_server_ip, tcp_server_port, local_address
        )
    
    def _handle_vibration_communication(self, serial_service, page, tcp_socket, tcp_server_ip, tcp_server_port, local_address, network_type, target_address, timestamp):
        """处理温振模块的TCP通讯"""
        # 尝试使用保存的问询帧
        vib_query_to_send = None
        expected_response_length = 13  # 包含LoRa地址的完整长度
        actual_target_address = ""
        target_bytes = b""
        
        page_config = serial_service.pages.get(page, serial_service.pages["vibration"])
        
        if "serial_config" in page_config and "query_frame" in page_config["serial_config"] and page_config["serial_config"]["query_frame"]:
            # 使用保存的问询帧
            try:
                hex_frame = page_config["serial_config"]["query_frame"].replace(" ", "")
                vib_query_to_send = bytearray.fromhex(hex_frame)
                expected_response_length = len(vib_query_to_send) + 5  # 估计响应长度
                print(f"【{page}页面】使用保存的温振问询帧: {page_config['serial_config']['query_frame']}")
            except ValueError:
                print(f"【{page}页面】无效的问询帧格式，使用默认问询帧")
                vib_query_to_send = None
        
        if not vib_query_to_send:
            # 构建默认问询帧（38个寄存器，0000-0025）
            vib_query = build_modbus_query(
                slave_id=0x01,
                function_code=0x03,
                start_address=0x0000,
                register_count=0x0026
            )
            
            vib_query_to_send = vib_query
            expected_response_length = 81  # 1+1+1+76+2 = 81字节（38个寄存器的应答帧）
        
        # 确保问询帧包含LoRa目的地址
        extracted_address = target_address
        if network_type == "lora":
            print(f"【{page}页面】使用LoRa网络，添加目标地址前缀")
            try:
                # 将目标地址转换为字节数组并添加到问询帧前面
                target_bytes = bytearray.fromhex(target_address)
                if len(target_bytes) == 2:
                    # 检查问询帧是否已经包含目标地址
                    if len(vib_query_to_send) >= 10 and vib_query_to_send[:2] == target_bytes:
                        print(f"【{page}页面】问询帧已包含目标地址，使用现有帧")
                    else:
                        # 添加目标地址前缀
                        vib_query_to_send = target_bytes + vib_query_to_send
                        print(f"【{page}页面】已添加目标地址前缀: {target_address}")
                    extracted_address = target_address
                else:
                    target_bytes = b""
                    print(f"【{page}页面】目标地址长度错误，应为2字节")
            except ValueError:
                target_bytes = b""
                print(f"【{page}页面】无效的目标地址格式")
        else:
            target_bytes = b""
            print(f"【{page}页面】使用标准网络")
        
        # 如果是LoRa网络，调整预期响应长度以包含目标地址前缀
        if network_type == "lora" and len(target_bytes) == 2:
            expected_response_length += len(target_bytes)
            print(f"【{page}页面】调整预期响应长度为: {expected_response_length} 字节")
        
        vib_query_str = ' '.join([f'{b:02X}' for b in vib_query_to_send])
        print(f"【{page}页面】发送温振问询帧: {vib_query_str}")
        
        response_data = b""
        try:
            tcp_socket.sendall(vib_query_to_send)
            print(f"【{page}页面】TCP发送温振问询帧成功")
            
            start_time = time.time()
            response_data = b""
            # 多次尝试接收，确保收到完整的应答帧（包括分两次返回的情况）
            while time.time() - start_time < 2:  # 2秒超时
                try:
                    chunk = tcp_socket.recv(1024)
                    if chunk:
                        response_data += chunk
                        print(f"【{page}页面】收到应答帧片段，长度: {len(chunk)} 字节，累计长度: {len(response_data)} 字节")
                        # 对于温振传感器，我们需要等待更长时间以确保收到所有数据
                        # 即使达到预期长度，也继续接收一小段时间，以防数据分两次返回
                        if len(response_data) >= expected_response_length:
                            # 继续接收一小段时间，以防数据分两次返回
                            time.sleep(0.2)
                            try:
                                additional_chunk = tcp_socket.recv(1024)
                                if additional_chunk:
                                    response_data += additional_chunk
                                    print(f"【{page}页面】收到额外应答帧片段，长度: {len(additional_chunk)} 字节，累计长度: {len(response_data)} 字节")
                            except socket.timeout:
                                pass
                            break
                    else:
                        time.sleep(0.1)
                except socket.timeout:
                    # 超时是正常的，继续等待
                    time.sleep(0.1)
                    continue
            
            elapsed_time = time.time() - start_time
            print(f"【{page}页面】收到TCP温振应答帧（耗时: {elapsed_time:.2f}秒）: {[f'{b:02X}' for b in response_data]}")
            
        except ConnectionResetError:
            print(f"【{page}页面】TCP连接被重置，尝试重新连接")
            page_config["tcp_connected"] = False
            if page_config.get("tcp_socket"):
                try:
                    page_config["tcp_socket"].close()
                except:
                    pass
                page_config["tcp_socket"] = None
        except ConnectionRefusedError:
            print(f"【{page}页面】TCP连接被拒绝，请检查服务器是否运行")
            page_config["tcp_connected"] = False
        except Exception as e:
            print(f"【{page}页面】TCP通信错误: {str(e)}")
            page_config["tcp_connected"] = False
        
        print(f"【{page}页面】收到温振应答帧长度: {len(response_data)}")
        
        page_config = serial_service.pages.get(page, serial_service.pages["vibration"])
        
        if len(response_data) >= expected_response_length:
            target_address_match = True
            if network_type == "lora" and len(response_data) >= len(target_bytes):
                response_target_bytes = response_data[:len(target_bytes)]
                response_target_address = ''.join([f'{b:02X}' for b in response_target_bytes]).upper()
                actual_target_address = response_target_address
                
                if response_target_address != extracted_address.upper():
                    print(f"【{page}页面】目标地址不匹配，预期: {extracted_address.upper()}，实际: {response_target_address}")
                    target_address_match = False
                else:
                    print(f"【{page}页面】目标地址匹配: {response_target_address}")
            
            if target_address_match:
                actual_modbus_response = response_data
                
                # 不手动移除LoRa前缀，让parse_vibration_response函数处理
                # 这样与串口处理保持一致
                print(f"【{page}页面】直接使用完整应答帧进行解析，长度: {len(actual_modbus_response)} 字节")
                
                # 使用温振传感器解析函数
                if len(actual_modbus_response) >= 9:
                    vib_result = parse_vibration_response(actual_modbus_response)
                    if vib_result:
                        page_config["data"] = vib_result
                        page_config["data"]["timestamp"] = timestamp
                        print(f"【{page}页面】解析到温振数据: 温度={vib_result['temperature']:.1f}°C")
                        if actual_target_address:
                            print(f"【{page}页面】目标地址: {actual_target_address}")
                    else:
                        print(f"【{page}页面】温振解析失败，保持之前的数据")
                        if "data" in page_config:
                            page_config["data"]["timestamp"] = timestamp
                else:
                    print(f"【{page}页面】温振应答帧长度不足，保持之前的数据")
                    if "data" in page_config:
                        page_config["data"]["timestamp"] = timestamp
            else:
                print(f"【{page}页面】目标地址不匹配，跳过解析")
                if "data" in page_config:
                    page_config["data"]["timestamp"] = timestamp
        else:
            print(f"【{page}页面】未收到应答帧，保持之前的数据")
            if "data" in page_config:
                page_config["data"]["timestamp"] = timestamp
        
        # 保存振动数据帧
        self.frame_handler.save_frame_data(
            serial_service, page, "tcp", vib_query_to_send, response_data,
            network_type, target_address, target_bytes, timestamp, tcp_server_ip, tcp_server_port, local_address
        )
    
    def _handle_config_communication(self, serial_service, page, tcp_socket, tcp_server_ip, tcp_server_port, local_address, network_type, target_address, timestamp):
        """处理配置页面的TCP通讯"""
        # 配置页面暂时不支持TCP，使用默认数据
        print(f"【{page}页面】TCP模式暂不支持配置数据，使用默认数据")
        page_config = serial_service.pages.get(page, serial_service.pages["config"])
        page_config["data"]["timestamp"] = timestamp
        page_config["frame_data"]["query"] = "TCP模式暂不支持"
        page_config["frame_data"]["response"] = "TCP模式暂不支持"
        # 重置立即问询标志
        page_config["immediate_query"] = False

# 导入threading模块
import threading
