#!/usr/bin/env python3
"""
Demo Upload System - Non-interactive version for testing
======================================================

Demonstrates the data upload system functionality without requiring
interactive input. Uses pre-created sample files.

Usage:
    python demo_upload_system.py
"""

from data_upload_system import DataUploadSystem
import pandas as pd

def demo_upload_system():
    """Demonstrate the complete upload system workflow."""
    print("🎯 DEMO: Perceptual Mapping Data Upload System")
    print("=" * 60)
    
    # Initialize system
    system = DataUploadSystem()
    
    # Step 1: Load qualitative data from file
    print("\n📝 STEP 1: Loading Qualitative Data")
    print("-" * 40)
    
    try:
        with open('test_sample_data.txt', 'r', encoding='utf-8') as f:
            qualitative_text = f.read()
        
        result = system._validate_qualitative_text(qualitative_text)
        
        if result.is_valid:
            system.session_data['qualitative_data'] = result.data
            print(f"✅ Qualitative data loaded: {result.message}")
            if result.warnings:
                for warning in result.warnings:
                    print(f"⚠️  {warning}")
        else:
            print(f"❌ Validation failed: {result.message}")
            return False
            
    except FileNotFoundError:
        print("❌ test_sample_data.txt not found. Please create sample data first.")
        return False
    
    # Step 2: Set industry context
    print("\n🏭 STEP 2: Setting Industry Context")
    print("-" * 40)
    
    industry_context = "Premium smartphone market targeting professionals aged 25-45. Key competitors include Apple, Samsung, Google. Focus on camera quality, performance, and business features."
    
    if len(industry_context) <= system.INDUSTRY_CONTEXT_LIMIT:
        system.session_data['industry_context'] = industry_context
        print(f"✅ Industry context set: {len(industry_context)} characters")
    else:
        print(f"❌ Context too long: {len(industry_context)} characters")
        return False
    
    # Step 3: Simulate keyword extraction (skip real GenAI for demo)
    print("\n🤖 STEP 3: Simulating Keyword Extraction")
    print("-" * 40)
    
    sample_keywords = [
        "Camera_Quality", "Battery_Life", "Performance", "Price_Value",
        "Build_Quality", "Display_Quality", "Design_Appeal", "Feature_Richness",
        "Brand_Trust", "Gaming_Performance"
    ]
    
    system.session_data['extracted_keywords'] = sample_keywords
    print(f"✅ Keywords extracted (simulated): {len(sample_keywords)} dimensions")
    print(f"📋 Keywords: {', '.join(sample_keywords)}")
    
    # Step 4: Load quantitative data
    print("\n📊 STEP 4: Loading Quantitative Survey Data")
    print("-" * 40)
    
    try:
        df = pd.read_csv('test_large_survey.csv')
        
        result = system._validate_quantitative_data(df, 'CSV')
        
        if result.is_valid:
            system.session_data['quantitative_data'] = result.data
            print(f"✅ Quantitative data loaded: {result.message}")
            if result.warnings:
                for warning in result.warnings:
                    print(f"⚠️  {warning}")
        else:
            print(f"❌ Validation failed: {result.message}")
            return False
            
    except FileNotFoundError:
        print("❌ test_large_survey.csv not found. Please create sample data first.")
        return False
    
    # Step 5: Generate analysis
    print("\n🎯 STEP 5: Analysis Generation")
    print("-" * 40)
    
    system.session_data['analysis_ready'] = True
    
    # Show available dimensions
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    dimension_cols = [col for col in numeric_cols if col not in ['popularity']]
    
    print(f"📊 Available Dimensions for Perceptual Maps:")
    for i, col in enumerate(dimension_cols, 1):
        print(f"   {i}. {col.replace('_', ' ').title()}")
    
    print(f"\n🎨 Analysis Summary:")
    print(f"   ✅ {len(df)} products analyzed")
    print(f"   ✅ {len(dimension_cols)} perceptual dimensions")
    print(f"   ✅ {len(dimension_cols) * (len(dimension_cols) - 1) // 2} possible map combinations")
    print(f"   ✅ {df['brand'].nunique()} brands compared")
    print(f"   ✅ Popularity-weighted bubble sizing enabled")
    
    # Save session data
    system._save_session_data()
    
    print(f"\n🎉 Demo completed successfully!")
    print(f"📁 Session ID: {system.session_data['session_id']}")
    
    # Optional: Generate a sample map
    generate_map = input("\n🗺️  Generate sample perceptual map? (y/n): ").strip().lower()
    if generate_map == 'y':
        try:
            from perceptual_map_analyzer import PerceptualMapAnalyzer
            
            analyzer = PerceptualMapAnalyzer(df, include_popularity=True)
            analyzer.create_perceptual_map('camera_quality', 'price_value',
                                         title="Demo: Camera Quality vs Price Value")
            
            print("✅ Sample perceptual map generated!")
            
        except ImportError as e:
            print(f"❌ Could not generate map: {e}")
    
    return True

def show_validation_limits():
    """Display validation limits and requirements."""
    print("\n📋 VALIDATION REQUIREMENTS")
    print("=" * 40)
    
    limits = DataUploadSystem.QUALITATIVE_WORD_LIMITS
    print(f"🔤 Qualitative Data:")
    print(f"   • Min words: {limits['min_words']:,}")
    print(f"   • Max words: {limits['max_words']:,}")
    print(f"   • Recommended: {limits['recommended_min']:,} - {limits['recommended_max']:,}")
    
    limits = DataUploadSystem.QUANTITATIVE_LIMITS
    print(f"\n📊 Quantitative Data:")
    print(f"   • Min respondents: {limits['min_respondents']:,}")
    print(f"   • Max respondents: {limits['max_respondents']:,}")
    print(f"   • Recommended min: {limits['recommended_min_respondents']:,}")
    print(f"   • Rating scale: {limits['rating_scale'][0]}-{limits['rating_scale'][1]}")
    print(f"   • Questions: {limits['min_questions']}-{limits['max_questions']}")
    
    print(f"\n📝 Industry Context:")
    print(f"   • Character limit: {DataUploadSystem.INDUSTRY_CONTEXT_LIMIT}")

if __name__ == "__main__":
    print("🔧 SYSTEM REQUIREMENTS CHECK")
    print("=" * 40)
    
    # Check for required files
    import os
    
    required_files = ['test_sample_data.txt', 'test_large_survey.csv']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        print("   These files should have been created automatically.")
        exit(1)
    else:
        print("✅ All required files found")
    
    # Show requirements
    show_validation_limits()
    
    # Run demo
    success = demo_upload_system()
    
    if success:
        print("\n🎯 Demo completed successfully!")
        print("\nNext steps:")
        print("• Use 'python data_upload_system.py' for interactive mode")
        print("• Use 'python enhanced_upload_interface.py' for web interface")
        print("• Replace sample files with your real research data")
    else:
        print("\n❌ Demo failed. Check error messages above.")