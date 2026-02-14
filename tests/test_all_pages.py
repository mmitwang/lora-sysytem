"""测试所有页面的功能"""

import asyncio
from playwright.async_api import async_playwright


async def test_all_pages():
    """测试所有页面的加载和基本功能"""
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            # 测试概览页面
            print("测试概览页面...")
            await page.goto('http://localhost:5000/overview')
            await page.wait_for_load_state('networkidle')
            await page.screenshot(path='tests/screenshots/overview.png')
            assert '系统概览' in await page.content()
            print("概览页面测试通过")
            
            # 测试温湿度监控页面
            print("测试温湿度监控页面...")
            await page.goto('http://localhost:5000/temperature')
            await page.wait_for_load_state('networkidle')
            await page.screenshot(path='tests/screenshots/temperature.png')
            assert '温湿度监控' in await page.content()
            print("温湿度监控页面测试通过")
            
            # 测试温振监控页面
            print("测试温振监控页面...")
            await page.goto('http://localhost:5000/vibration')
            await page.wait_for_load_state('networkidle')
            await page.screenshot(path='tests/screenshots/vibration.png')
            assert '温振监控' in await page.content()
            print("温振监控页面测试通过")
            
            # 测试视频监控页面
            print("测试视频监控页面...")
            await page.goto('http://localhost:5000/video')
            await page.wait_for_load_state('networkidle')
            await page.screenshot(path='tests/screenshots/video.png')
            assert '视频监控' in await page.content()
            print("视频监控页面测试通过")
            
            # 测试空气质量监控页面
            print("测试空气质量监控页面...")
            await page.goto('http://localhost:5000/air')
            await page.wait_for_load_state('networkidle')
            await page.screenshot(path='tests/screenshots/air.png')
            assert '空气质量监控' in await page.content()
            print("空气质量监控页面测试通过")
            
            # 测试导航栏功能
            print("测试导航栏功能...")
            
            # 从概览页面导航到温湿度监控页面
            await page.goto('http://localhost:5000/overview')
            await page.wait_for_load_state('networkidle')
            
            # 点击温湿度监控导航链接
            await page.click('a[href="/temperature"]')
            await page.wait_for_load_state('networkidle')
            assert '温湿度监控' in await page.content()
            print("从概览页面导航到温湿度监控页面测试通过")
            
            # 点击温振监控导航链接
            await page.click('a[href="/vibration"]')
            await page.wait_for_load_state('networkidle')
            assert '温振监控' in await page.content()
            print("从温湿度监控页面导航到温振监控页面测试通过")
            
            # 点击视频监控导航链接
            await page.click('a[href="/video"]')
            await page.wait_for_load_state('networkidle')
            assert '视频监控' in await page.content()
            print("从温振监控页面导航到视频监控页面测试通过")
            
            # 点击空气质量监控导航链接
            await page.click('a[href="/air"]')
            await page.wait_for_load_state('networkidle')
            assert '空气质量监控' in await page.content()
            print("从视频监控页面导航到空气质量监控页面测试通过")
            
            # 点击概览导航链接
            await page.click('a[href="/overview"]')
            await page.wait_for_load_state('networkidle')
            assert '系统概览' in await page.content()
            print("从空气质量监控页面导航到概览页面测试通过")
            
            # 测试温湿度监控页面的功能按钮
            print("测试温湿度监控页面的功能按钮...")
            await page.goto('http://localhost:5000/temperature')
            await page.wait_for_load_state('networkidle')
            
            # 点击刷新数据按钮
            refresh_button = page.locator('button#refresh-data')
            if await refresh_button.count() > 0:
                await refresh_button.click()
                await asyncio.sleep(1)  # 等待1秒
                print("刷新数据按钮测试通过")
            
            # 点击更新周期按钮
            update_interval_button = page.locator('button#update-interval')
            if await update_interval_button.count() > 0:
                # 输入新的周期值
                interval_input = page.locator('input#query-interval')
                if await interval_input.count() > 0:
                    await interval_input.fill('3')
                    await update_interval_button.click()
                    await asyncio.sleep(1)  # 等待1秒
                    print("更新周期按钮测试通过")
            
            print("所有页面测试通过！")
            
        finally:
            # 关闭浏览器
            await browser.close()


if __name__ == '__main__':
    asyncio.run(test_all_pages())
