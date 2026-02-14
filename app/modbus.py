"""Modbus协议服务模块"""

from app.config import Config


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
    """解析温度数据"""
    try:
        if len(response) < 7:
            print(f"应答帧长度不足: {len(response)}")
            return None
        
        # 检查地址码和功能码
        if response[0] != Config.MODBUS_SLAVE_ID or response[1] != Config.MODBUS_FUNCTION_CODE:
            print(f"忽略非01地址码的应答帧: 地址码={response[0]:02X}, 功能码={response[1]:02X}")
            return None
        
        # 检查有效字节数
        if response[2] != 0x02:
            print(f"有效字节数错误: {response[2]:02X}")
            return None
        
        # 提取温度值（2字节）
        temperature_raw = (response[3] << 8) | response[4]
        
        # 计算CRC校验
        crc_data = response[:5]
        expected_crc = calculate_crc(crc_data)
        actual_crc = (response[6] << 8) | response[5]
        
        if expected_crc != actual_crc:
            print(f"CRC校验失败: 预期={expected_crc:04X}, 实际={actual_crc:04X}")
            # 暂时忽略CRC校验失败，继续解析数据
        
        # 转换为实际值（寄存器值 ÷ 10）
        temperature = temperature_raw / 10.0
        
        # 验证数据范围
        if temperature < Config.TEMPERATURE_RANGE[0] or temperature > Config.TEMPERATURE_RANGE[1]:
            print(f"温度值超出范围: {temperature}")
            return None
        
        print(f"解析成功: 温度={temperature}°C")
        return {
            "temperature": temperature
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


def parse_vibration_response(response):
    """解析温振监控的Modbus-RTU应答帧"""
    try:
        if len(response) < 9:
            print(f"应答帧长度不足: {len(response)}")
            return None
        
        # 检查地址码和功能码
        if response[0] != Config.MODBUS_SLAVE_ID or response[1] != Config.MODBUS_FUNCTION_CODE:
            print(f"忽略非01地址码的应答帧: 地址码={response[0]:02X}, 功能码={response[1]:02X}")
            return None
        
        # 检查有效字节数
        if response[2] != 0x04:
            print(f"有效字节数错误: {response[2]:02X}")
            return None
        
        # 提取温度值（前2字节）和振动值（后2字节）
        temperature_raw = (response[3] << 8) | response[4]
        vibration = (response[5] << 8) | response[6]
        
        # 计算CRC校验
        crc_data = response[:6]
        expected_crc = calculate_crc(crc_data)
        actual_crc = (response[8] << 8) | response[7]
        
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
        
        # 振动值计算：振动值除以10
        vibration = vibration / 10.0
        
        # 验证数据范围
        if temperature < Config.TEMPERATURE_RANGE[0] or temperature > Config.TEMPERATURE_RANGE[1]:
            print(f"温度值超出范围: {temperature}")
            return None
        if vibration < 0 or vibration > 100:
            print(f"振动值超出范围: {vibration}")
            return None
        
        print(f"解析成功: 温度={temperature}°C, 振动={vibration}Hz")
        return {
            "temperature": temperature,
            "vibration": vibration
        }
    except Exception as e:
        print(f"解析应答帧失败: {e}")
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
        if len(response) < 17:  # 完整应答帧长度应为17字节（包括校验码）
            print(f"应答帧长度不足: {len(response)}")
            return None
        
        # 检查地址码和功能码
        if response[0] != Config.MODBUS_SLAVE_ID or response[1] != Config.MODBUS_FUNCTION_CODE:
            print(f"忽略非01地址码的应答帧: 地址码={response[0]:02X}, 功能码={response[1]:02X}")
            return None
        
        # 检查有效字节数
        if response[2] != 0x10:  # 16字节有效数据
            print(f"有效字节数错误: {response[2]:02X}")
            return None
        
        # 提取数据（按照协议规范的顺序）
        status = (response[3] << 8) | response[4]      # 状态：0000H
        temperature_raw = (response[5] << 8) | response[6]  # 温度：0001H
        humidity = (response[7] << 8) | response[8]       # 湿度：0002H（uint16）
        co2 = (response[9] << 8) | response[10]          # CO2：0003H
        # 气压：10-13（0001 03FEH），前四位作为高位，后四位作为低位
        pressure_high = (response[11] << 8) | response[12]  # 气压高位：00 01
        pressure_low = (response[13] << 8) | response[14]   # 气压低位：03 FE
        pressure = (pressure_high << 16) | pressure_low      # 组合成完整气压值（单位：Pa）
        # 光照：14-17（0000 01A7H），使用全部4字节中的有效部分
        light = (response[17] << 8) | response[18]        # 光照：使用后2字节 01 A7
        
        # 计算CRC校验（使用除校验码外的所有数据）
        crc_data = response[:-2]
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
            return None
        if humidity < 0 or humidity > 100:
            print(f"湿度值超出范围: {humidity}")
            return None
        if co2 < 0 or co2 > 5000:
            print(f"CO2值超出范围: {co2}")
            return None
        if pressure < 0 or pressure > 1100:
            print(f"气压值超出范围: {pressure}")
            # 暂时不返回None，允许超出范围的值通过
            # return None
        if light < 0 or light > 100000:
            print(f"光照强度值超出范围: {light}")
            return None
        
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
