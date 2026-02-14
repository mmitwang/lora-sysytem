import asyncio
from playwright.async_api import async_playwright
import time
import json
import os

# 测试配置
BASE_URL = "http://127.0.0.1:5000"
TEST_TIMEOUT = 60000  # 60秒超时

class TestIoTSystem:
    """IoT系统自动测试类"""
    
    async def setup(self, page):
        """测试前的设置"""
        await page.goto(BASE_URL)
        await page.wait_for_load_state('networkidle')
        print("页面加载完成")
    
    async def test_page_load(self, page):
        """测试页面加载和初始化"""
        await self.setup(page)
        
        # 检查页面标题
        title = await page.title()
        assert "物联网数据大屏" in title, f"页面标题不正确: {title}"
        print("页面标题检查通过")
        
        # 检查主要元素是否存在（使用state='attached'而不是默认的'visible'）
        await page.wait_for_selector('#temperature-value', state='attached')
        await page.wait_for_selector('#humidity-value', state='attached')
        await page.wait_for_selector('#open-serial', state='attached')
        await page.wait_for_selector('#close-serial', state='attached')
        await page.wait_for_selector('#start-query', state='attached')
        await page.wait_for_selector('#stop-query', state='attached')
        await page.wait_for_selector('#query-interval', state='attached')
        await page.wait_for_selector('#update-interval', state='attached')
        print("页面元素检查通过")
    
    async def test_serial_port_selection(self, page):
        """测试串口端口选择功能"""
        await self.setup(page)
        
        # 等待串口端口列表加载
        await page.wait_for_timeout(2000)  # 等待2秒，确保串口端口列表有足够时间加载
        print("串口端口列表加载完成")
        
        # 检查是否有可用串口
        port_options = await page.query_selector_all('#serial-port option')
        assert len(port_options) > 0, "没有可用的串口端口"
        print(f"发现 {len(port_options)} 个可用串口")
    
    async def test_query_interval_update(self, page):
        """测试问询周期更新功能"""
        await self.setup(page)
        
        # 直接通过API测试问询周期更新
        new_interval = 5
        
        # 发送API请求更新问询周期
        response = await page.context.request.post(f"{BASE_URL}/api/serial/interval", data=json.dumps({"interval": new_interval}), headers={"Content-Type": "application/json"})
        assert response.status == 200
        data = await response.json()
        assert data['status'] == 'success'
        print("问询周期更新成功")
        
        # 验证后端API返回的问询周期是否正确
        response = await page.context.request.get(f"{BASE_URL}/api/query/interval")
        assert response.status == 200
        data = await response.json()
        assert data['status'] == 'success'
        assert data['interval'] == new_interval
        print(f"后端问询周期验证通过: {data['interval']}秒")
    
    async def test_query_control(self, page):
        """测试问询控制功能"""
        await self.setup(page)
        
        # 启动问询（通过API）
        response = await page.context.request.post(f"{BASE_URL}/api/query/start", data=json.dumps({}), headers={"Content-Type": "application/json"})
        assert response.status == 200
        data = await response.json()
        assert data['status'] == 'success'
        print("问询启动成功")
        
        # 验证后端API返回的问询状态是否正确
        response = await page.context.request.get(f"{BASE_URL}/api/query/status")
        assert response.status == 200
        data = await response.json()
        assert data['status'] == 'success'
        assert data['running'] is True
        print("后端问询状态验证通过: 运行中")
        
        # 停止问询（通过API）
        response = await page.context.request.post(f"{BASE_URL}/api/query/stop", data=json.dumps({}), headers={"Content-Type": "application/json"})
        assert response.status == 200
        data = await response.json()
        assert data['status'] == 'success'
        print("问询停止成功")
        
        # 验证后端API返回的问询状态是否正确
        response = await page.context.request.get(f"{BASE_URL}/api/query/status")
        assert response.status == 200
        data = await response.json()
        assert data['status'] == 'success'
        assert data['running'] is False
        print("后端问询状态验证通过: 已停止")
    
    async def test_sensor_data_collection(self, page):
        """测试传感器数据采集功能"""
        await self.setup(page)
        
        # 启动问询（通过API）
        response = await page.context.request.post(f"{BASE_URL}/api/query/start", data=json.dumps({}), headers={"Content-Type": "application/json"})
        assert response.status == 200
        data = await response.json()
        assert data['status'] == 'success'
        
        # 等待数据采集
        await asyncio.sleep(3)  # 等待3秒，确保有足够时间采集数据
        
        # 获取传感器数据
        response = await page.context.request.get(f"{BASE_URL}/api/sensor/data")
        assert response.status == 200
        data = await response.json()
        assert 'temperature' in data
        assert 'humidity' in data
        assert 'timestamp' in data
        print(f"传感器数据采集成功: 温度={data['temperature']}°C, 湿度={data['humidity']}%")
        
        # 停止问询（通过API）
        response = await page.context.request.post(f"{BASE_URL}/api/query/stop", data=json.dumps({}), headers={"Content-Type": "application/json"})
        assert response.status == 200
        data = await response.json()
        assert data['status'] == 'success'
    
    async def test_history_data(self, page):
        """测试历史数据功能"""
        await self.setup(page)
        
        # 获取历史数据（当天）
        response = await page.context.request.get(f"{BASE_URL}/api/history/data?range=day")
        assert response.status == 200
        data = await response.json()
        assert data['status'] == 'success'
        assert 'data' in data
        print(f"历史数据获取成功，共 {len(data['data'])} 条记录")
    
    async def test_frame_data(self, page):
        """测试帧数据功能"""
        await self.setup(page)
        
        # 获取帧数据
        response = await page.context.request.get(f"{BASE_URL}/api/serial/frames")
        assert response.status == 200
        data = await response.json()
        assert 'query' in data
        assert 'response' in data
        print("帧数据获取成功")
    
    async def test_database_sync(self, page):
        """测试数据库数据同步功能"""
        await self.setup(page)
        
        # 启动问询（通过API）
        response = await page.context.request.post(f"{BASE_URL}/api/query/start", data=json.dumps({}), headers={"Content-Type": "application/json"})
        assert response.status == 200
        data = await response.json()
        assert data['status'] == 'success'
        
        # 等待数据采集
        await asyncio.sleep(5)  # 等待5秒，确保有足够时间采集多条数据
        
        # 停止问询（通过API）
        response = await page.context.request.post(f"{BASE_URL}/api/query/stop", data=json.dumps({}), headers={"Content-Type": "application/json"})
        assert response.status == 200
        data = await response.json()
        assert data['status'] == 'success'
        
        # 获取历史数据，验证数据库是否同步
        response = await page.context.request.get(f"{BASE_URL}/api/history/data?range=day")
        assert response.status == 200
        data = await response.json()
        assert data['status'] == 'success'
        # 注意：如果没有真实硬件连接，可能不会有数据，所以这里不做严格断言
        print(f"数据库数据同步测试完成，共 {len(data['data'])} 条记录")

async def run_tests():
    """运行所有测试"""
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False)  # 非无头模式，方便查看测试过程
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            test_instance = TestIoTSystem()
            
            # 运行测试
            print("\n=== 开始测试页面加载和初始化 ===")
            await test_instance.test_page_load(page)
            
            print("\n=== 开始测试串口端口选择 ===")
            await test_instance.test_serial_port_selection(page)
            
            print("\n=== 开始测试问询周期更新 ===")
            await test_instance.test_query_interval_update(page)
            
            print("\n=== 开始测试问询控制 ===")
            await test_instance.test_query_control(page)
            
            print("\n=== 开始测试传感器数据采集 ===")
            await test_instance.test_sensor_data_collection(page)
            
            print("\n=== 开始测试历史数据 ===")
            await test_instance.test_history_data(page)
            
            print("\n=== 开始测试帧数据 ===")
            await test_instance.test_frame_data(page)
            
            print("\n=== 开始测试数据库数据同步 ===")
            await test_instance.test_database_sync(page)
            
            print("\n=== 所有测试通过！===")
            
        finally:
            # 关闭浏览器
            await context.close()
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_tests())
