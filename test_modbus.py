"""测试Modbus应答帧解析"""

from app.modbus import parse_light_gas_response

# 用户提供的完整应答帧示例
# 01 03 0C 00 00 00 EC 00 19 03 00 03 FE 01 A7 A6 D8
test_response = bytearray([
    0x01,  # 地址码
    0x03,  # 功能码
    0x0C,  # 字节数
    0x00, 0x00,  # 状态
    0x00, 0xEC,  # 温度
    0x00, 0x19,  # 湿度
    0x03, 0x00,  # CO2
    0x03, 0xFE,  # 气压
    0x01, 0xA7,  # 光照
    0xA6, 0xD8   # 校验码
])

print("测试应答帧解析...")
print(f"测试应答帧长度: {len(test_response)}")
print(f"测试应答帧内容: {[f'{b:02X}' for b in test_response]}")

result = parse_light_gas_response(test_response)

if result:
    print("\n解析成功！")
    print(f"状态: 0x{result['status']:04X}")
    print(f"温度: {result['temperature']} °C")
    print(f"湿度: {result['humidity']} %")
    print(f"CO2浓度: {result['co2']} ppm")
    print(f"大气压强: {result['pressure']} hPa")
    print(f"光照强度: {result['light']} Lux")
    
    # 验证解析结果是否符合预期
    expected_temperature = 23.6  # 0x00EC = 236, 236/10 = 23.6
    expected_humidity = 25      # 0x0019 = 25
    expected_co2 = 768          # 0x0300 = 768
    expected_pressure = 1022     # 0x03FE = 1022
    expected_light = 423         # 0x01A7 = 423
    
    print("\n验证结果:")
    print(f"温度验证: {'通过' if abs(result['temperature'] - expected_temperature) < 0.1 else '失败'}")
    print(f"湿度验证: {'通过' if result['humidity'] == expected_humidity else '失败'}")
    print(f"CO2验证: {'通过' if result['co2'] == expected_co2 else '失败'}")
    print(f"气压验证: {'通过' if result['pressure'] == expected_pressure else '失败'}")
    print(f"光照验证: {'通过' if result['light'] == expected_light else '失败'}")
else:
    print("\n解析失败！")
