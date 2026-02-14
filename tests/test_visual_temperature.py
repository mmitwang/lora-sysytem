import asyncio
from playwright.async_api import async_playwright

async def test_visual_temperature_page():
    async with async_playwright() as p:
        # 启动浏览器（非无头模式）
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            print("测试1: 直接访问温湿度监控页面")
            await page.goto('http://192.168.110.6:5000/temperature')
            await page.wait_for_load_state('networkidle')
            
            # 等待一段时间，确保页面完全加载
            await asyncio.sleep(5)
            
            # 获取当前URL
            current_url = page.url
            print(f"当前URL: {current_url}")
            assert '/temperature' in current_url
            
            # 检查温湿度监控页面的元素
            print("测试2: 检查温湿度监控页面元素")
            
            # 检查温度值元素是否存在（不等待可见，只检查是否存在）
            temperature_value = page.locator('#temperature-value')
            temperature_exists = await temperature_value.is_visible()
            print(f"温度值元素是否可见: {temperature_exists}")
            
            # 检查湿度值元素是否存在
            humidity_value = page.locator('#humidity-value')
            humidity_exists = await humidity_value.is_visible()
            print(f"湿度值元素是否可见: {humidity_exists}")
            
            # 检查配置面板元素
            print("测试3: 检查配置面板元素")
            
            # 检查串口配置
            serial_port_select = page.locator('#serial-port')
            serial_exists = await serial_port_select.is_visible()
            print(f"串口配置元素是否可见: {serial_exists}")
            
            # 检查问询周期设置
            query_interval_input = page.locator('#query-interval')
            query_exists = await query_interval_input.is_visible()
            print(f"问询周期设置元素是否可见: {query_exists}")
            
            # 检查操作按钮
            print("测试4: 检查操作按钮")
            
            # 检查打开串口按钮
            open_serial_button = page.locator('#open-serial')
            open_exists = await open_serial_button.is_visible()
            print(f"打开串口按钮是否可见: {open_exists}")
            
            # 检查启动问询按钮
            start_query_button = page.locator('#start-query')
            start_exists = await start_query_button.is_visible()
            print(f"启动问询按钮是否可见: {start_exists}")
            
            # 检查刷新数据按钮
            refresh_button = page.locator('#refresh-data')
            refresh_exists = await refresh_button.is_visible()
            print(f"刷新数据按钮是否可见: {refresh_exists}")
            
            # 检查导航栏激活状态
            print("测试5: 检查导航栏激活状态")
            nav_link = page.locator('nav a[href="/temperature"]')
            nav_exists = await nav_link.is_visible()
            print(f"导航链接是否可见: {nav_exists}")
            
            # 检查是否有active类
            if nav_exists:
                class_list = await nav_link.evaluate('el => Array.from(el.classList)')
                print(f"导航链接类列表: {class_list}")
                has_active = 'active' in class_list
                print(f"导航链接是否有active类: {has_active}")
            
            # 检查页面标题
            h2_elements = page.locator('h2')
            h2_count = await h2_elements.count()
            print(f"找到的h2元素数量: {h2_count}")
            
            for i in range(h2_count):
                h2_text = await h2_elements.nth(i).text_content()
                h2_visible = await h2_elements.nth(i).is_visible()
                print(f"h2元素 {i}: {h2_text} (可见: {h2_visible})")
            
            # 检查所有section的状态
            print("测试6: 检查所有section的状态")
            sections = ['overview', 'temperature', 'vibration', 'video', 'air']
            for section_id in sections:
                section = page.locator(f'#\{section_id}')
                exists = await section.is_visible()
                print(f"Section {section_id} 是否可见: {exists}")
            
            # 等待用户输入，以便查看浏览器状态
            print("\n测试完成！请查看浏览器窗口和开发者工具控制台。")
            print("按Enter键关闭浏览器...")
            input()
            
        except Exception as e:
            print(f"测试过程中出现错误: {e}")
        finally:
            # 关闭浏览器
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_visual_temperature_page())
