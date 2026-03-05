"""Modbus协议服务模块"""

from app.config import Config
import time


def calculate_crc(data):
    """计算Modbus-RTU CRC16校验码"""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc


def build_modbus_query(slave_id=None, function_code=None, start_address=None, register_count=None):
    """构建Modbus-RTU问询帧"""
    # 使用配置中的默认值
    slave_id = slave_id or Config.MODBUS_SLAVE_ID
    function_code = function_code or Config.MODBUS_FUNCTION_CODE
    start_address = start_address or Config.MODBUS_START_ADDRESS
    register_count = register_count or Config.MODBUS_REGISTER_COUNT
    
    # 构建数据部分
    data = [
        slave_id,
        function_code,
        (start_address >> 8) & 0xFF,  # 起始地址高字节
        start_address & 0xFF,         # 起始地址低字节
        (register_count >> 8) & 0xFF,  # 寄存器数量高字节
        register_count & 0xFF          # 寄存器数量低字节
    ]
    
    # 计算CRC16校验码
    crc = calculate_crc(data)
    
    # 添加校验码（低位在前，高位在后）
    data.append(crc & 0xFF)
    data.append((crc >> 8) & 0xFF)
    
    return bytearray(data)


def bytes_to_float(bytes_data):
    """将4字节大端序数据转换为浮点数"""
    import struct
    # 将字节数据转换为大端序浮点数
    return struct.unpack('>f', bytes_data)[0]


def parse_temperature_response(response):
    """解析温度和湿度数据"""
    try:
        if len(response) < 9:
            print(f"应答帧长度不足: {len(response)}")
            return None
        
        # 检查是否包含LoRa目标地址前缀
        # 假设LoRa目标地址前缀为2字节
        modbus_start = 0
        if len(response) >= 11 and response[0] not in [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10]:
            # 可能包含LoRa目标地址前缀，跳过前2字节
            modbus_start = 2
            print(f"检测到可能的LoRa目标地址前缀，从位置{modbus_start}开始解析")
        
        # 检查地址码和功能码
        if response[modbus_start] != Config.MODBUS_SLAVE_ID or response[modbus_start + 1] != Config.MODBUS_FUNCTION_CODE:
            print(f"忽略非01地址码的应答帧: 地址码={response[modbus_start]:02X}, 功能码={response[modbus_start + 1]:02X}")
            return None
        
        # 检查有效字节数（2个寄存器，每个2字节，共4字节）
        if response[modbus_start + 2] != 0x04:
            print(f"有效字节数错误: {response[modbus_start + 2]:02X}")
            return None
        
        # 提取温度值（2字节，有符号16位）
        # 湿度在前，温度在后
        humidity_raw = (response[modbus_start + 3] << 8) | response[modbus_start + 4]
        temperature_raw = (response[modbus_start + 5] << 8) | response[modbus_start + 6]
        
        # 计算CRC校验
        crc_data = response[modbus_start:modbus_start + 7]
        expected_crc = calculate_crc(crc_data)
        actual_crc = (response[modbus_start + 7] << 8) | response[modbus_start + 8]
        
        if expected_crc != actual_crc:
            print(f"CRC校验失败: 预期={expected_crc:04X}, 实际={actual_crc:04X}")
            # 暂时忽略CRC校验失败，继续解析数据
        
        # 转换为实际值（寄存器值 ÷ 10）
        # 温度：有符号16位，需要处理补码
        if temperature_raw > 32767:
            temperature = (temperature_raw - 65536) / 10.0
        else:
            temperature = temperature_raw / 10.0
        
        # 湿度：无符号16位，也需要除以10
        humidity = humidity_raw / 10.0
        
        # 验证数据范围
        if temperature < Config.TEMPERATURE_RANGE[0] or temperature > Config.TEMPERATURE_RANGE[1]:
            print(f"温度值超出范围: {temperature}")
            return None
        
        if humidity < Config.HUMIDITY_RANGE[0] or humidity > Config.HUMIDITY_RANGE[1]:
            print(f"湿度值超出范围: {humidity}")
            return None
        
        print(f"解析成功: 温度={temperature}°C, 湿度={humidity}%")
        return {
            "temperature": temperature,
            "humidity": humidity
        }
    except Exception as e:
        print(f"解析温度应答帧失败: {e}")
        return None


def parse_frequency_response(response):
    """解析振动频率数据"""
    try:
        if len(response) < 9:
            print(f"应答帧长度不足: {len(response)}")
            return None
        
        # 检查地址码和功能码
        if response[0] != Config.MODBUS_SLAVE_ID or response[1] != Config.MODBUS_FUNCTION_CODE:
            print(f"忽略非01地址码的应答帧: 地址码={response[0]:02X}, 功能码={response[1]:02X}")
            return None
        
        # 检查有效字节数
        if response[2] not in [0x04, 0x0C]:
            print(f"有效字节数错误: {response[2]:02X}")
            return None
        
        # 提取频率值（按float类型解析）
        if response[2] == 0x04:  # 4字节数据
            if len(response) < 11:
                print(f"应答帧长度不足: {len(response)}")
                return None
            frequency_bytes = response[3:7]  # 4字节float数据
            frequency = bytes_to_float(frequency_bytes)
        elif response[2] == 0x0C:  # 12字节数据（XYZ三个轴）
            if len(response) < 17:
                print(f"应答帧长度不足: {len(response)}")
                return None
            # 提取X轴频率（前4字节float数据）
            frequency_bytes = response[3:7]  # 4字节float数据
            frequency = bytes_to_float(frequency_bytes)
        
        # 计算CRC校验
        crc_data = response[:-2]
        expected_crc = calculate_crc(crc_data)
        actual_crc = (response[-1] << 8) | response[-2]
        
        if expected_crc != actual_crc:
            print(f"CRC校验失败: 预期={expected_crc:04X}, 实际={actual_crc:04X}")
            # 暂时忽略CRC校验失败，继续解析数据
        
        print(f"解析成功: 频率={frequency}Hz")
        return {
            "frequency": frequency
        }
    except Exception as e:
        print(f"解析频率应答帧失败: {e}")
        return None


def parse_velocity_response(response):
    """解析速度数据"""
    try:
        if len(response) < 9:
            print(f"应答帧长度不足: {len(response)}")
            return None
        
        # 检查地址码和功能码
        if response[0] != Config.MODBUS_SLAVE_ID or response[1] != Config.MODBUS_FUNCTION_CODE:
            print(f"忽略非01地址码的应答帧: 地址码={response[0]:02X}, 功能码={response[1]:02X}")
            return None
        
        # 检查有效字节数
        if response[2] not in [0x02, 0x06]:
            print(f"有效字节数错误: {response[2]:02X}")
            return None
        
        # 提取速度值
        if response[2] == 0x02:  # 2字节数据（单轴）
            velocity_raw = (response[3] << 8) | response[4]
        elif response[2] == 0x06:  # 6字节数据（XYZ三个轴）
            # 提取X轴速度（前2字节）
            velocity_raw = (response[3] << 8) | response[4]
        
        # 计算CRC校验
        crc_data = response[:-2]
        expected_crc = calculate_crc(crc_data)
        actual_crc = (response[-1] << 8) | response[-2]
        
        if expected_crc != actual_crc:
            print(f"CRC校验失败: 预期={expected_crc:04X}, 实际={actual_crc:04X}")
            # 暂时忽略CRC校验失败，继续解析数据
        
        # 转换为实际值（寄存器值 ÷ 10）
        velocity = velocity_raw / 10.0
        
        print(f"解析成功: 速度={velocity}mm/s")
        return {
            "velocity": velocity
        }
    except Exception as e:
        print(f"解析速度应答帧失败: {e}")
        return None


def parse_acceleration_response(response):
    """解析加速度数据"""
    try:
        if len(response) < 9:
            print(f"应答帧长度不足: {len(response)}")
            return None
        
        # 检查地址码和功能码
        if response[0] != Config.MODBUS_SLAVE_ID or response[1] != Config.MODBUS_FUNCTION_CODE:
            print(f"忽略非01地址码的应答帧: 地址码={response[0]:02X}, 功能码={response[1]:02X}")
            return None
        
        # 检查有效字节数
        if response[2] not in [0x02, 0x06]:
            print(f"有效字节数错误: {response[2]:02X}")
            return None
        
        # 提取加速度值
        if response[2] == 0x02:  # 2字节数据（单轴）
            acceleration_raw = (response[3] << 8) | response[4]
        elif response[2] == 0x06:  # 6字节数据（XYZ三个轴）
            # 提取X轴加速度（前2字节）
            acceleration_raw = (response[3] << 8) | response[4]
        
        # 计算CRC校验
        crc_data = response[:-2]
        expected_crc = calculate_crc(crc_data)
        actual_crc = (response[-1] << 8) | response[-2]
        
        if expected_crc != actual_crc:
            print(f"CRC校验失败: 预期={expected_crc:04X}, 实际={actual_crc:04X}")
            # 暂时忽略CRC校验失败，继续解析数据
        
        # 转换为实际值（寄存器值 ÷ 10）
        acceleration = acceleration_raw / 10.0
        
        print(f"解析成功: 加速度={acceleration}m/s²")
        return {
            "acceleration": acceleration
        }
    except Exception as e:
        print(f"解析加速度应答帧失败: {e}")
        return None


def calculate_amplitude(waveform_data):
    """根据波形数据计算振幅"""
    import math
    
    if not waveform_data:
        return 0.0
    
    # 计算峰值（Peak）
    peak = max(abs(value) for value in waveform_data)
    
    # 计算均方根值（RMS）
    rms = math.sqrt(sum(value**2 for value in waveform_data) / len(waveform_data))
    
    return {
        "peak": peak,
        "rms": rms
    }


def parse_modbus_response(response):
    """解析Modbus-RTU应答帧"""
    try:
        if len(response) < 9:
            print(f"应答帧长度不足: {len(response)}")
            return None
        
        # 检查地址码和功能码（只处理地址码为01的应答帧）
        if response[0] != Config.MODBUS_SLAVE_ID or response[1] != Config.MODBUS_FUNCTION_CODE:
            print(f"忽略非01地址码的应答帧: 地址码={response[0]:02X}, 功能码={response[1]:02X}")
            return None
        
        # 检查有效字节数
        if response[2] != 0x04:
            print(f"有效字节数错误: {response[2]:02X}")
            return None
        
        # 提取湿度值（前2字节）和温度值（后2字节）
        humidity = (response[3] << 8) | response[4]
        temperature_raw = (response[5] << 8) | response[6]
        
        # 计算CRC校验
        crc_data = response[:6]
        expected_crc = calculate_crc(crc_data)
        actual_crc = (response[8] << 8) | response[7]
        
        if expected_crc != actual_crc:
            print(f"CRC校验失败: 预期={expected_crc:04X}, 实际={actual_crc:04X}")
            # 暂时忽略CRC校验失败，继续解析数据
            # return None
        
        # 转换为实际值
        # 湿度计算：湿度值除以10
        humidity = humidity / 10.0
        
        # 温度计算：处理补码形式（当温度低于0℃时）
        if temperature_raw > 32767:
            # 补码转换
            temperature = (temperature_raw - 65536) / 10.0
        else:
            temperature = temperature_raw / 10.0
        
        # 验证数据范围
        if humidity < Config.HUMIDITY_RANGE[0] or humidity > Config.HUMIDITY_RANGE[1]:
            print(f"湿度值超出范围: {humidity}")
            return None
        if temperature < Config.TEMPERATURE_RANGE[0] or temperature > Config.TEMPERATURE_RANGE[1]:
            print(f"温度值超出范围: {temperature}")
            return None
        
        print(f"解析成功: 温度={temperature}°C, 湿度={humidity}%")
        return {
            "temperature": temperature,
            "humidity": humidity
        }
    except Exception as e:
        print(f"解析应答帧失败: {e}")
        return None


def parse_vibration_response(modbus_response):
    """解析温振监控的Modbus-RTU应答帧"""
    try:
        # 首先检查是否包含LoRa目标地址前缀
        if len(modbus_response) > 4 and modbus_response[0] == 0x00 and modbus_response[1] == 0x03 and modbus_response[2] == 0x01 and modbus_response[3] == 0x03:
            # 包含LoRa目标地址前缀 (00 03 01 03)
            print(f"检测到LoRa目标地址前缀，跳过前4字节")
            # 跳过前4字节：00 03 01 03
            actual_data = modbus_response[4:]
            print(f"跳过前缀后的长度: {len(actual_data)}")
        elif len(modbus_response) > 2 and modbus_response[0] == 0x00 and modbus_response[1] == 0x03:
            # 包含LoRa目标地址前缀 (00 03)
            print(f"检测到LoRa目标地址前缀，跳过前2字节")
            # 跳过前2字节：00 03
            actual_data = modbus_response[2:]
            print(f"跳过前缀后的长度: {len(actual_data)}")
        else:
            actual_data = modbus_response
        
        if len(actual_data) < 5:
            print(f"应答帧长度不足: {len(actual_data)}")
            return None
        
        # 直接从实际数据中提取信息
        print(f"开始解析温振数据...")
        
        # 提取温度值（偏移1-2字节，大端序）
        temperature_raw = (actual_data[1] << 8) | actual_data[2]
        print(f"温度原始值: {temperature_raw} (0x{temperature_raw:04X})")
        
        # 提取速度值（偏移3-8字节）
        velocity_x_raw = (actual_data[3] << 8) | actual_data[4]
        velocity_y_raw = (actual_data[5] << 8) | actual_data[6]
        velocity_z_raw = (actual_data[7] << 8) | actual_data[8]
        
        # 提取位移值（偏移9-14字节）
        displacement_x_raw = (actual_data[9] << 8) | actual_data[10]
        displacement_y_raw = (actual_data[11] << 8) | actual_data[12]
        displacement_z_raw = (actual_data[13] << 8) | actual_data[14]
        
        # 提取加速度值（偏移15-20字节）
        acceleration_x_raw = (actual_data[15] << 8) | actual_data[16]
        acceleration_y_raw = (actual_data[17] << 8) | actual_data[18]
        
        # 提取版本号（偏移19-20字节）
        version = (actual_data[19] << 8) | actual_data[20]
        print(f"版本号原始值: {version} (0x{version:04X})")
        
        # 提取加速度Z值（偏移21-22字节）
        acceleration_z_raw = (actual_data[21] << 8) | actual_data[22]
        
        # 提取频率值（从偏移23开始，假设是float32类型）
        frequency_x = bytes_to_float(actual_data[23:27])
        frequency_y = bytes_to_float(actual_data[27:31])
        frequency_z = bytes_to_float(actual_data[31:35])
        
        # 转换为实际值
        # 温度计算：处理补码形式（当温度低于0℃时）
        if temperature_raw > 32767:
            temperature = (temperature_raw - 65536) / 10.0
        else:
            temperature = temperature_raw / 10.0
        
        # 速度、加速度、位移计算
        velocity_x = velocity_x_raw / 10.0
        velocity_y = velocity_y_raw / 10.0
        velocity_z = velocity_z_raw / 10.0
        
        acceleration_x = acceleration_x_raw / 10.0
        acceleration_y = acceleration_y_raw / 10.0
        acceleration_z = acceleration_z_raw / 10.0
        
        displacement_x = displacement_x_raw / 10.0
        displacement_y = displacement_y_raw / 10.0
        displacement_z = displacement_z_raw / 10.0
        
        # 计算合成值
        import math
        resultant_velocity = math.sqrt(velocity_x**2 + velocity_y**2 + velocity_z**2)
        resultant_acceleration = math.sqrt(acceleration_x**2 + acceleration_y**2 + acceleration_z**2)
        resultant_displacement = math.sqrt(displacement_x**2 + displacement_y**2 + displacement_z**2)
        
        # 确定状态等级
        status_text = "良好"
        if resultant_velocity > 1.8:
            status_text = "严重"
        elif resultant_velocity > 1.12:
            status_text = "警告"
        elif resultant_velocity > 0.71:
            status_text = "注意"
        
        print(f"解析成功: 温度={temperature}°C, 频率X={frequency_x}Hz, 速度X={velocity_x}mm/s, 加速度X={acceleration_x}m/s², 位移X={displacement_x}μm")
        return {
            "temperature": temperature,
            "frequency_x": frequency_x,
            "frequency_y": frequency_y,
            "frequency_z": frequency_z,
            "velocity_x": velocity_x,
            "velocity_y": velocity_y,
            "velocity_z": velocity_z,
            "acceleration_x": acceleration_x,
            "acceleration_y": acceleration_y,
            "acceleration_z": acceleration_z,
            "displacement_x": displacement_x,
            "displacement_y": displacement_y,
            "displacement_z": displacement_z,
            "resultant_velocity": resultant_velocity,
            "resultant_acceleration": resultant_acceleration,
            "resultant_displacement": resultant_displacement,
            "status": status_text,
            "version": version,
            "timestamp": time.time()
        }
    except Exception as e:
        print(f"解析温振应答帧失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def parse_vibration_sensor_response(response_data):
    """解析温振传感器的Modbus-RTU应答帧（单帧包含所有数据）
    
    应答帧格式（38个寄存器，0000-0025）：
    - 地址码 (1字节)
    - 功能码 (1字节)
    - 字节数 (1字节) = 0x4C (76字节)
    - 数据 (76字节，38个寄存器)
    - CRC校验 (2字节)
    
    寄存器映射：
    - 0000: 温度 (扩大10倍)
    - 0001: 速度X (扩大10倍)
    - 0002: 速度Y (扩大10倍)
    - 0003: 速度Z (扩大10倍)
    - 0004: 位移X (扩大10倍)
    - 0005: 位移Y (扩大10倍)
    - 0006: 位移Z (扩大10倍)
    - 0007-0008: 保留
    - 0009: 版本号
    - 000A: 加速度X (扩大10倍)
    - 000B: 加速度Y (扩大10倍)
    - 000C: 加速度Z (扩大10倍)
    - 000D-0020: 保留
    - 0021: X轴振动频率 (float)
    - 0022: 保留
    - 0023: Y轴振动频率 (float)
    - 0024: 保留
    - 0025: Z轴振动频率 (float)
    """
    try:
        import struct
        
        # 检查是否包含LoRa目标地址前缀
        modbus_data = response_data
        if len(response_data) >= 83 and response_data[0] == 0x00 and response_data[1] == 0x03:
            # 包含LoRa目标地址前缀 0003
            modbus_data = response_data[2:]
            print(f"检测到LoRa目标地址前缀: {response_data[0]:02X} {response_data[1]:02X}")
        
        # 检查应答帧格式
        if len(modbus_data) >= 81:
            # 标准Modbus-RTU应答帧：地址码 + 功能码 + 数据长度 + 数据 + CRC
            address = modbus_data[0]
            function_code = modbus_data[1]
            data_length = modbus_data[2]
            
            print(f"应答帧信息:")
            print(f"  地址码: {address:02X}H")
            print(f"  功能码: {function_code:02X}H")
            print(f"  数据长度: {data_length} 字节")
            
            if function_code == 0x03 and data_length == 0x4C:
                # 温振应答帧（76字节数据，38个寄存器）
                # 数据区从偏移3开始
                data_area = modbus_data[3:3+data_length]
                
                # 按照偏移位置解析（相对于数据区）
                temperature_raw = (data_area[0] << 8) | data_area[1]
                velocity_x = (data_area[2] << 8) | data_area[3]
                velocity_y = (data_area[4] << 8) | data_area[5]
                velocity_z = (data_area[6] << 8) | data_area[7]
                displacement_x = (data_area[8] << 8) | data_area[9]
                displacement_y = (data_area[10] << 8) | data_area[11]
                displacement_z = (data_area[12] << 8) | data_area[13]
                version = (data_area[18] << 8) | data_area[19]
                acceleration_x = (data_area[20] << 8) | data_area[21]
                acceleration_y = (data_area[22] << 8) | data_area[23]
                acceleration_z = (data_area[24] << 8) | data_area[25]
                
                # 频率X轴：偏移66-69 (float32，相对于数据区)
                if len(data_area) >= 70:
                    freq_x_bytes = data_area[66:70]
                    freq_x = struct.unpack('>f', freq_x_bytes)[0]
                else:
                    freq_x = 0.0
                
                # 频率Y轴：偏移72-75 (float32，相对于数据区)
                if len(data_area) >= 76:
                    freq_y_bytes = data_area[72:76]
                    freq_y = struct.unpack('>f', freq_y_bytes)[0]
                else:
                    freq_y = 0.0
                
                # 频率Z轴：偏移78-81 (float32，相对于数据区)
                if len(data_area) >= 82:
                    freq_z_bytes = data_area[78:82]
                    freq_z = struct.unpack('>f', freq_z_bytes)[0]
                else:
                    freq_z = 0.0
                
                # 温度数据转换（有符号16位，除以10）
                if temperature_raw > 32767:
                    temperature = (temperature_raw - 65536) / 10.0
                else:
                    temperature = temperature_raw / 10.0
                
                # 振动速度转换（除以10）
                velocity_x_value = velocity_x / 10.0
                velocity_y_value = velocity_y / 10.0
                velocity_z_value = velocity_z / 10.0
                
                # 振动位移转换（除以10）
                displacement_x_value = displacement_x / 10.0
                displacement_y_value = displacement_y / 10.0
                displacement_z_value = displacement_z / 10.0
                
                # 振动加速度转换（除以10）
                acceleration_x_value = acceleration_x / 10.0
                acceleration_y_value = acceleration_y / 10.0
                acceleration_z_value = acceleration_z / 10.0
                
                # 计算合成速度值
                import math
                vibration = math.sqrt(velocity_x_value**2 + velocity_y_value**2 + velocity_z_value**2)
                
                # 验证CRC校验
                if len(modbus_data) >= 81:
                    # CRC16校验码：小端序（低字节在前）
                    received_crc = (modbus_data[80] << 8) | modbus_data[79]
                    calculated_crc = calculate_crc(modbus_data[:79])
                    
                    crc_valid = received_crc == calculated_crc
                    print(f"  CRC校验: {'通过' if crc_valid else '失败'}")
                    print(f"  接收CRC: {received_crc:04X}H")
                    print(f"  计算CRC: {calculated_crc:04X}H")
                
                print(f"解析成功: 温度={temperature:.1f}°C, 振动={vibration:.3f}mm/s")
                return {
                    "temperature": temperature,
                    "vibration": vibration,
                    "velocity_x": velocity_x_value,
                    "velocity_y": velocity_y_value,
                    "velocity_z": velocity_z_value,
                    "displacement_x": displacement_x_value,
                    "displacement_y": displacement_y_value,
                    "displacement_z": displacement_z_value,
                    "acceleration_x": acceleration_x_value,
                    "acceleration_y": acceleration_y_value,
                    "acceleration_z": acceleration_z_value,
                    "version": version,
                    "freq_x": freq_x,
                    "freq_y": freq_y,
                    "freq_z": freq_z,
                    "temperature_raw": temperature_raw,
                    "crc_valid": crc_valid if len(modbus_data) >= 81 else None
                }
            else:
                print(f"  功能码或数据长度不匹配")
                return None
        else:
            print(f"  应答帧长度不足: {len(modbus_data)} 字节")
            return None
    except Exception as e:
        print(f"解析错误: {e}")
        import traceback
        traceback.print_exc()
        return None


def parse_air_quality_response(response):
    """解析空气质量监控的Modbus-RTU应答帧"""
    try:
        if len(response) < 13:  # 空气质量数据需要更多字节
            print(f"应答帧长度不足: {len(response)}")
            return None
        
        # 检查地址码和功能码
        if response[0] != Config.MODBUS_SLAVE_ID or response[1] != Config.MODBUS_FUNCTION_CODE:
            print(f"忽略非01地址码的应答帧: 地址码={response[0]:02X}, 功能码={response[1]:02X}")
            return None
        
        # 检查有效字节数
        if response[2] != 0x08:  # 8字节有效数据
            print(f"有效字节数错误: {response[2]:02X}")
            return None
        
        # 提取空气质量数据
        aqi = (response[3] << 8) | response[4]
        pm25 = (response[5] << 8) | response[6]
        pm10 = (response[7] << 8) | response[8]
        co2 = (response[9] << 8) | response[10]
        voc = (response[11] << 8) | response[12]
        
        # 计算CRC校验
        crc_data = response[:12]
        expected_crc = calculate_crc(crc_data)
        actual_crc = (response[14] << 8) | response[13]
        
        if expected_crc != actual_crc:
            print(f"CRC校验失败: 预期={expected_crc:04X}, 实际={actual_crc:04X}")
            # 暂时忽略CRC校验失败，继续解析数据
        
        # 转换为实际值
        pm25 = pm25 / 10.0
        pm10 = pm10 / 10.0
        co2 = co2 / 10.0
        voc = voc / 10.0
        
        # 验证数据范围
        if aqi < 0 or aqi > 500:
            print(f"AQI值超出范围: {aqi}")
            return None
        if pm25 < 0 or pm25 > 500:
            print(f"PM2.5值超出范围: {pm25}")
            return None
        if pm10 < 0 or pm10 > 600:
            print(f"PM10值超出范围: {pm10}")
            return None
        if co2 < 0 or co2 > 5000:
            print(f"CO2值超出范围: {co2}")
            return None
        if voc < 0 or voc > 1000:
            print(f"VOC值超出范围: {voc}")
            return None
        
        print(f"解析成功: AQI={aqi}, PM2.5={pm25}, PM10={pm10}, CO2={co2}, VOC={voc}")
        return {
            "aqi": aqi,
            "pm25": pm25,
            "pm10": pm10,
            "co2": co2,
            "voc": voc
        }
    except Exception as e:
        print(f"解析应答帧失败: {e}")
        return None


def parse_light_gas_response(response):
    """解析光照气体监控的Modbus-RTU应答帧"""
    try:
        # 检查是否包含LoRa目标地址前缀
        # 假设LoRa目标地址前缀为2字节
        modbus_start = 0
        if len(response) >= 19 and response[0] not in [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10]:
            # 可能包含LoRa目标地址前缀，跳过前2字节
            modbus_start = 2
            print(f"检测到可能的LoRa目标地址前缀，从位置{modbus_start}开始解析")
        
        # 完整应答帧长度应为17字节（包括校验码），如果包含LoRa前缀则为19字节
        if len(response) < (17 + modbus_start):
            print(f"应答帧长度不足: {len(response)}，预期至少{17 + modbus_start}字节")
            return None
        
        # 检查地址码和功能码
        if response[modbus_start] != Config.MODBUS_SLAVE_ID or response[modbus_start + 1] != Config.MODBUS_FUNCTION_CODE:
            print(f"忽略非01地址码的应答帧: 地址码={response[modbus_start]:02X}, 功能码={response[modbus_start + 1]:02X}")
            return None
        
        # 检查有效字节数
        if response[modbus_start + 2] != 0x10:  # 16字节有效数据
            print(f"有效字节数错误: {response[modbus_start + 2]:02X}")
            return None
        
        # 提取数据（按照协议规范的顺序）
        # 打印应答帧内容，以便调试
        print(f"【解析】应答帧内容: {[f'{b:02X}' for b in response]}")
        print(f"【解析】modbus_start: {modbus_start}")
        
        status = (response[modbus_start + 3] << 8) | response[modbus_start + 4]      # 状态：0000H
        print(f"【解析】状态: {status:04X}")
        
        temperature_raw = (response[modbus_start + 5] << 8) | response[modbus_start + 6]  # 温度：0001H
        print(f"【解析】温度原始值: {temperature_raw:04X}")
        
        humidity = (response[modbus_start + 7] << 8) | response[modbus_start + 8]       # 湿度：0002H（uint16）
        print(f"【解析】湿度: {humidity}")
        
        co2 = (response[modbus_start + 9] << 8) | response[modbus_start + 10]          # CO2：0003H
        print(f"【解析】CO2: {co2}")
        
        # 气压：10-13（0001 03FEH），前四位作为高位，后四位作为低位
        pressure_high = (response[modbus_start + 11] << 8) | response[modbus_start + 12]  # 气压高位：00 01
        pressure_low = (response[modbus_start + 13] << 8) | response[modbus_start + 14]   # 气压低位：03 FE
        pressure = (pressure_high << 16) | pressure_low      # 组合成完整气压值（单位：Pa）
        print(f"【解析】气压: {pressure} Pa = {pressure/1000:.2f} kPa")
        
        # 光照：14-17（0000 01A7H），使用全部4字节中的有效部分
        # 修正光照强度的偏移量，确保正确提取数据
        light_high = (response[modbus_start + 15] << 8) | response[modbus_start + 16]  # 光照高位
        light_low = (response[modbus_start + 17] << 8) | response[modbus_start + 18]   # 光照低位
        light = (light_high << 16) | light_low              # 组合成完整光照值（单位：Lux）
        print(f"【解析】光照: {light} Lux")
        
        # 计算CRC校验（使用除校验码外的所有数据）
        crc_data = response[modbus_start:-2]
        expected_crc = calculate_crc(crc_data)
        actual_crc = (response[-1] << 8) | response[-2]
        
        if expected_crc != actual_crc:
            print(f"CRC校验失败: 预期={expected_crc:04X}, 实际={actual_crc:04X}")
            # 暂时忽略CRC校验失败，继续解析数据
        
        # 转换为实际值
        # 温度计算：处理补码形式（当温度低于0℃时）
        if temperature_raw > 32767:
            # 补码转换
            temperature = (temperature_raw - 65536) / 10.0
        else:
            temperature = temperature_raw / 10.0
        
        # 湿度计算：直接使用值（已经是百分比）
        humidity = humidity
        
        # CO2计算：直接使用值（单位ppm）
        co2 = co2
        
        # 气压计算：从Pa转换为kPa（除以1000）
        pressure = pressure / 1000.0
        
        # 光照强度计算：直接使用值（单位Lux）
        light = light
        
        # 验证数据范围
        if temperature < Config.TEMPERATURE_RANGE[0] or temperature > Config.TEMPERATURE_RANGE[1]:
            print(f"温度值超出范围: {temperature}")
            # 暂时不返回None，允许超出范围的值通过
            # return None
        if humidity < 0 or humidity > 100:
            print(f"湿度值超出范围: {humidity}")
            # 暂时不返回None，允许超出范围的值通过
            # return None
        if co2 < 0 or co2 > 5000:
            print(f"CO2值超出范围: {co2}")
            # 暂时不返回None，允许超出范围的值通过
            # return None
        if pressure < 0 or pressure > 1100:
            print(f"气压值超出范围: {pressure}")
            # 暂时不返回None，允许超出范围的值通过
            # return None
        if light < 0 or light > 100000:
            print(f"光照强度值超出范围: {light}")
            # 暂时不返回None，允许超出范围的值通过
            # return None
        
        print(f"解析成功: 状态={status:04X}, 温度={temperature}°C, 湿度={humidity}%, CO2={co2}ppm, 气压={pressure}kPa, 光照={light}Lux")
        return {
            "status": status,
            "temperature": temperature,
            "humidity": humidity,
            "co2": co2,
            "pressure": pressure,
            "light": light
        }
    except Exception as e:
        print(f"解析应答帧失败: {e}")
        return None


def validate_modbus_frame(frame):
    """验证Modbus帧的有效性"""
    if len(frame) < 8:  # 最小Modbus帧长度
        return False, "帧长度不足"
    
    # 检查CRC校验
    crc_data = frame[:-2]
    expected_crc = calculate_crc(crc_data)
    actual_crc = (frame[-1] << 8) | frame[-2]
    
    if expected_crc != actual_crc:
        return False, "CRC校验失败"
    
    return True, "帧有效"
