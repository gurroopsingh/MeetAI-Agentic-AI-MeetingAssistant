import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    os.makedirs('docs/screenshots', exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1400, 'height': 900})
        
        # 1. Dashboard
        print("Taking Dashboard screenshot...")
        await page.goto('http://localhost:3000/')
        await page.wait_for_timeout(2000)
        await page.screenshot(path='docs/screenshots/dashboard.png')
        
        # 2. Meetings
        print("Taking Meetings screenshot...")
        await page.goto('http://localhost:3000/meetings')
        await page.wait_for_timeout(2000)
        await page.screenshot(path='docs/screenshots/meetings.png')
        
        # 3. Workspace
        print("Taking Workspace screenshot...")
        link = await page.query_selector('a[href^="/meetings/"]')
        if link:
            href = await link.get_attribute('href')
            await page.goto(f'http://localhost:3000{href}')
            await page.wait_for_timeout(4000)
            await page.screenshot(path='docs/screenshots/workspace.png')
        else:
            print("No meeting found for workspace screenshot")
        
        # 4. Tasks
        print("Taking Tasks screenshot...")
        await page.goto('http://localhost:3000/tasks')
        await page.wait_for_timeout(2000)
        await page.screenshot(path='docs/screenshots/tasks.png')
        
        # 5. Settings
        print("Taking Settings screenshot...")
        await page.goto('http://localhost:3000/settings')
        await page.wait_for_timeout(2000)
        await page.screenshot(path='docs/screenshots/settings.png')
        
        await browser.close()

asyncio.run(main())
