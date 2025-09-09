#!/usr/bin/env python3
"""
Playwright Web Interface Runner
==============================

Automatically starts the upload system web interface and opens it in a browser
using Playwright. Provides automated interaction and testing capabilities.

Usage:
    python run_with_playwright.py
"""

import asyncio
import subprocess
import time
import signal
import sys
import os
from pathlib import Path
from playwright.async_api import async_playwright

class PlaywrightWebRunner:
    """Run the upload system with Playwright browser automation."""
    
    def __init__(self):
        self.server_process = None
        self.server_url = "http://localhost:8080"
        
    async def start_server(self):
        """Start the Flask server in background."""
        print("🔄 Starting Flask server...")
        
        # Activate venv and start server
        server_script = Path("enhanced_upload_interface.py").resolve()
        
        # Use shell with venv activation
        cmd = f"source venv/bin/activate && python {server_script}"
        
        self.server_process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid  # Create new process group
        )
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        await asyncio.sleep(3)
        
        if self.server_process.poll() is not None:
            # Server failed to start
            stdout, stderr = self.server_process.communicate()
            print(f"❌ Server failed to start:")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return False
        
        print(f"✅ Server started at {self.server_url}")
        return True
    
    def stop_server(self):
        """Stop the Flask server."""
        if self.server_process:
            print("🛑 Stopping Flask server...")
            try:
                # Kill the entire process group
                os.killpg(os.getpgid(self.server_process.pid), signal.SIGTERM)
                self.server_process.wait(timeout=5)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                # Force kill if needed
                try:
                    os.killpg(os.getpgid(self.server_process.pid), signal.SIGKILL)
                except ProcessLookupError:
                    pass
            print("✅ Server stopped")
    
    async def run_browser_session(self):
        """Run interactive browser session with the upload interface."""
        async with async_playwright() as p:
            # Launch browser
            print("🌐 Launching browser...")
            browser = await p.chromium.launch(headless=False, slow_mo=1000)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # Navigate to the upload interface
                print(f"📱 Opening {self.server_url}")
                await page.goto(self.server_url)
                
                # Wait for page to load
                await page.wait_for_selector('h1', timeout=10000)
                
                print("✅ Upload interface loaded successfully!")
                print("\n" + "="*60)
                print("🎯 INTERACTIVE DEMO STARTING")
                print("="*60)
                
                # Demo Step 1: Show qualitative data input
                await self.demo_qualitative_input(page)
                
                # Demo Step 2: Show industry context
                await self.demo_industry_context(page)
                
                # Demo Step 3: Show file upload (without actual GenAI)
                await self.demo_file_upload(page)
                
                # Demo Step 4: Show final results
                await self.demo_final_results(page)
                
                # Keep browser open for user interaction
                print("\n🎉 Demo completed!")
                print("💡 The browser will stay open for you to explore the interface")
                print("🔧 You can now upload your own data and test all features")
                print("\nPress Ctrl+C to close when done...")
                
                # Wait indefinitely until user closes
                try:
                    while not page.is_closed():
                        await asyncio.sleep(1)
                except KeyboardInterrupt:
                    print("\n👋 Closing browser...")
                
            except Exception as e:
                print(f"❌ Browser session error: {e}")
                
            finally:
                await browser.close()
    
    async def demo_qualitative_input(self, page):
        """Demonstrate qualitative data input."""
        print("\n📝 DEMO: Qualitative Data Input")
        print("-" * 40)
        
        # Load sample qualitative text
        try:
            with open('test_sample_data.txt', 'r', encoding='utf-8') as f:
                sample_text = f.read()
        except FileNotFoundError:
            sample_text = """Sample qualitative research data for demonstration.
            
            Users consistently mention camera quality as their top priority. Battery life is crucial for daily usage. Performance matters for gaming and multitasking. Price value is important for budget-conscious consumers. Build quality affects purchase decisions significantly."""
        
        # Fill in the qualitative text area
        textarea = page.locator('#qualitative-text')
        await textarea.fill(sample_text)
        
        print("✅ Sample qualitative data entered")
        print(f"📊 Text length: {len(sample_text)} characters")
        
        # Wait to see real-time validation
        await asyncio.sleep(2)
        
        # Validate the text
        validate_btn = page.locator('#validate-text-btn')
        if await validate_btn.is_visible():
            await validate_btn.click()
            print("✅ Text validation triggered")
            await asyncio.sleep(1)
    
    async def demo_industry_context(self, page):
        """Demonstrate industry context input."""
        print("\n🏭 DEMO: Industry Context Input")
        print("-" * 40)
        
        context_text = "Premium smartphone market targeting professionals aged 25-45. Key competitors include Apple, Samsung, Google. Focus on camera quality, performance, and business features."
        
        # Fill industry context
        context_input = page.locator('#industry-context')
        await context_input.fill(context_text)
        
        print("✅ Industry context entered")
        print(f"📊 Context length: {len(context_text)} characters")
        
        # Save context
        save_btn = page.locator('#save-context-btn')
        if await save_btn.is_visible():
            await save_btn.click()
            print("✅ Context saved")
            await asyncio.sleep(1)
    
    async def demo_file_upload(self, page):
        """Demonstrate file upload functionality."""
        print("\n📊 DEMO: File Upload Simulation")
        print("-" * 40)
        
        # Check if quantitative file exists
        if os.path.exists('test_large_survey.csv'):
            print("✅ Found sample CSV file")
            
            # Get file input element
            file_input = page.locator('#quantitative-file')
            
            # Upload the file
            await file_input.set_input_files('test_large_survey.csv')
            print("✅ Sample CSV file uploaded")
            
            # Wait for processing
            await asyncio.sleep(2)
            
        else:
            print("⚠️  No sample CSV file found - skipping file upload demo")
    
    async def demo_final_results(self, page):
        """Show final results and analysis options."""
        print("\n🎯 DEMO: Analysis Options")
        print("-" * 40)
        
        # Check if analysis button is enabled
        analysis_btn = page.locator('#generate-analysis-btn')
        
        if await analysis_btn.is_visible():
            is_enabled = await analysis_btn.is_enabled()
            if is_enabled:
                await analysis_btn.click()
                print("✅ Analysis generation triggered")
                await asyncio.sleep(2)
            else:
                print("⚠️  Analysis button not enabled - may need more data")
        
        print("✅ Demo sequence completed")
    
    async def run(self):
        """Run the complete Playwright session."""
        try:
            # Start server
            if not await self.start_server():
                return False
            
            # Run browser session
            await self.run_browser_session()
            
        except KeyboardInterrupt:
            print("\n👋 Session interrupted by user")
        except Exception as e:
            print(f"❌ Error during session: {e}")
        finally:
            self.stop_server()
        
        return True

async def main():
    """Main execution function."""
    print("🎭 Playwright Web Interface Runner")
    print("=" * 50)
    print("This will:")
    print("1. ✅ Start the Flask upload server")
    print("2. ✅ Launch browser with Playwright")  
    print("3. ✅ Open the upload interface")
    print("4. ✅ Run interactive demo")
    print("5. ✅ Keep browser open for exploration")
    print("\nPress Ctrl+C anytime to stop")
    print("=" * 50)
    
    runner = PlaywrightWebRunner()
    
    # Setup signal handler for clean shutdown
    def signal_handler(signum, frame):
        print("\n🛑 Received shutdown signal")
        runner.stop_server()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    success = await runner.run()
    
    if success:
        print("\n🎉 Playwright session completed successfully!")
    else:
        print("\n❌ Playwright session failed")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)