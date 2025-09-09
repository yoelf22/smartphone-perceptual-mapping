#!/usr/bin/env python3
"""
Test enhanced perceptual maps with realistic data
"""
import pandas as pd
from data_driven_analyzer import DataDrivenAnalyzer
import matplotlib.pyplot as plt

def test_enhanced_maps():
    """Test the enhanced map generation with realistic data."""
    print("🧪 Testing Enhanced Perceptual Maps")
    print("=" * 40)
    
    # Load the example data
    try:
        df = pd.read_csv('example_flexible_data.csv')
        print(f"✅ Loaded data: {len(df)} services")
        
        # Create analyzer
        analyzer = DataDrivenAnalyzer(df)
        
        # Get analysis summary
        summary = analyzer.get_analysis_summary()
        print(f"📊 Available dimensions: {summary['available_dimensions']}")
        print(f"📈 Total brands: {summary['brands']}")
        
        # Test different combinations
        test_combinations = [
            ('content_quality', 'user_interface', 'Quality vs UX'),
            ('performance', 'price_value', 'Performance vs Value'),
            ('brand_trust', 'innovation', 'Trust vs Innovation')
        ]
        
        for x_dim, y_dim, description in test_combinations:
            if x_dim in summary['available_dimensions'] and y_dim in summary['available_dimensions']:
                print(f"\n🎨 Creating {description} map...")
                
                # Create enhanced map
                filename = f"enhanced_{x_dim}_vs_{y_dim}_test.png"
                fig, ax = analyzer.create_perceptual_map(
                    x_dim, y_dim, 
                    save_path=f"results/{filename}"
                )
                
                plt.close(fig)  # Clean up
                print(f"   ✅ Saved: {filename}")
                
        print(f"\n🎉 Enhanced maps created! Key improvements:")
        print(f"   • Professional brand colors")
        print(f"   • Smart labels with leader lines")
        print(f"   • Quadrant analysis (Leaders, Niche Players, etc.)")
        print(f"   • Enhanced bubble sizing")
        print(f"   • Professional legends and styling")
        print(f"   • Grid and reference lines")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Set matplotlib backend for headless operation
    import matplotlib
    matplotlib.use('Agg')
    
    test_enhanced_maps()