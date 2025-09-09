#!/usr/bin/env python3
"""
Test Web Analysis Endpoint
==========================

Test the analysis generation endpoint to ensure it works properly.
"""

import requests
import json
import pandas as pd

def test_analysis_endpoint():
    """Test the analysis generation endpoint."""
    print("🧪 Testing Web Analysis Endpoint")
    print("=" * 40)
    
    # Load test data
    try:
        df = pd.read_csv('test_large_survey.csv')
        print(f"✅ Test data loaded: {len(df)} rows")
    except Exception as e:
        print(f"❌ Failed to load test data: {e}")
        return False
    
    # Convert to web format
    data_for_web = df.to_dict('records')
    
    # Test the analysis endpoint
    url = "http://localhost:8080/generate_analysis"
    payload = {
        'quantitative_data': data_for_web
    }
    
    print(f"🌐 Testing analysis endpoint: {url}")
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print(f"✅ Analysis generation successful!")
                
                summary = result.get('analysis_summary', {})
                print(f"📊 Analysis Summary:")
                print(f"   • Total products: {summary.get('total_products')}")
                print(f"   • Dimensions: {len(summary.get('dimensions', []))}")
                print(f"   • Possible maps: {summary.get('possible_maps')}")
                print(f"   • Brands: {summary.get('brands')}")
                
                dimensions = result.get('available_dimensions', [])
                print(f"📋 Available dimensions: {', '.join(dimensions)}")
                
                return True
            else:
                print(f"❌ Analysis failed: {result}")
                return False
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        print("   Make sure the Flask server is running at localhost:8080")
        return False

def test_map_creation():
    """Test creating a specific perceptual map."""
    print("\n🗺️  Testing Map Creation Endpoint")
    print("-" * 40)
    
    # Load test data
    try:
        df = pd.read_csv('test_large_survey.csv')
        data_for_web = df.to_dict('records')
    except Exception as e:
        print(f"❌ Failed to load test data: {e}")
        return False
    
    # Test map creation
    url = "http://localhost:8080/create_map"
    payload = {
        'x_dimension': 'camera_quality',
        'y_dimension': 'price_value',
        'quantitative_data': data_for_web
    }
    
    print(f"🌐 Testing map creation: camera_quality vs price_value")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print(f"✅ Map creation successful!")
                print(f"📁 Map file: {result.get('map_file')}")
                return True
            else:
                print(f"❌ Map creation failed: {result}")
                return False
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    """Run web analysis tests."""
    print("🧪 WEB ANALYSIS TEST SUITE")
    print("=" * 50)
    
    # Check server availability
    try:
        response = requests.get("http://localhost:8080", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding properly")
            return 1
        print("✅ Server is running and responding")
    except:
        print("❌ Server not accessible at localhost:8080")
        print("   Please start the server with: python enhanced_upload_interface.py")
        return 1
    
    # Run tests
    tests_passed = 0
    tests_total = 2
    
    if test_analysis_endpoint():
        tests_passed += 1
    
    if test_map_creation():
        tests_passed += 1
    
    print(f"\n📊 TEST RESULTS")
    print("=" * 20)
    print(f"✅ Passed: {tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        print(f"🎉 All web analysis tests passed!")
        return 0
    else:
        print(f"⚠️  Some tests failed. Check server logs.")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())