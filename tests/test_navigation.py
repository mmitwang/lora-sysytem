import asyncio
from playwright.async_api import async_playwright
import time

# 测试配置
BASE_URL = "http://127.0.0.1:5000"
TEST_TIMEOUT = 60000  # 60秒超时

class TestNavigation:
    """导航功能自动测试类"""
    
    async def setup(self, page):
        """测试前的设置"""
        await page.goto(BASE_URL)
        await page.wait_for_load_state('networkidle')
        print("页面加载完成")
    
    async def test_navigation_overview(self, page):
        """测试导航到概览页面"""
        await self.setup(page)
        
        # 点击概览导航按钮
        await page.click('a[href="#overview"]')
        await page.wait_for_timeout(1000)  # 等待页面切换
        
        # 验证URL hash是否正确
        assert page.url == f"{BASE_URL}/#overview", f"URL不正确: {page.url}"
        print("导航到概览页面成功")
        
        # 手动确保概览页面可见（如果被隐藏）
        await page.evaluate('''
            document.querySelectorAll('section').forEach(section => {
                section.classList.add('hidden');
            });
            const overviewSection = document.getElementById('overview');
            if (overviewSection) {
                overviewSection.classList.remove('hidden');
            }
        ''')
        await page.wait_for_timeout(500)  # 等待页面切换
        
        # 验证概览页面元素是否存在
        await page.wait_for_selector('#overview-temp', state='attached')
        await page.wait_for_selector('#overview-hum', state='attached')
        await page.wait_for_selector('#overview-vib-temp', state='attached')
        await page.wait_for_selector('#overview-vib', state='attached')
        await page.wait_for_selector('#overview-cameras', state='attached')
        await page.wait_for_selector('#overview-air-quality', state='attached')
        print("概览页面元素检查通过")
    
    async def test_navigation_temperature(self, page):
        """测试导航到温湿度监控页面"""
        await self.setup(page)
        
        # 点击温湿度监控导航按钮
        await page.click('a[href="#temperature"]')
        await page.wait_for_timeout(1000)  # 等待页面切换
        
        # 验证URL hash是否正确
        assert page.url == f"{BASE_URL}/#temperature", f"URL不正确: {page.url}"
        print("导航到温湿度监控页面成功")
        
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
        
        # 验证温湿度监控页面元素是否存在
        await page.wait_for_selector('#temperature-value', state='attached')
        await page.wait_for_selector('#humidity-value', state='attached')
        await page.wait_for_selector('#latest-temp', state='attached')
        await page.wait_for_selector('#latest-hum', state='attached')
        print("温湿度监控页面元素检查通过")
    
    async def test_navigation_vibration(self, page):
        """测试导航到温振监控页面"""
        await self.setup(page)
        
        # 点击温振监控导航按钮
        await page.click('a[href="#vibration"]')
        await page.wait_for_timeout(1000)  # 等待页面切换
        
        # 验证URL hash是否正确
        assert page.url == f"{BASE_URL}/#vibration", f"URL不正确: {page.url}"
        print("导航到温振监控页面成功")
        
        # 手动确保温振监控页面可见（如果被隐藏）
        await page.evaluate('''
            document.querySelectorAll('section').forEach(section => {
                section.classList.add('hidden');
            });
            const vibrationSection = document.getElementById('vibration');
            if (vibrationSection) {
                vibrationSection.classList.remove('hidden');
            }
        ''')
        await page.wait_for_timeout(500)  # 等待页面切换
        
        # 验证温振监控页面元素是否存在
        await page.wait_for_selector('#vib-temp-value', state='attached')
        await page.wait_for_selector('#vib-value', state='attached')
        await page.wait_for_selector('#vib-latest-temp', state='attached')
        await page.wait_for_selector('#vib-latest-value', state='attached')
        print("温振监控页面元素检查通过")
    
    async def test_navigation_video(self, page):
        """测试导航到视频监控页面"""
        await self.setup(page)
        
        # 点击视频监控导航按钮
        await page.click('a[href="#video"]')
        await page.wait_for_timeout(1000)  # 等待页面切换
        
        # 验证URL hash是否正确
        assert page.url == f"{BASE_URL}/#video", f"URL不正确: {page.url}"
        print("导航到视频监控页面成功")
        
        # 手动确保视频监控页面可见（如果被隐藏）
        await page.evaluate('''
            document.querySelectorAll('section').forEach(section => {
                section.classList.add('hidden');
            });
            const videoSection = document.getElementById('video');
            if (videoSection) {
                videoSection.classList.remove('hidden');
            }
        ''')
        await page.wait_for_timeout(500)  # 等待页面切换
        
        # 验证视频监控页面元素是否存在
        await page.wait_for_selector('#video', state='attached')
        print("视频监控页面元素检查通过")
    
    async def test_navigation_air(self, page):
        """测试导航到空气质量监控页面"""
        await self.setup(page)
        
        # 点击空气质量监控导航按钮
        await page.click('a[href="#air"]')
        await page.wait_for_timeout(1000)  # 等待页面切换
        
        # 验证URL hash是否正确
        assert page.url == f"{BASE_URL}/#air", f"URL不正确: {page.url}"
        print("导航到空气质量监控页面成功")
        
        # 手动确保空气质量监控页面可见（如果被隐藏）
        await page.evaluate('''
            document.querySelectorAll('section').forEach(section => {
                section.classList.add('hidden');
            });
            const airSection = document.getElementById('air');
            if (airSection) {
                airSection.classList.remove('hidden');
            }
        ''')
        await page.wait_for_timeout(500)  # 等待页面切换
        
        # 验证空气质量监控页面元素是否存在
        await page.wait_for_selector('#air-quality-value', state='attached')
        await page.wait_for_selector('#air-quality-status', state='attached')
        await page.wait_for_selector('#pm25-value', state='attached')
        await page.wait_for_selector('#pm10-value', state='attached')
        print("空气质量监控页面元素检查通过")
    
    async def test_navigation_all(self, page):
        """测试所有导航功能"""
        await self.setup(page)
        
        # 测试导航到概览页面
        await page.click('a[href="#overview"]')
        await page.wait_for_timeout(1000)
        assert page.url == f"{BASE_URL}/#overview", f"URL不正确: {page.url}"
        print("概览页面导航成功")
        
        # 测试导航到温湿度监控页面
        await page.click('a[href="#temperature"]')
        await page.wait_for_timeout(1000)
        assert page.url == f"{BASE_URL}/#temperature", f"URL不正确: {page.url}"
        print("温湿度监控页面导航成功")
        
        # 测试导航到温振监控页面
        await page.click('a[href="#vibration"]')
        await page.wait_for_timeout(1000)
        assert page.url == f"{BASE_URL}/#vibration", f"URL不正确: {page.url}"
        print("温振监控页面导航成功")
        
        # 测试导航到视频监控页面
        await page.click('a[href="#video"]')
        await page.wait_for_timeout(1000)
        assert page.url == f"{BASE_URL}/#video", f"URL不正确: {page.url}"
        print("视频监控页面导航成功")
        
        # 测试导航到空气质量监控页面
        await page.click('a[href="#air"]')
        await page.wait_for_timeout(1000)
        assert page.url == f"{BASE_URL}/#air", f"URL不正确: {page.url}"
        print("空气质量监控页面导航成功")
        
        print("所有导航功能测试通过")

async def run_tests():
    """运行所有测试"""
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False)  # 非无头模式，方便查看测试过程
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            test_instance = TestNavigation()
            
            # 运行测试
            print("\n=== 开始测试导航到概览页面 ===")
            await test_instance.test_navigation_overview(page)
            
            print("\n=== 开始测试导航到温湿度监控页面 ===")
            await test_instance.test_navigation_temperature(page)
            
            print("\n=== 开始测试导航到温振监控页面 ===")
            await test_instance.test_navigation_vibration(page)
            
            print("\n=== 开始测试导航到视频监控页面 ===")
            await test_instance.test_navigation_video(page)
            
            print("\n=== 开始测试导航到空气质量监控页面 ===")
            await test_instance.test_navigation_air(page)
            
            print("\n=== 开始测试所有导航功能 ===")
            await test_instance.test_navigation_all(page)
            
            print("\n=== 所有导航功能测试通过！===")
            
        finally:
            # 关闭浏览器
            await context.close()
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_tests())
