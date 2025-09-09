#!/usr/bin/env python3
"""
Simple Playwright Runner
=======================

Launches browser to access the running upload system interface.
Assumes the Flask server is already running.

Usage:
    # Terminal 1: Start server
    source venv/bin/activate && python enhanced_upload_interface.py
    
    # Terminal 2: Launch browser
    source venv/bin/activate && python simple_playwright_runner.py
"""

import asyncio
from playwright.async_api import async_playwright
import requests
import time

async def check_server(url, max_retries=10):
    """Check if server is running."""
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return True
        except:
            pass
        
        if i < max_retries - 1:
            print(f"⏳ Waiting for server... ({i+1}/{max_retries})")
            await asyncio.sleep(1)
    
    return False

async def run_browser_demo():
    """Run browser automation demo."""
    server_url = "http://localhost:8080"
    
    # Check if server is running
    print("🔍 Checking if server is running...")
    if not await check_server(server_url):
        print(f"❌ Server not running at {server_url}")
        print("Please start the server first:")
        print("   source venv/bin/activate")
        print("   python enhanced_upload_interface.py")
        return False
    
    print("✅ Server is running!")
    
    # Launch browser
    async with async_playwright() as p:
        print("🌐 Launching browser...")
        browser = await p.chromium.launch(
            headless=False,  # Show browser window
            slow_mo=500      # Slow down actions for visibility
        )
        
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Navigate to upload interface
            print(f"📱 Opening {server_url}")
            await page.goto(server_url)
            
            # Wait for page to load
            await page.wait_for_load_state('networkidle')
            
            print("🎯 Upload interface loaded!")
            print("\n" + "="*50)
            print("🎭 STARTING AUTOMATED DEMO")
            print("="*50)
            
            # Demo Step 1: Fill qualitative data
            print("\n📝 Step 1: Adding qualitative data...")
            
            sample_text = """
            User feedback indicates that camera quality is the most important factor when choosing a smartphone. Many users specifically mention the need for excellent photo capabilities for social media sharing.

            Battery life emerged as the second most critical feature, with users consistently requesting all-day battery performance. Power users especially emphasize this need.

            Performance and speed are crucial for gaming and multitasking. Users report frustration with lag or slow app loading times.

            Price value matters significantly, particularly among younger demographics and students who want premium features at accessible prices.

            Build quality and premium feel influence purchase decisions. Users appreciate solid construction and materials that feel substantial.

            Display quality is important for media consumption and outdoor visibility. Sharp, bright screens enhance the user experience.

            Brand reputation and trust play a role in decision making, with established brands having advantages in customer confidence.

            Design appeal and aesthetics matter for devices used daily in public. Modern, stylish designs are preferred over outdated looks.
            """
            
            # Find and fill the textarea
            textarea = page.locator('#qualitative-text')
            await textarea.fill(sample_text.strip())
            
            # Wait to see real-time validation
            print("⏳ Watching real-time validation...")
            await asyncio.sleep(3)
            
            # Demo Step 2: Add industry context
            print("\n🏭 Step 2: Adding industry context...")
            
            context_text = "Premium smartphone market targeting professionals aged 25-45. Key competitors include Apple, Samsung, Google. Focus on camera quality, performance, and business features."
            
            context_input = page.locator('#industry-context')
            await context_input.fill(context_text)
            
            await asyncio.sleep(2)
            
            # Demo Step 3: Simulate GenAI service selection
            print("\n🤖 Step 3: Showing GenAI options...")
            
            service_select = page.locator('#genai-service')
            await service_select.select_option('openai')
            
            await asyncio.sleep(1)
            
            # Demo Step 4: Show file upload area
            print("\n📊 Step 4: Highlighting file upload area...")
            
            # Scroll to quantitative section
            quantitative_section = page.locator('#step4')
            await quantitative_section.scroll_into_view_if_needed()
            
            # Highlight the file drop zone
            drop_zone = page.locator('#quantitative-drop')
            await drop_zone.hover()
            
            await asyncio.sleep(2)
            
            print("\n🎉 Demo completed!")
            print("💡 The interface is now ready for your interaction")
            print("📁 You can upload your own files and test all features")
            print("🔧 Try dragging CSV files to the upload areas")
            print("\n⌨️  Press Enter to close browser, or interact directly with the interface...")
            
            # Wait for user input or interaction
            try:
                # Check if running in interactive mode
                import sys
                if sys.stdin.isatty():
                    input()  # Wait for user to press Enter
                else:
                    # Non-interactive mode, wait longer
                    await asyncio.sleep(30)
            except:
                await asyncio.sleep(10)
            
        except Exception as e:
            print(f"❌ Demo error: {e}")
            await asyncio.sleep(5)  # Keep browser open briefly to see error
            
        finally:
            print("👋 Closing browser...")
            await browser.close()
    
    return True

async def main():
    """Main execution."""
    print("🎭 Simple Playwright Browser Launcher")
    print("=" * 40)
    print("This will open the upload interface in a browser")
    print("and run an automated demo to show the features.")
    print("=" * 40)
    
    try:
        success = await run_browser_demo()
        
        if success:
            print("\n✅ Browser demo completed!")
        else:
            print("\n❌ Demo failed - make sure server is running")
            
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())