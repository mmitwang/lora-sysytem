import asyncio
from playwright.async_api import async_playwright

async def test_temperature_page():
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            print("测试1: 直接访问温湿度监控页面")
            await page.goto('http://192.168.110.6:5000/temperature')
            await page.wait_for_load_state('networkidle')
            
            # 验证页面标题
            title = await page.title()
            print(f"页面标题: {title}")
            assert '物联网数据大屏' in title
            
            # 获取当前URL
            current_url = page.url
            print(f"当前URL: {current_url}")
            
            # 等待一段时间，确保页面完全加载
            await asyncio.sleep(2)
            
            # 验证页面内容
            h2_elements = page.locator('h2')
            h2_count = await h2_elements.count()
            print(f"找到的h2元素数量: {h2_count}")
            
            for i in range(h2_count):
                h2_text = await h2_elements.nth(i).text_content()
                print(f"h2元素 {i}: {h2_text}")
            
            # 检查是否有id为temperature的section
            temperature_section = page.locator('#temperature')
            is_visible = await temperature_section.is_visible()
            print(f"温度监控section是否可见: {is_visible}")
            
            # 检查是否有id为overview的section
            overview_section = page.locator('#overview')
            overview_visible = await overview_section.is_visible()
            print(f"概览section是否可见: {overview_visible}")
            
            print("测试2: 从概览页面导航到温湿度监控页面")
            await page.goto('http://192.168.110.6:5000/overview')
            await page.wait_for_load_state('networkidle')
            
            # 点击温湿度监控导航链接
            await page.click('a[href="/temperature"]')
            await page.wait_for_load_state('networkidle')
            
            # 验证URL是否正确
            url = page.url
            print(f"当前URL: {url}")
            assert '/temperature' in url
            
            print("测试3: 检查温湿度数据显示")
            # 检查温度值元素是否存在
            temperature_value = page.locator('#temperature-value')
            await temperature_value.wait_for()
            temp_text = await temperature_value.text_content()
            print(f"温度值: {temp_text}")
            
            # 检查湿度值元素是否存在
            humidity_value = page.locator('#humidity-value')
            await humidity_value.wait_for()
            hum_text = await humidity_value.text_content()
            print(f"湿度值: {hum_text}")
            
            print("测试4: 测试时间范围选择功能")
            # 点击时间范围下拉菜单
            await page.click('#time-range')
            
            # 选择不同的时间范围
            time_ranges = ['week', 'month', 'year']
            for time_range in time_ranges:
                await page.select_option('#time-range', time_range)
                await asyncio.sleep(1)  # 等待页面更新
                print(f"选择时间范围: {time_range}")
            
            # 切换回当天
            await page.select_option('#time-range', 'day')
            await asyncio.sleep(1)
            
            print("测试5: 测试操作按钮功能")
            # 测试刷新数据按钮
            refresh_button = page.locator('#refresh-data')
            if await refresh_button.is_visible():
                await refresh_button.click()
                print("点击刷新数据按钮")
                await asyncio.sleep(2)
            else:
                print("刷新数据按钮不可见")
            
            # 测试打开串口按钮
            open_serial_button = page.locator('#open-serial')
            if await open_serial_button.is_visible():
                await open_serial_button.click()
                print("点击打开串口按钮")
                await asyncio.sleep(2)
            else:
                print("打开串口按钮不可见")
            
            # 测试启动问询按钮
            start_query_button = page.locator('#start-query')
            if await start_query_button.is_visible():
                await start_query_button.click()
                print("点击启动问询按钮")
                await asyncio.sleep(2)
            else:
                print("启动问询按钮不可见")
            
            print("测试6: 测试配置面板功能")
            # 检查串口配置部分
            serial_port_select = page.locator('#serial-port')
            if await serial_port_select.is_visible():
                print("串口配置部分可见")
            else:
                print("串口配置部分不可见")
            
            # 检查问询周期设置
            query_interval_input = page.locator('#query-interval')
            if await query_interval_input.is_visible():
                print("问询周期设置可见")
            else:
                print("问询周期设置不可见")
            
            print("测试7: 验证导航栏激活状态")
            # 检查温湿度监控导航链接是否激活
            nav_link = page.locator('nav a[href="/temperature"]')
            class_list = await nav_link.evaluate('el => el.classList')
            print(f"导航链接类列表: {class_list}")
            assert 'active' in class_list
            
            print("所有测试通过！")
            
        except Exception as e:
            print(f"测试过程中出现错误: {e}")
        finally:
            # 关闭浏览器
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_temperature_page())
