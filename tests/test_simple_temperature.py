import asyncio
from playwright.async_api import async_playwright

async def test_simple_temperature_page():
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            print("测试1: 直接访问温湿度监控页面")
            await page.goto('http://192.168.110.6:5000/temperature')
            await page.wait_for_load_state('networkidle')
            
            # 等待一段时间，确保页面完全加载
            await asyncio.sleep(3)
            
            # 获取当前URL
            current_url = page.url
            print(f"当前URL: {current_url}")
            assert '/temperature' in current_url
            
            # 检查温湿度监控页面的元素
            print("测试2: 检查温湿度监控页面元素")
            
            # 检查温度值元素
            temperature_value = page.locator('#temperature-value')
            await temperature_value.wait_for(timeout=60000)
            temp_text = await temperature_value.text_content()
            print(f"温度值: {temp_text}")
            
            # 检查湿度值元素
            humidity_value = page.locator('#humidity-value')
            await humidity_value.wait_for(timeout=60000)
            hum_text = await humidity_value.text_content()
            print(f"湿度值: {hum_text}")
            
            # 检查配置面板元素
            print("测试3: 检查配置面板元素")
            
            # 检查串口配置
            serial_port_select = page.locator('#serial-port')
            await serial_port_select.wait_for(timeout=60000)
            print("串口配置元素存在")
            
            # 检查问询周期设置
            query_interval_input = page.locator('#query-interval')
            await query_interval_input.wait_for(timeout=60000)
            print("问询周期设置元素存在")
            
            # 检查操作按钮
            print("测试4: 检查操作按钮")
            
            # 检查打开串口按钮
            open_serial_button = page.locator('#open-serial')
            await open_serial_button.wait_for(timeout=60000)
            print("打开串口按钮存在")
            
            # 检查启动问询按钮
            start_query_button = page.locator('#start-query')
            await start_query_button.wait_for(timeout=60000)
            print("启动问询按钮存在")
            
            # 检查刷新数据按钮
            refresh_button = page.locator('#refresh-data')
            await refresh_button.wait_for(timeout=60000)
            print("刷新数据按钮存在")
            
            # 检查导航栏激活状态
            print("测试5: 检查导航栏激活状态")
            nav_link = page.locator('nav a[href="/temperature"]')
            await nav_link.wait_for(timeout=60000)
            
            # 检查是否有active类
            class_list = await nav_link.evaluate('el => Array.from(el.classList)')
            print(f"导航链接类列表: {class_list}")
            assert 'active' in class_list, "导航链接应该有active类"
            
            print("所有测试通过！")
            
        except Exception as e:
            print(f"测试过程中出现错误: {e}")
        finally:
            # 关闭浏览器
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_simple_temperature_page())
