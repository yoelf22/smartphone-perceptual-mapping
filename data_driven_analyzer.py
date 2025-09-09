#!/usr/bin/env python3
"""
Data-Driven Analyzer
====================

Completely data-driven perceptual mapping that extracts all parameters 
from the input data structure without hardcoding.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional

class DataDrivenAnalyzer:
    """Fully data-driven perceptual mapping analyzer."""
    
    def __init__(self, df: pd.DataFrame):
        """Initialize with automatic data structure detection."""
        self.original_data = df.copy()
        self.data = df.copy()
        
        # Automatically detect data structure
        self.analysis = self._analyze_data_structure()
        
        # Prepare data for analysis
        self._prepare_data()
    
    def _analyze_data_structure(self) -> Dict:
        """Analyze data structure and extract all key parameters."""
        analysis = {
            'total_rows': len(self.data),
            'total_columns': len(self.data.columns),
            'column_types': {},
            'numeric_columns': [],
            'string_columns': [],
            'identifier_column': None,
            'category_columns': [],
            'rating_columns': [],
            'special_columns': {}
        }
        
        # Analyze each column
        for col in self.data.columns:
            col_type = str(self.data[col].dtype)
            analysis['column_types'][col] = col_type
            
            # Categorize columns by type
            if self.data[col].dtype in ['object', 'string']:
                analysis['string_columns'].append(col)
            elif np.issubdtype(self.data[col].dtype, np.number):
                analysis['numeric_columns'].append(col)
        
        # Auto-detect identifier column
        analysis['identifier_column'] = self._find_identifier_column()
        
        # Auto-detect category columns
        analysis['category_columns'] = self._find_category_columns()
        
        # Auto-detect rating columns
        analysis['rating_columns'] = self._find_rating_columns()
        
        # Auto-detect special columns (popularity, etc.)
        analysis['special_columns'] = self._find_special_columns()
        
        return analysis
    
    def _find_identifier_column(self) -> Optional[str]:
        """Find the column most likely to contain product/item identifiers."""
        # Get string columns directly from data
        string_cols = [col for col in self.data.columns if self.data[col].dtype in ['object', 'string']]
        
        if not string_cols:
            return None
        
        # Score columns based on likelihood of being identifiers
        scores = {}
        
        for col in string_cols:
            score = 0
            col_lower = col.lower()
            
            # Check for identifier keywords
            identifier_keywords = [
                'name', 'product', 'item', 'service', 'brand', 'model', 
                'company', 'app', 'platform', 'tool', 'system', 'option'
            ]
            
            for keyword in identifier_keywords:
                if keyword in col_lower:
                    score += 10
            
            # Check uniqueness (identifiers should be mostly unique)
            unique_ratio = self.data[col].nunique() / len(self.data)
            if unique_ratio > 0.8:
                score += 5
            elif unique_ratio > 0.5:
                score += 3
            
            # Check for meaningful content (not just codes)
            avg_length = self.data[col].astype(str).str.len().mean()
            if avg_length > 3:
                score += 2
            
            scores[col] = score
        
        # Return the column with the highest score
        if scores:
            return max(scores, key=scores.get)
        
        return string_cols[0] if string_cols else None
    
    def _find_category_columns(self) -> List[str]:
        """Find columns that represent categories/groupings."""
        string_cols = [col for col in self.data.columns if self.data[col].dtype in ['object', 'string']]
        category_cols = []
        
        category_keywords = ['category', 'type', 'tier', 'segment', 'class', 'level', 'group']
        
        for col in string_cols:
            col_lower = col.lower()
            
            # Skip identifier column (will be determined later)
            # This is handled in the filtering logic below
            
            # Check for category keywords
            for keyword in category_keywords:
                if keyword in col_lower:
                    category_cols.append(col)
                    break
            else:
                # Check if it has low cardinality (typical of categories)
                unique_ratio = self.data[col].nunique() / len(self.data)
                if unique_ratio < 0.3 and self.data[col].nunique() > 1:
                    category_cols.append(col)
        
        return category_cols
    
    def _find_rating_columns(self) -> List[str]:
        """Find columns that contain ratings/scores."""
        numeric_cols = [col for col in self.data.columns if np.issubdtype(self.data[col].dtype, np.number)]
        rating_cols = []
        
        for col in numeric_cols:
            # Skip special columns (will be checked later)
            # This is handled in the filtering logic
            
            # Check if values look like ratings
            col_min, col_max = self.data[col].min(), self.data[col].max()
            col_range = col_max - col_min
            
            # Typical rating characteristics
            is_rating = (
                (col_range <= 10 and col_min >= 0) or  # 0-10 scale
                (col_range <= 9 and col_min >= 1) or   # 1-10 scale
                (col_range <= 4 and col_min >= 1) or   # 1-5 scale
                (col_range <= 6 and col_min >= 1)      # 1-7 scale
            )
            
            if is_rating:
                rating_cols.append(col)
        
        return rating_cols
    
    def _find_special_columns(self) -> Dict[str, str]:
        """Find special columns like popularity, market share, etc."""
        numeric_cols = [col for col in self.data.columns if np.issubdtype(self.data[col].dtype, np.number)]
        special_cols = {}
        
        # Look for popularity/market share indicators
        for col in numeric_cols:
            col_lower = col.lower()
            
            if any(keyword in col_lower for keyword in ['popularity', 'popular', 'market_share', 'share']):
                special_cols['popularity'] = col
            elif any(keyword in col_lower for keyword in ['size', 'volume', 'count', 'users']):
                special_cols['size'] = col
        
        return special_cols
    
    def _prepare_data(self):
        """Prepare data for analysis with standardized column names."""
        # Create working copy
        self.processed_data = self.data.copy()
        
        # Standardize identifier column
        identifier_col = self.analysis['identifier_column']
        if identifier_col and identifier_col != 'phone_model':
            self.processed_data = self.processed_data.rename(columns={identifier_col: 'phone_model'})
        
        # Create brand column from identifier if not exists
        if 'brand' not in self.processed_data.columns and 'phone_model' in self.processed_data.columns:
            self.processed_data['brand'] = (
                self.processed_data['phone_model']
                .astype(str)
                .str.extract(r'^(\w+)')[0]
                .fillna('Unknown')
            )
        
        # Handle tier/category
        category_cols = self.analysis['category_columns']
        if category_cols and 'tier' not in self.processed_data.columns:
            self.processed_data = self.processed_data.rename(columns={category_cols[0]: 'tier'})
        elif 'tier' not in self.processed_data.columns:
            self.processed_data['tier'] = 'Standard'
        
        # Handle popularity
        if 'popularity' not in self.processed_data.columns:
            popularity_col = self.analysis['special_columns'].get('popularity')
            if popularity_col:
                self.processed_data = self.processed_data.rename(columns={popularity_col: 'popularity'})
            else:
                # Create synthetic popularity based on ratings
                rating_cols = self.analysis['rating_columns']
                if rating_cols:
                    avg_rating = self.processed_data[rating_cols].mean(axis=1)
                    # Normalize to 0-100 scale
                    min_rating, max_rating = avg_rating.min(), avg_rating.max()
                    self.processed_data['popularity'] = (
                        ((avg_rating - min_rating) / (max_rating - min_rating)) * 100
                    ).round().astype(int)
                else:
                    self.processed_data['popularity'] = 50  # Default
    
    def get_available_dimensions(self) -> List[str]:
        """Get list of dimensions available for perceptual mapping."""
        # Return only rating columns, excluding metadata
        exclude_columns = ['phone_model', 'brand', 'tier', 'popularity']
        exclude_columns.extend(self.analysis['category_columns'])
        
        dimensions = [
            col for col in self.analysis['rating_columns'] 
            if col not in exclude_columns
        ]
        
        return dimensions
    
    def create_perceptual_map(self, x_dimension: str, y_dimension: str, save_path: str = None) -> Tuple:
        """Create perceptual map using the ORIGINAL WORKING approach."""
        # Validate dimensions
        available_dims = self.get_available_dimensions()
        
        if x_dimension not in available_dims:
            raise ValueError(f"X dimension '{x_dimension}' not in available dimensions: {available_dims}")
        
        if y_dimension not in available_dims:
            raise ValueError(f"Y dimension '{y_dimension}' not in available dimensions: {available_dims}")
        
        # Set up matplotlib for non-interactive use - EXACTLY like original
        fig, ax = plt.subplots(figsize=(11.2, 8))
        
        # Get data for the two dimensions - EXACTLY like original
        x_data = self.processed_data[x_dimension]
        y_data = self.processed_data[y_dimension]
        
        # Define brand colors - simplified version
        brand_colors = self._get_brand_colors()
        
        print(f"📊 Creating perceptual map with {len(self.processed_data)} data points...")
        print(f"   X-axis ({x_dimension}): {x_data.min():.1f} to {x_data.max():.1f}")
        print(f"   Y-axis ({y_dimension}): {y_data.min():.1f} to {y_data.max():.1f}")
        
        # CORRECT APPROACH: Aggregate survey responses by product
        print(f"   🔄 Aggregating survey responses by product...")
        
        # Group by product and calculate average scores + frequency
        product_groups = self.processed_data.groupby('phone_model').agg({
            x_dimension: 'mean',
            y_dimension: 'mean',
            'phone_model': 'count'  # Count for frequency/popularity
        }).rename(columns={'phone_model': 'frequency'})
        
        print(f"   📊 {len(self.processed_data)} survey responses → {len(product_groups)} unique products")
        
        # Create scatter plot - one point per product at average coordinates
        for product_name, row in product_groups.iterrows():
            avg_x = row[x_dimension]
            avg_y = row[y_dimension] 
            frequency = row['frequency']
            
            # Get brand color (extract brand from product name)
            brand = product_name.split()[0] if ' ' in product_name else product_name
            color = brand_colors.get(brand, '#666666')
            
            # Bubble size based on frequency in survey (more responses = larger bubble)
            # Increased by 50% as requested
            bubble_size = int((100 + min(700, frequency * 8)) * 1.5)  # Scale with response count, 50% larger
            
            # Debug each aggregated product
            print(f"   📍 {product_name}: ({avg_x:.1f}, {avg_y:.1f}) - {frequency} responses")
            
            # Plot one point per product at averaged coordinates  
            ax.scatter(avg_x, avg_y,
                      c=color, marker='o', s=bubble_size,
                      alpha=0.8, edgecolors='black', linewidth=1.5)
            
            # Add product label on the left with colored background and connecting line
            # Position label to the left of the circle
            label_offset_x = -40  # Left of circle
            label_offset_y = 0    # Aligned with circle center
            
            # Use matplotlib's built-in connection instead of manual line drawing
            
            # Add label with colored background matching circle and connecting line
            ax.annotate(product_name, (avg_x, avg_y),
                       xytext=(label_offset_x, label_offset_y), textcoords='offset points',
                       fontsize=9, fontweight='normal',  # Lighter regular font
                       ha='right', va='center',  # Right-align text, center vertically
                       bbox=dict(boxstyle='round,pad=0.3', 
                               facecolor=color, alpha=0.6,  # Same color as circle with transparency
                               edgecolor='black', linewidth=0.5),
                       arrowprops=dict(arrowstyle='-', color=color, lw=1, alpha=0.7))
        
        # Customize axes - EXACTLY like original
        ax.set_xlabel(x_dimension.replace('_', ' ').title(), fontsize=14, fontweight='bold')
        ax.set_ylabel(y_dimension.replace('_', ' ').title(), fontsize=14, fontweight='bold')
        
        # Auto zoom to actual product data range (aggregated averages) for better visibility
        # Use aggregated product ranges instead of raw survey data for tighter zoom
        product_x_values = product_groups[x_dimension]
        product_y_values = product_groups[y_dimension]
        
        x_min, x_max = product_x_values.min(), product_x_values.max()
        y_min, y_max = product_y_values.min(), product_y_values.max()
        
        # Minimal padding for maximum zoom while keeping circles visible
        x_range = max(x_max - x_min, 0.5)  # Minimum range to prevent division by zero
        y_range = max(y_max - y_min, 0.5)  # Minimum range to prevent division by zero
        
        x_padding = x_range * 0.1  # 10% padding for tight zoom
        y_padding = y_range * 0.1  # 10% padding for tight zoom
        
        print(f"   🔍 Auto-zoom: X range [{x_min:.1f}, {x_max:.1f}] → [{x_min-x_padding:.1f}, {x_max+x_padding:.1f}]")
        print(f"   🔍 Auto-zoom: Y range [{y_min:.1f}, {y_max:.1f}] → [{y_min-y_padding:.1f}, {y_max+y_padding:.1f}]")
        
        ax.set_xlim(x_min - x_padding, x_max + x_padding)
        ax.set_ylim(y_min - y_padding, y_max + y_padding)
        
        # Add reference lines at means of aggregated product data
        product_x_mean = product_x_values.mean()
        product_y_mean = product_y_values.mean()
        ax.axhline(product_y_mean, color='gray', linestyle='--', alpha=0.5, linewidth=1)
        ax.axvline(product_x_mean, color='gray', linestyle='--', alpha=0.5, linewidth=1)
        
        print(f"   📊 Reference lines at X={product_x_mean:.1f}, Y={product_y_mean:.1f}")
        
        # Add quadrant labels if requested - EXACTLY like original
        quadrant_configs = [
            (x_max - x_padding/3, y_max - y_padding/3, 'Leaders', 'lightgreen'),
            (x_min + x_padding/3, y_max - y_padding/3, 'Niche Players', 'lightblue'),
            (x_min + x_padding/3, y_min + y_padding/3, 'Challenged', 'lightcoral'),
            (x_max - x_padding/3, y_min + y_padding/3, 'Specialists', 'lightyellow')
        ]
        
        for x_pos, y_pos, label, color in quadrant_configs:
            ax.text(x_pos, y_pos, label, ha='center', va='center',
                   fontsize=12, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor=color, alpha=0.8))
        
        # Add title - like original but data-driven  
        title = f'Perceptual Map: {x_dimension.replace("_", " ")} vs {y_dimension.replace("_", " ")}'
        title += '\n(Bubble size = Survey response frequency)'
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=25)
        
        # Add grid - EXACTLY like original
        ax.grid(True, alpha=0.3, linestyle=':')
        
        # Create legend
        self._create_enhanced_legend(ax, brand_colors)
        
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            print(f"📁 Map saved to: {save_path}")
        
        return fig, ax
    
    def _calculate_bubble_size(self, popularity):
        """Calculate bubble size based on popularity (like original version)."""
        # Scale popularity to bubble size (50-500 range for better visibility)
        min_size, max_size = 100, 800
        normalized = (popularity - 0) / (100 - 0)  # Assume 0-100 scale
        return min_size + (max_size - min_size) * normalized
    
    def _add_smart_labels_with_leaders(self, ax, x_dimension, y_dimension, brand_colors):
        """Add smart labels with leader lines (adapted from original version)."""
        for _, row in self.processed_data.iterrows():
            popularity = row.get('popularity', 50)
            bubble_size = self._calculate_bubble_size(popularity)
            
            # Calculate bubble radius in data coordinates
            ax_bbox = ax.get_window_extent()
            fig_bbox = ax.figure.get_window_extent()
            width_ratio = (ax.get_xlim()[1] - ax.get_xlim()[0]) / ax_bbox.width
            height_ratio = (ax.get_ylim()[1] - ax.get_ylim()[0]) / ax_bbox.height
            
            radius_points = (bubble_size / (72**2 / ax.figure.dpi**2))**0.5
            radius_data_x = radius_points * width_ratio
            radius_data_y = radius_points * height_ratio
            
            # Position label at 2.5 diameters to the left of circle center
            label_offset_x = -2.5 * 2 * radius_data_x
            label_offset_y = 0
            
            label_x = row[x_dimension] + label_offset_x
            label_y = row[y_dimension] + label_offset_y
            
            # Get brand color and make it lighter for background
            brand = row['brand']
            bubble_color = brand_colors.get(brand, '#666666')
            
            def lighten_color(hex_color, factor=0.3):
                """Convert hex color to lighter shade"""
                import matplotlib.colors as mcolors
                rgb = mcolors.hex2color(hex_color)
                light_rgb = [min(1, c + (1-c) * factor) for c in rgb]
                return mcolors.rgb2hex(light_rgb)
            
            light_bg_color = lighten_color(bubble_color, 0.7)
            
            # Add text label with leader line
            ax.annotate(
                row['phone_model'], 
                xy=(row[x_dimension], row[y_dimension]),
                xytext=(label_x, label_y),
                fontsize=9,
                ha='right', va='center',
                bbox=dict(
                    boxstyle='round,pad=0.4', 
                    facecolor=light_bg_color, 
                    edgecolor=bubble_color,
                    alpha=0.9,
                    linewidth=1
                ),
                arrowprops=dict(
                    arrowstyle='-',
                    color=bubble_color,
                    lw=1,
                    alpha=0.7
                )
            )
    
    def _get_brand_colors(self):
        """Get professional brand colors mapping."""
        default_brand_colors = {
            'Apple': '#007AFF',
            'Samsung': '#1f77b4', 
            'Google': '#ff7f0e',
            'OnePlus': '#2ca02c',
            'Xiaomi': '#d62728',
            'Netflix': '#E50914',
            'Spotify': '#1DB954',
            'Disney': '#0063D1',
            'Amazon': '#FF9900',
            'YouTube': '#FF0000',
            'Hulu': '#66AA33',
            'HBO': '#8A2BE2',
            'Coursera': '#0056D3',
            'LinkedIn': '#0077B5',
            'MasterClass': '#EA4335'
        }
        
        brands = self.processed_data['brand'].unique()
        brand_colors = {}
        available_colors = ['#007AFF', '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', 
                           '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        
        for i, brand in enumerate(brands):
            if brand in default_brand_colors:
                brand_colors[brand] = default_brand_colors[brand]
            else:
                brand_colors[brand] = available_colors[i % len(available_colors)]
        
        return brand_colors

    def _add_quadrant_backgrounds(self, ax, x_center, y_center, x_min, x_max, y_min, y_max):
        """Add colored quadrant background rectangles."""
        # Define quadrant colors (subtle backgrounds)
        quadrant_colors = {
            'leaders': '#e6ffe6',      # Light green - top right
            'niche': '#ffe6e6',        # Light red/pink - top left  
            'challenged': '#ffebe6',   # Light orange - bottom left
            'specialists': '#e6f3ff'   # Light blue - bottom right
        }
        
        # Create background rectangles
        # Top-left: Niche Players (Low X, High Y)
        ax.add_patch(plt.Rectangle((x_min, y_center), x_center - x_min, y_max - y_center, 
                                  facecolor=quadrant_colors['niche'], alpha=0.3, zorder=0))
        
        # Top-right: Leaders (High X, High Y) 
        ax.add_patch(plt.Rectangle((x_center, y_center), x_max - x_center, y_max - y_center,
                                  facecolor=quadrant_colors['leaders'], alpha=0.3, zorder=0))
        
        # Bottom-left: Challenged (Low X, Low Y)
        ax.add_patch(plt.Rectangle((x_min, y_min), x_center - x_min, y_center - y_min,
                                  facecolor=quadrant_colors['challenged'], alpha=0.3, zorder=0))
        
        # Bottom-right: Specialists (High X, Low Y)
        ax.add_patch(plt.Rectangle((x_center, y_min), x_max - x_center, y_center - y_min,
                                  facecolor=quadrant_colors['specialists'], alpha=0.3, zorder=0))

    def _add_quadrant_labels_proper(self, ax, x_center, y_center, x_min, x_max, y_min, y_max):
        """Add proper quadrant labels in corners."""
        # Calculate label positions (in corner areas)
        x_left = x_min + (x_center - x_min) * 0.15
        x_right = x_center + (x_max - x_center) * 0.85
        y_bottom = y_min + (y_center - y_min) * 0.15  
        y_top = y_center + (y_max - y_center) * 0.85
        
        # Add quadrant labels
        label_style = dict(fontsize=14, fontweight='bold', ha='center', va='center',
                          bbox=dict(boxstyle='round,pad=0.6', facecolor='white', 
                                   edgecolor='gray', alpha=0.9))
        
        ax.text(x_left, y_top, 'NICHE\nPLAYERS', color='#CC0000', **label_style)
        ax.text(x_right, y_top, 'LEADERS', color='#00AA00', **label_style)  
        ax.text(x_left, y_bottom, 'CHALLENGED', color='#FF6600', **label_style)
        ax.text(x_right, y_bottom, 'SPECIALISTS', color='#0066CC', **label_style)
    
    def _create_enhanced_legend(self, ax, brand_colors):
        """Create comprehensive legend (like original version)."""
        brand_handles = []
        for brand, color in brand_colors.items():
            if brand in self.processed_data['brand'].values:
                handle = plt.Line2D([0], [0], marker='o', color='w', 
                                  markerfacecolor=color, markersize=12,
                                  markeredgecolor='black', markeredgewidth=1.5, 
                                  label=brand, linestyle='None')
                brand_handles.append(handle)
        
        # Create brand legend
        if brand_handles:
            brand_legend = ax.legend(handles=brand_handles, title='Brands', 
                                   loc='upper left', bbox_to_anchor=(1.02, 1),
                                   fontsize=10, title_fontsize=12)
            brand_legend.get_title().set_fontweight('bold')
            ax.add_artist(brand_legend)
    
    def get_analysis_summary(self) -> Dict:
        """Get complete analysis summary."""
        dimensions = self.get_available_dimensions()
        
        return {
            'total_products': len(self.processed_data),
            'available_dimensions': dimensions,
            'possible_maps': len(dimensions) * (len(dimensions) - 1) // 2,
            'brands': self.processed_data['brand'].nunique(),
            'categories': self.processed_data['tier'].nunique(),
            'data_structure': {
                'identifier_column': self.analysis['identifier_column'],
                'category_columns': self.analysis['category_columns'],
                'rating_columns': self.analysis['rating_columns'],
                'special_columns': self.analysis['special_columns']
            }
        }

def test_data_driven_analyzer():
    """Test the data-driven analyzer with various data formats."""
    print("🧪 Testing Data-Driven Analyzer")
    print("=" * 40)
    
    # Test with streaming services data
    streaming_data = pd.DataFrame([
        ['Netflix', 'Entertainment', 85, 9, 8, 8, 6],
        ['Spotify', 'Music', 82, 8, 9, 8, 8],
        ['Disney+', 'Entertainment', 78, 8, 8, 7, 5]
    ], columns=['service', 'category', 'popularity', 'content_quality', 'user_interface', 'performance', 'price_value'])
    
    print("\n📊 Testing with Streaming Services Data:")
    analyzer = DataDrivenAnalyzer(streaming_data)
    summary = analyzer.get_analysis_summary()
    
    print(f"✅ Analysis Summary:")
    for key, value in summary.items():
        if key != 'data_structure':
            print(f"   • {key}: {value}")
    
    dimensions = analyzer.get_available_dimensions()
    print(f"📋 Available Dimensions: {dimensions}")
    
    return analyzer

if __name__ == "__main__":
    test_data_driven_analyzer()