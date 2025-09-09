#!/usr/bin/env python3
"""
Quick test to verify map visibility fix
"""
import requests
import json

def test_map_creation_and_visibility():
    """Test that maps can be created and are visible via the API."""
    base_url = "http://localhost:8080"
    
    # Test data - minimal example
    test_data = [
        {"service": "Netflix", "content_quality": 9, "user_interface": 8, "performance": 8, "price_value": 6},
        {"service": "Spotify", "content_quality": 8, "user_interface": 9, "performance": 8, "price_value": 8},
        {"service": "Disney+", "content_quality": 8, "user_interface": 8, "performance": 7, "price_value": 5}
    ]
    
    print("🧪 Testing Map Creation and Visibility")
    print("=" * 40)
    
    # Test 1: Create a map
    print("\n1. Creating test map...")
    map_data = {
        "x_dimension": "content_quality",
        "y_dimension": "user_interface", 
        "quantitative_data": test_data
    }
    
    response = requests.post(f"{base_url}/create_map", json=map_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Map created successfully: {result['message']}")
        print(f"   📁 File: {result['map_file']}")
        print(f"   🔗 URL: {result['map_url']}")
        
        # Test 2: Check if map is accessible
        print("\n2. Testing map accessibility...")
        map_response = requests.get(f"{base_url}{result['map_url']}")
        
        if map_response.status_code == 200:
            print(f"   ✅ Map accessible! Size: {len(map_response.content)} bytes")
        else:
            print(f"   ❌ Map not accessible: {map_response.status_code}")
            
    else:
        print(f"   ❌ Map creation failed: {response.status_code}")
        print(f"   Error: {response.text}")
    
    # Test 3: List all maps
    print("\n3. Listing all available maps...")
    list_response = requests.get(f"{base_url}/list_maps")
    
    if list_response.status_code == 200:
        maps = list_response.json()['maps']
        print(f"   ✅ Found {len(maps)} total maps")
        for i, map_info in enumerate(maps[:3], 1):  # Show first 3
            print(f"   {i}. {map_info['filename']} - {map_info['created']}")
    else:
        print(f"   ❌ Failed to list maps: {list_response.status_code}")

if __name__ == "__main__":
    try:
        test_map_creation_and_visibility()
        print("\n🎉 All tests completed!")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask server at localhost:8080")
        print("   Make sure the server is running with: python enhanced_upload_interface.py")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")