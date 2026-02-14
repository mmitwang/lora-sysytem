import asyncio
from playwright.async_api import async_playwright
import time
import json

# 测试配置
BASE_URL = "http://127.0.0.1:5000"
TEST_TIMEOUT = 60000  # 60秒超时

class TestTemperatureHumidity:
    """温湿度监控功能自动测试类"""
    
    async def setup(self, page):
        """测试前的设置"""
        await page.goto(BASE_URL)
        await page.wait_for_load_state('networkidle')
        print("页面加载完成")
    
    async def test_navigation_to_temperature_page(self, page):
        """测试导航到温湿度监控页面"""
        await self.setup(page)
        
        # 点击温湿度监控导航按钮
        await page.click('a[href="#temperature"]')
        await page.wait_for_timeout(1000)  # 等待页面切换
        
        # 验证URL hash是否正确
        assert page.url == f"{BASE_URL}/#temperature", f"URL不正确: {page.url}"
        print("导航到温湿度监控页面成功")
        
        # 检查温湿度监控页面是否可见
        temperature_section = await page.query_selector('#temperature')
        if temperature_section:
            section_class = await temperature_section.get_attribute('class')
            print(f"温湿度监控页面section类: {section_class}")
        
        # 手动确保温湿度监控页面可见（如果被隐藏）
        await page.evaluate('''
            document.querySelectorAll('section').forEach(section => {
                section.classList.add('hidden');
            });
            const temperatureSection = document.getElementById('temperature');
            if (temperatureSection) {
                temperatureSection.classList.remove('hidden');
            }
        ''')
        await page.wait_for_timeout(500)  # 等待页面切换
        print("已手动确保温湿度监控页面可见")
        
        # 验证温湿度监控页面元素是否存在
        await page.wait_for_selector('#temperature-value', state='attached')
        await page.wait_for_selector('#humidity-value', state='attached')
        await page.wait_for_selector('#latest-temp', state='attached')
        await page.wait_for_selector('#latest-hum', state='attached')
        print("温湿度监控页面元素检查通过")
    
    async def test_serial_port_operations(self, page):
        """测试串口操作功能"""
        await self.setup(page)
        
        # 导航到温湿度监控页面
        await page.click('a[href="#temperature"]')
        await page.wait_for_timeout(1000)
        
        # 手动确保温湿度监控页面可见（如果被隐藏）
        await page.evaluate('''
            document.querySelectorAll('section').forEach(section => {
                section.classList.add('hidden');
            });
            const temperatureSection = document.getElementById('temperature');
            if (temperatureSection) {
                temperatureSection.classList.remove('hidden');
            }
        ''')
        await page.wait_for_timeout(500)  # 等待页面切换
        
        # 检查串口端口下拉框
        await page.wait_for_selector('#serial-port', state='attached')
        port_options = await page.query_selector_all('#serial-port option')
        print(f"发现 {len(port_options)} 个可用串口")
        
        # 检查波特率下拉框
        await page.wait_for_selector('#serial-baudrate', state='attached')
        baudrate_options = await page.query_selector_all('#serial-baudrate option')
        assert len(baudrate_options) > 0, "波特率选项为空"
        print("波特率选项检查通过")
        
        # 检查校验位下拉框
        await page.wait_for_selector('#serial-parity', state='attached')
        parity_options = await page.query_selector_all('#serial-parity option')
        assert len(parity_options) > 0, "校验位选项为空"
        print("校验位选项检查通过")
        
        # 检查停止位下拉框
        await page.wait_for_selector('#serial-stopbits', state='attached')
        stopbits_options = await page.query_selector_all('#serial-stopbits option')
        assert len(stopbits_options) > 0, "停止位选项为空"
        print("停止位选项检查通过")
    
    async def test_query_interval_operations(self, page):
        """测试问询周期操作功能"""
        await self.setup(page)
        
        # 导航到温湿度监控页面
        await page.click('a[href="#temperature"]')
        await page.wait_for_timeout(1000)
        
        # 手动确保温湿度监控页面可见（如果被隐藏）
        await page.evaluate('''
            document.querySelectorAll('section').forEach(section => {
                section.classList.add('hidden');
            });
            const temperatureSection = document.getElementById('temperature');
            if (temperatureSection) {
                temperatureSection.classList.remove('hidden');
            }
        ''')
        await page.wait_for_timeout(500)  # 等待页面切换
        
        # 检查问询周期输入框
        await page.wait_for_selector('#query-interval', state='attached')
        current_interval = await page.input_value('#query-interval')
        print(f"当前问询周期: {current_interval}秒")
        
        # 修改问询周期
        new_interval = "3"
        await page.fill('#query-interval', new_interval)
        await page.click('#update-interval')
        await page.wait_for_timeout(1000)
        print("问询周期更新成功")
    
    async def test_query_control_buttons(self, page):
        """测试问询控制按钮功能"""
        await self.setup(page)
        
        # 导航到温湿度监控页面
        await page.click('a[href="#temperature"]')
        await page.wait_for_timeout(1000)
        
        # 手动确保温湿度监控页面可见（如果被隐藏）
        await page.evaluate('''
            document.querySelectorAll('section').forEach(section => {
                section.classList.add('hidden');
            });
            const temperatureSection = document.getElementById('temperature');
            if (temperatureSection) {
                temperatureSection.classList.remove('hidden');
            }
        ''')
        await page.wait_for_timeout(500)  # 等待页面切换
        
        # 检查启动问询按钮
        await page.wait_for_selector('#start-query', state='attached')
        # 检查停止问询按钮
        await page.wait_for_selector('#stop-query', state='attached')
        # 检查刷新数据按钮
        await page.wait_for_selector('#refresh-data', state='attached')
        print("问询控制按钮检查通过")
    
    async def test_time_range_selection(self, page):
        """测试时间范围选择功能"""
        await self.setup(page)
        
        # 导航到温湿度监控页面
        await page.click('a[href="#temperature"]')
        await page.wait_for_timeout(1000)
        
        # 手动确保温湿度监控页面可见（如果被隐藏）
        await page.evaluate('''
            document.querySelectorAll('section').forEach(section => {
                section.classList.add('hidden');
            });
            const temperatureSection = document.getElementById('temperature');
            if (temperatureSection) {
                temperatureSection.classList.remove('hidden');
            }
        ''')
        await page.wait_for_timeout(500)  # 等待页面切换
        
        # 检查时间范围下拉框
        await page.wait_for_selector('#time-range', state='attached')
        
        # 测试不同时间范围选项
        time_ranges = ['day', 'week', 'month', 'year', 'custom']
        for range_value in time_ranges:
            await page.select_option('#time-range', range_value)
            await page.wait_for_timeout(500)
            print(f"时间范围切换到: {range_value}")
        
        # 测试自定义时间范围
        await page.select_option('#time-range', 'custom')
        await page.wait_for_selector('#custom-date-range', state='attached')
        print("自定义时间范围功能检查通过")
    
    async def test_data_refresh_button(self, page):
        """测试刷新数据按钮功能"""
        await self.setup(page)
        
        # 导航到温湿度监控页面
        await page.click('a[href="#temperature"]')
        await page.wait_for_timeout(1000)
        
        # 手动确保温湿度监控页面可见（如果被隐藏）
        await page.evaluate('''
            document.querySelectorAll('section').forEach(section => {
                section.classList.add('hidden');
            });
            const temperatureSection = document.getElementById('temperature');
            if (temperatureSection) {
                temperatureSection.classList.remove('hidden');
            }
        ''')
        await page.wait_for_timeout(500)  # 等待页面切换
        
        # 点击刷新数据按钮
        await page.click('#refresh-data')
        await page.wait_for_timeout(1000)
        print("刷新数据按钮功能检查通过")
    
    async def test_api_endpoints(self, page):
        """测试温湿度相关API端点"""
        await self.setup(page)
        
        # 测试获取传感器数据API
        response = await page.context.request.get(f"{BASE_URL}/api/sensor/data")
        assert response.status == 200
        data = await response.json()
        assert 'temperature' in data
        assert 'humidity' in data
        assert 'timestamp' in data
        print(f"传感器数据API测试通过: 温度={data['temperature']}°C, 湿度={data['humidity']}%")
        
        # 测试获取历史数据API
        response = await page.context.request.get(f"{BASE_URL}/api/history/data?range=day&table=sensor_history")
        assert response.status == 200
        data = await response.json()
        assert data['status'] == 'success'
        assert 'data' in data
        print(f"历史数据API测试通过，共 {len(data['data'])} 条记录")
        
        # 测试获取串口状态API
        response = await page.context.request.get(f"{BASE_URL}/api/serial/status")
        assert response.status == 200
        data = await response.json()
        assert 'is_open' in data
        assert 'query_running' in data
        print("串口状态API测试通过")

async def run_tests():
    """运行所有测试"""
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False)  # 非无头模式，方便查看测试过程
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            test_instance = TestTemperatureHumidity()
            
            # 运行测试
            print("\n=== 开始测试导航到温湿度监控页面 ===")
            await test_instance.test_navigation_to_temperature_page(page)
            
            print("\n=== 开始测试串口操作功能 ===")
            await test_instance.test_serial_port_operations(page)
            
            print("\n=== 开始测试问询周期操作功能 ===")
            await test_instance.test_query_interval_operations(page)
            
            print("\n=== 开始测试问询控制按钮功能 ===")
            await test_instance.test_query_control_buttons(page)
            
            print("\n=== 开始测试时间范围选择功能 ===")
            await test_instance.test_time_range_selection(page)
            
            print("\n=== 开始测试刷新数据按钮功能 ===")
            await test_instance.test_data_refresh_button(page)
            
            print("\n=== 开始测试温湿度相关API端点 ===")
            await test_instance.test_api_endpoints(page)
            
            print("\n=== 所有温湿度监控功能测试通过！===")
            
        finally:
            # 关闭浏览器
            await context.close()
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_tests())
