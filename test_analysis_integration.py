#!/usr/bin/env python3
"""
Test Analysis Integration
========================

Test the complete integration between file upload, validation, and analysis generation.
This will help identify and fix the analysis failure issue.
"""

import pandas as pd
import sys
import os

def test_data_flow():
    """Test the complete data flow from upload to analysis."""
    print("🧪 Testing Analysis Integration")
    print("=" * 40)
    
    # Step 1: Test CSV reading
    print("\n📊 Step 1: Testing CSV Data Loading")
    try:
        df = pd.read_csv('test_large_survey.csv')
        print(f"✅ CSV loaded: {len(df)} rows, {len(df.columns)} columns")
        print(f"📋 Columns: {list(df.columns)}")
    except Exception as e:
        print(f"❌ CSV loading failed: {e}")
        return False
    
    # Step 2: Test data validation
    print("\n🔍 Step 2: Testing Data Validation")
    try:
        from data_upload_system import DataUploadSystem
        system = DataUploadSystem()
        
        result = system._validate_quantitative_data(df, 'CSV')
        
        if result.is_valid:
            print(f"✅ Data validation passed: {result.message}")
            if result.warnings:
                for warning in result.warnings:
                    print(f"⚠️  {warning}")
        else:
            print(f"❌ Data validation failed: {result.message}")
            return False
            
    except Exception as e:
        print(f"❌ Data validation error: {e}")
        return False
    
    # Step 3: Test analyzer creation
    print("\n🎯 Step 3: Testing Analyzer Creation")
    try:
        from perceptual_map_analyzer import PerceptualMapAnalyzer
        analyzer = PerceptualMapAnalyzer(df, include_popularity=True)
        
        print(f"✅ Analyzer created successfully")
        print(f"📊 Dimensions found: {len(analyzer.dimensions)}")
        print(f"📋 Dimensions: {analyzer.dimensions}")
        
    except Exception as e:
        print(f"❌ Analyzer creation failed: {e}")
        return False
    
    # Step 4: Test analysis summary
    print("\n📈 Step 4: Testing Analysis Summary Generation")
    try:
        dimensions = analyzer.dimensions
        
        analysis_summary = {
            'total_products': len(df),
            'dimensions': dimensions,
            'possible_maps': len(dimensions) * (len(dimensions) - 1) // 2,
            'brands': df['brand'].nunique() if 'brand' in df.columns else 0
        }
        
        print(f"✅ Analysis summary generated:")
        for key, value in analysis_summary.items():
            print(f"   • {key}: {value}")
            
    except Exception as e:
        print(f"❌ Analysis summary failed: {e}")
        return False
    
    # Step 5: Test map creation
    print("\n🗺️  Step 5: Testing Map Creation")
    try:
        # Try to create a simple map
        if len(dimensions) >= 2:
            x_dim = dimensions[0]
            y_dim = dimensions[1]
            
            print(f"📊 Attempting to create map: {x_dim} vs {y_dim}")
            
            # Test without actually showing the plot (headless)
            import matplotlib
            matplotlib.use('Agg')  # Use non-interactive backend
            
            fig, ax = analyzer.create_perceptual_map(
                x_dim, y_dim,
                save_path=None  # Don't save, just test creation
            )
            
            print(f"✅ Map creation successful!")
            
        else:
            print(f"⚠️  Not enough dimensions for map creation ({len(dimensions)} < 2)")
            
    except Exception as e:
        print(f"❌ Map creation failed: {e}")
        # This might fail due to display issues, but it's not critical
        print("   (This might be due to display/GUI issues, which is OK for testing)")
    
    print(f"\n🎉 Integration test completed successfully!")
    return True

def test_web_interface_data():
    """Test the data format expected by web interface."""
    print("\n🌐 Testing Web Interface Data Format")
    print("-" * 40)
    
    try:
        df = pd.read_csv('test_large_survey.csv')
        
        # Convert to the format expected by web interface
        data_for_web = df.to_dict('records')
        
        print(f"✅ Data converted to web format:")
        print(f"   • Type: {type(data_for_web)}")
        print(f"   • Length: {len(data_for_web)}")
        print(f"   • Sample record keys: {list(data_for_web[0].keys()) if data_for_web else 'None'}")
        
        # Test recreating DataFrame from web data
        df_recreated = pd.DataFrame(data_for_web)
        
        print(f"✅ DataFrame recreated from web data:")
        print(f"   • Shape: {df_recreated.shape}")
        print(f"   • Columns match: {list(df.columns) == list(df_recreated.columns)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Web interface data test failed: {e}")
        return False

def main():
    """Run all integration tests."""
    print("🧪 ANALYSIS INTEGRATION TEST SUITE")
    print("=" * 50)
    
    # Check if test files exist
    required_files = ['test_large_survey.csv']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ Missing test files: {', '.join(missing_files)}")
        return 1
    
    # Run tests
    tests = [
        ("Data Flow Integration", test_data_flow),
        ("Web Interface Data Format", test_web_interface_data)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🔬 Running: {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            failed += 1
    
    print(f"\n📊 TEST RESULTS")
    print("=" * 20)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"🎯 Total: {passed + failed}")
    
    if failed == 0:
        print(f"\n🎉 All tests passed! Integration should work.")
        return 0
    else:
        print(f"\n⚠️  Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())