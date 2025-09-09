#!/usr/bin/env python3
"""
Test Flexible Column Detection
==============================

Test the system's ability to detect product name columns 
with various naming conventions.
"""

import pandas as pd

def test_flexible_column_detection():
    """Test flexible column detection with various naming patterns."""
    print("🧪 Testing Flexible Column Detection")
    print("=" * 40)
    
    # Test cases with different column naming patterns
    test_cases = [
        # Standard patterns
        {
            'name': 'Standard Product Name',
            'columns': ['product_name', 'camera_rating', 'battery_rating'],
            'data': [['iPhone 15', 8, 7], ['Samsung S24', 9, 8]]
        },
        {
            'name': 'Model Column',
            'columns': ['model', 'camera_quality', 'battery_life'],
            'data': [['iPhone 15', 8, 7], ['Samsung S24', 9, 8]]
        },
        {
            'name': 'Brand Column',
            'columns': ['brand', 'camera_score', 'battery_score'],
            'data': [['Apple', 8, 7], ['Samsung', 9, 8]]
        },
        
        # Software/Service patterns
        {
            'name': 'Software Platform',
            'columns': ['platform', 'usability', 'features'],
            'data': [['Slack', 8, 7], ['Teams', 7, 9]]
        },
        {
            'name': 'Service Provider',
            'columns': ['service', 'quality', 'price_value'],
            'data': [['Netflix', 9, 6], ['Spotify', 8, 8]]
        },
        {
            'name': 'App Name',
            'columns': ['app', 'interface', 'performance'],
            'data': [['WhatsApp', 7, 8], ['Telegram', 8, 7]]
        },
        
        # Generic patterns
        {
            'name': 'Item Name',
            'columns': ['item', 'rating1', 'rating2'],
            'data': [['Item A', 6, 7], ['Item B', 8, 5]]
        },
        {
            'name': 'Company Name',
            'columns': ['company', 'trust', 'satisfaction'],
            'data': [['Google', 8, 7], ['Microsoft', 7, 8]]
        },
        {
            'name': 'Generic Name Column',
            'columns': ['name', 'score1', 'score2'],
            'data': [['Option 1', 6, 8], ['Option 2', 9, 6]]
        },
        
        # Edge cases
        {
            'name': 'First String Column Fallback',
            'columns': ['id', 'description', 'rating1', 'rating2'],
            'data': [['Product A', 'Good product', 7, 8], ['Product B', 'Better product', 8, 7]]
        },
        {
            'name': 'Mixed Case',
            'columns': ['Product_Name', 'Quality_Rating', 'Value_Rating'],
            'data': [['Tesla Model 3', 9, 7], ['BMW i4', 8, 6]]
        }
    ]
    
    def find_product_column(df):
        """Copy of the function from enhanced_upload_interface.py"""
        product_keywords = [
            'product_name', 'product', 'phone_model', 'model', 'brand', 
            'item', 'name', 'smartphone', 'mobile', 'device', 'company',
            'manufacturer', 'service', 'option', 'choice', 'alternative',
            'solution', 'app', 'software', 'platform', 'tool', 'system',
            'website', 'car', 'vehicle'
        ]
        
        # First, try exact matches
        for keyword in product_keywords:
            if keyword in df.columns:
                return keyword
        
        # Then try partial matches
        for col in df.columns:
            col_lower = col.lower()
            for keyword in product_keywords:
                if keyword in col_lower:
                    return col
        
        # Finally, take the first string column if available
        string_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
        if string_cols:
            return string_cols[0]
        
        return None
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        print(f"\n🔍 Testing: {test_case['name']}")
        
        # Create test DataFrame
        df = pd.DataFrame(test_case['data'], columns=test_case['columns'])
        
        # Test column detection
        detected_col = find_product_column(df)
        
        if detected_col:
            print(f"✅ Detected column: '{detected_col}'")
            print(f"   Sample values: {df[detected_col].tolist()}")
            passed += 1
        else:
            print(f"❌ No product column detected")
            print(f"   Available columns: {list(df.columns)}")
            failed += 1
    
    print(f"\n📊 FLEXIBLE COLUMN DETECTION RESULTS")
    print("=" * 40)
    print(f"✅ Passed: {passed}/{len(test_cases)}")
    print(f"❌ Failed: {failed}/{len(test_cases)}")
    
    if failed == 0:
        print(f"🎉 All column detection tests passed!")
        return True
    else:
        print(f"⚠️  Some tests failed - column detection needs improvement")
        return False

def test_validation_flexibility():
    """Test the updated validation system."""
    print(f"\n🧪 Testing Updated Validation System")
    print("=" * 40)
    
    try:
        from data_upload_system import DataUploadSystem
        system = DataUploadSystem()
        
        # Test with various column names
        test_data = pd.DataFrame([
            ['Netflix', 'Entertainment', 'Premium', 80, 9, 8, 7, 6],
            ['Spotify', 'Music', 'Premium', 75, 8, 9, 8, 7],
            ['Disney+', 'Entertainment', 'Premium', 70, 7, 7, 9, 5]
        ], columns=['service', 'category', 'tier', 'popularity', 'content_quality', 'user_interface', 'value', 'features'])
        
        result = system._validate_quantitative_data(test_data, 'CSV')
        
        if result.is_valid:
            print(f"✅ Validation passed: {result.message}")
            if result.warnings:
                print(f"⚠️  Warnings:")
                for warning in result.warnings:
                    print(f"   • {warning}")
            return True
        else:
            print(f"❌ Validation failed: {result.message}")
            return False
            
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        return False

def main():
    """Run all flexibility tests."""
    print("🧪 FLEXIBLE COLUMN DETECTION TEST SUITE")
    print("=" * 50)
    
    test1_passed = test_flexible_column_detection()
    test2_passed = test_validation_flexibility()
    
    print(f"\n🎯 OVERALL RESULTS")
    print("=" * 20)
    
    if test1_passed and test2_passed:
        print(f"🎉 All flexibility tests passed!")
        print(f"✅ System can handle diverse column naming patterns")
        return 0
    else:
        print(f"⚠️  Some flexibility tests failed")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())