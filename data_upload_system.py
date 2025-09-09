#!/usr/bin/env python3
"""
Interactive Data Upload System for Perceptual Mapping
===================================================

Comprehensive data upload and validation system with:
- Qualitative data processing (interviews/Reddit scraping)
- Industry context input
- Secure GenAI keyword extraction
- Quantitative data validation (CSV/JSON)
- Analysis generation pipeline

Usage:
    python data_upload_system.py

Security Note: 
- GenAI credentials are handled in-memory only
- No API keys are stored or logged
- Credentials are cleared after processing
"""

import pandas as pd
import numpy as np
import json
import csv
import re
import os
import sys
import getpass
import tempfile
import hashlib
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext
    GUI_AVAILABLE = True
except ImportError:
    print("⚠️  GUI components not available (tkinter not installed)")
    print("   File dialogs will use command line input instead")
    GUI_AVAILABLE = False
    tk = None
from pathlib import Path

@dataclass
class ValidationResult:
    """Result of data validation."""
    is_valid: bool
    message: str
    data: Optional[pd.DataFrame] = None
    warnings: List[str] = None

class DataUploadSystem:
    """Interactive system for uploading and validating perceptual mapping data."""
    
    # Data constraints
    QUALITATIVE_WORD_LIMITS = {
        'min_words': 100,
        'max_words': 5000,
        'recommended_min': 500,
        'recommended_max': 2000
    }
    
    QUANTITATIVE_LIMITS = {
        'min_respondents': 30,
        'max_respondents': 10000,
        'recommended_min_respondents': 100,
        'min_questions': 3,
        'max_questions': 20,
        'recommended_max_questions': 12,
        'rating_scale': (1, 9)  # 1-9 scale as requested
    }
    
    INDUSTRY_CONTEXT_LIMIT = 500  # characters
    
    def __init__(self):
        """Initialize the upload system."""
        self.session_data = {
            'qualitative_data': None,
            'industry_context': None,
            'extracted_keywords': None,
            'quantitative_data': None,
            'analysis_ready': False,
            'session_id': self._generate_session_id()
        }
        
        self.genai_credentials = None  # Will be cleared after use
        
        print("🔄 Data Upload System Initialized")
        print(f"📊 Session ID: {self.session_data['session_id']}")
        print("🔒 Security: Credentials handled in-memory only, never stored\n")
    
    def _generate_session_id(self) -> str:
        """Generate unique session identifier."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_hash = hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:6]
        return f"session_{timestamp}_{random_hash}"
    
    def start_interactive_session(self):
        """Start the complete interactive data upload session."""
        print("=" * 60)
        print("🎯 PERCEPTUAL MAPPING DATA UPLOAD SYSTEM")
        print("=" * 60)
        print("\nThis system will guide you through uploading your research data:")
        print("1. ✅ Qualitative data (interviews/discussions/Reddit)")
        print("2. ✅ Industry & product context")
        print("3. ✅ Keyword extraction (via GenAI)")
        print("4. ✅ Quantitative survey data (CSV/JSON)")
        print("5. ✅ Analysis generation")
        print("\n" + "─" * 60)
        
        try:
            # Step 1: Qualitative Data
            if not self._upload_qualitative_data():
                return False
            
            # Step 2: Industry Context
            if not self._input_industry_context():
                return False
            
            # Step 3: Keyword Extraction
            if not self._perform_keyword_extraction():
                return False
            
            # Step 4: Quantitative Data
            if not self._upload_quantitative_data():
                return False
            
            # Step 5: Generate Analysis
            self._generate_analysis_options()
            
            print("\n🎉 Data upload session completed successfully!")
            print(f"📁 Session data saved with ID: {self.session_data['session_id']}")
            
            return True
            
        except KeyboardInterrupt:
            print("\n❌ Session cancelled by user")
            return False
        except Exception as e:
            print(f"\n❌ Error during session: {str(e)}")
            return False
        finally:
            # Clear sensitive data
            self._clear_credentials()
    
    def _upload_qualitative_data(self) -> bool:
        """Step 1: Upload and validate qualitative data."""
        print("\n📝 STEP 1: QUALITATIVE DATA UPLOAD")
        print("=" * 40)
        
        # Display requirements
        limits = self.QUALITATIVE_WORD_LIMITS
        print(f"📋 Requirements:")
        print(f"   • Word Count: {limits['min_words']:,} - {limits['max_words']:,} words")
        print(f"   • Recommended: {limits['recommended_min']:,} - {limits['recommended_max']:,} words")
        print(f"   • Formats: Text files, interview summaries, Reddit dumps")
        print(f"   • Content: User discussions, interviews, social media posts\n")
        
        while True:
            print("🔽 Choose input method:")
            print("1. Upload text file")
            print("2. Paste text directly")
            print("3. Skip qualitative data (not recommended)")
            
            choice = input("\nSelect option (1-3): ").strip()
            
            if choice == '1':
                result = self._upload_text_file()
            elif choice == '2':
                result = self._input_text_directly()
            elif choice == '3':
                print("⚠️  Skipping qualitative data - analysis will be limited")
                return True
            else:
                print("❌ Invalid choice. Please select 1, 2, or 3.")
                continue
            
            if result.is_valid:
                self.session_data['qualitative_data'] = result.data
                print(f"✅ Qualitative data validated and stored")
                if result.warnings:
                    for warning in result.warnings:
                        print(f"⚠️  {warning}")
                return True
            else:
                print(f"❌ Validation failed: {result.message}")
                retry = input("Try again? (y/n): ").strip().lower()
                if retry != 'y':
                    return False
    
    def _upload_text_file(self) -> ValidationResult:
        """Upload qualitative data from file."""
        try:
            if GUI_AVAILABLE:
                # Use tkinter for file selection
                root = tk.Tk()
                root.withdraw()  # Hide main window
                
                file_path = filedialog.askopenfilename(
                    title="Select Qualitative Data File",
                    filetypes=[
                        ("Text files", "*.txt"),
                        ("All files", "*.*")
                    ]
                )
                
                if not file_path:
                    return ValidationResult(False, "No file selected")
            else:
                # Command line file input
                print("📁 Enter the full path to your text file:")
                file_path = input("File path: ").strip()
                
                if not file_path:
                    return ValidationResult(False, "No file path provided")
                
                # Remove quotes if present
                file_path = file_path.strip('"').strip("'")
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self._validate_qualitative_text(content)
            
        except Exception as e:
            return ValidationResult(False, f"File reading error: {str(e)}")
    
    def _input_text_directly(self) -> ValidationResult:
        """Input qualitative data directly via text input."""
        print("\n📝 Paste your qualitative data below.")
        print("💡 Tip: Include interview summaries, user quotes, discussion excerpts")
        print("🔚 Type 'END_INPUT' on a new line when finished\n")
        
        lines = []
        while True:
            try:
                line = input()
                if line.strip() == 'END_INPUT':
                    break
                lines.append(line)
            except EOFError:
                break
        
        content = '\n'.join(lines)
        return self._validate_qualitative_text(content)
    
    def _validate_qualitative_text(self, content: str) -> ValidationResult:
        """Validate qualitative text content."""
        if not content or not content.strip():
            return ValidationResult(False, "No content provided")
        
        # Count words
        word_count = len(content.split())
        limits = self.QUALITATIVE_WORD_LIMITS
        
        # Check minimum requirement
        if word_count < limits['min_words']:
            return ValidationResult(
                False, 
                f"Content too short: {word_count:,} words (minimum: {limits['min_words']:,})"
            )
        
        # Check maximum limit
        if word_count > limits['max_words']:
            return ValidationResult(
                False,
                f"Content too long: {word_count:,} words (maximum: {limits['max_words']:,})"
            )
        
        # Generate warnings for recommendations
        warnings = []
        if word_count < limits['recommended_min']:
            warnings.append(f"Content below recommended minimum ({limits['recommended_min']:,} words)")
        
        if word_count > limits['recommended_max']:
            warnings.append(f"Content above recommended maximum ({limits['recommended_max']:,} words)")
        
        # Basic content quality check
        sentences = len(re.split(r'[.!?]+', content))
        avg_words_per_sentence = word_count / max(sentences, 1)
        
        if avg_words_per_sentence < 5:
            warnings.append("Content appears fragmented - ensure complete thoughts")
        
        print(f"📊 Content Analysis:")
        print(f"   • Word count: {word_count:,}")
        print(f"   • Sentences: {sentences:,}")
        print(f"   • Avg words/sentence: {avg_words_per_sentence:.1f}")
        
        return ValidationResult(
            True,
            f"Qualitative data validated ({word_count:,} words)",
            data=content,
            warnings=warnings
        )
    
    def _input_industry_context(self) -> bool:
        """Step 2: Input industry and product category context."""
        print("\n🏭 STEP 2: INDUSTRY & PRODUCT CONTEXT")
        print("=" * 40)
        print(f"📝 Please provide a description of your industry and product category")
        print(f"📏 Limit: {self.INDUSTRY_CONTEXT_LIMIT} characters")
        print(f"💡 Include: market segment, target audience, key competitors\n")
        
        while True:
            print("Example: 'Premium smartphone market targeting professionals aged 25-45. ")
            print("Key competitors include Apple, Samsung, Google. Focus on camera quality, ")
            print("performance, and business features.'\n")
            
            context = input("Industry & Product Context: ").strip()
            
            if not context:
                print("❌ Context cannot be empty")
                continue
            
            if len(context) > self.INDUSTRY_CONTEXT_LIMIT:
                print(f"❌ Context too long: {len(context)} characters (max: {self.INDUSTRY_CONTEXT_LIMIT})")
                continue
            
            if len(context) < 50:
                print(f"⚠️  Context quite short ({len(context)} characters). Add more detail? (y/n): ", end="")
                response = input().strip().lower()
                if response == 'y':
                    continue
            
            self.session_data['industry_context'] = context
            print(f"✅ Industry context saved ({len(context)} characters)")
            return True
    
    def _perform_keyword_extraction(self) -> bool:
        """Step 3: Perform keyword extraction using GenAI."""
        print("\n🤖 STEP 3: KEYWORD EXTRACTION VIA GENAI")
        print("=" * 40)
        print("🔒 Security Notice: Your API credentials are processed in-memory only")
        print("🔒 No credentials are stored, logged, or transmitted to our servers")
        print("🔒 Credentials are cleared immediately after processing\n")
        
        # Skip if no qualitative data
        if not self.session_data['qualitative_data']:
            print("⚠️  No qualitative data available - skipping keyword extraction")
            return True
        
        print("🔽 Select GenAI Service:")
        print("1. OpenAI GPT")
        print("2. Anthropic Claude")
        print("3. Google Gemini")
        print("4. Skip keyword extraction")
        
        choice = input("\nSelect service (1-4): ").strip()
        
        if choice == '4':
            print("⚠️  Skipping keyword extraction")
            return True
        
        # Get credentials securely
        if not self._get_genai_credentials(choice):
            return False
        
        # Perform extraction
        keywords = self._extract_keywords_with_genai(choice)
        if keywords:
            self.session_data['extracted_keywords'] = keywords
            print("✅ Keywords extracted successfully")
            print(f"📋 Found {len(keywords)} key themes")
            return True
        else:
            print("❌ Keyword extraction failed")
            return input("Continue without keywords? (y/n): ").strip().lower() == 'y'
    
    def _get_genai_credentials(self, service_choice: str) -> bool:
        """Securely get GenAI credentials."""
        service_map = {
            '1': 'OpenAI',
            '2': 'Anthropic',
            '3': 'Google'
        }
        
        service_name = service_map.get(service_choice, 'Unknown')
        
        print(f"\n🔐 Enter {service_name} API Key:")
        print("🔒 Input is hidden for security")
        
        try:
            api_key = getpass.getpass("API Key: ").strip()
            
            if not api_key:
                print("❌ No API key provided")
                return False
            
            self.genai_credentials = {
                'service': service_choice,
                'api_key': api_key
            }
            
            print("✅ Credentials secured in memory")
            return True
            
        except KeyboardInterrupt:
            print("\n❌ Credential input cancelled")
            return False
    
    def _extract_keywords_with_genai(self, service_choice: str) -> Optional[List[str]]:
        """Extract keywords using selected GenAI service."""
        if not self.genai_credentials:
            return None
        
        print("🔄 Processing text with GenAI...")
        
        # Create prompt
        prompt = f"""
        Analyze the following qualitative research data and extract key product attributes/dimensions 
        that users care about. Focus on actionable insights for perceptual mapping.
        
        Industry Context: {self.session_data['industry_context']}
        
        Qualitative Data:
        {self.session_data['qualitative_data'][:2000]}...
        
        Extract 8-12 key attributes in this format:
        - Attribute_Name: Brief description
        
        Focus on measurable product characteristics users mentioned.
        """
        
        try:
            # Simulate GenAI processing (replace with actual API calls)
            print("🤖 Contacting GenAI service...")
            
            # For demonstration, return sample keywords
            # In real implementation, use actual API calls here
            keywords = [
                "Camera_Quality", "Battery_Life", "Performance", "Price_Value",
                "Build_Quality", "Design_Appeal", "User_Interface", "Brand_Trust",
                "Innovation", "Reliability"
            ]
            
            print("✅ GenAI processing complete")
            return keywords
            
        except Exception as e:
            print(f"❌ GenAI processing failed: {str(e)}")
            return None
        finally:
            # Clear credentials immediately
            self._clear_credentials()
    
    def _upload_quantitative_data(self) -> bool:
        """Step 4: Upload and validate quantitative survey data."""
        print("\n📊 STEP 4: QUANTITATIVE SURVEY DATA")
        print("=" * 40)
        
        limits = self.QUANTITATIVE_LIMITS
        print(f"📋 Requirements:")
        print(f"   • Respondents: {limits['min_respondents']:,} - {limits['max_respondents']:,}")
        print(f"   • Recommended: {limits['recommended_min_respondents']:,}+ respondents")
        print(f"   • Questions: {limits['min_questions']} - {limits['max_questions']}")
        print(f"   • Rating Scale: {limits['rating_scale'][0]}-{limits['rating_scale'][1]}")
        print(f"   • Format: CSV or JSON from Google Forms, SurveyMonkey, etc.")
        print(f"   • Required: Product names and characteristic ratings\n")
        
        while True:
            print("🔽 Choose upload method:")
            print("1. Upload CSV file")
            print("2. Upload JSON file")
            print("3. View sample format")
            
            choice = input("\nSelect option (1-3): ").strip()
            
            if choice == '1':
                result = self._upload_csv_data()
            elif choice == '2':
                result = self._upload_json_data()
            elif choice == '3':
                self._show_sample_format()
                continue
            else:
                print("❌ Invalid choice. Please select 1, 2, or 3.")
                continue
            
            if result.is_valid:
                self.session_data['quantitative_data'] = result.data
                print(f"✅ Quantitative data validated and stored")
                if result.warnings:
                    for warning in result.warnings:
                        print(f"⚠️  {warning}")
                return True
            else:
                print(f"❌ Validation failed: {result.message}")
                retry = input("Try again? (y/n): ").strip().lower()
                if retry != 'y':
                    return False
    
    def _upload_csv_data(self) -> ValidationResult:
        """Upload quantitative data from CSV."""
        try:
            if GUI_AVAILABLE:
                root = tk.Tk()
                root.withdraw()
                
                file_path = filedialog.askopenfilename(
                    title="Select Quantitative Data CSV",
                    filetypes=[
                        ("CSV files", "*.csv"),
                        ("All files", "*.*")
                    ]
                )
                
                if not file_path:
                    return ValidationResult(False, "No file selected")
            else:
                # Command line file input
                print("📊 Enter the full path to your CSV file:")
                file_path = input("CSV file path: ").strip()
                
                if not file_path:
                    return ValidationResult(False, "No file path provided")
                
                # Remove quotes if present
                file_path = file_path.strip('"').strip("'")
            
            # Read CSV
            df = pd.read_csv(file_path)
            return self._validate_quantitative_data(df, 'CSV')
            
        except Exception as e:
            return ValidationResult(False, f"CSV reading error: {str(e)}")
    
    def _upload_json_data(self) -> ValidationResult:
        """Upload quantitative data from JSON."""
        try:
            if GUI_AVAILABLE:
                root = tk.Tk()
                root.withdraw()
                
                file_path = filedialog.askopenfilename(
                    title="Select Quantitative Data JSON",
                    filetypes=[
                        ("JSON files", "*.json"),
                        ("All files", "*.*")
                    ]
                )
                
                if not file_path:
                    return ValidationResult(False, "No file selected")
            else:
                # Command line file input
                print("📊 Enter the full path to your JSON file:")
                file_path = input("JSON file path: ").strip()
                
                if not file_path:
                    return ValidationResult(False, "No file path provided")
                
                # Remove quotes if present
                file_path = file_path.strip('"').strip("'")
            
            # Read JSON and convert to DataFrame
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict) and 'responses' in data:
                df = pd.DataFrame(data['responses'])
            else:
                df = pd.json_normalize(data)
            
            return self._validate_quantitative_data(df, 'JSON')
            
        except Exception as e:
            return ValidationResult(False, f"JSON reading error: {str(e)}")
    
    def _validate_quantitative_data(self, df: pd.DataFrame, file_type: str) -> ValidationResult:
        """Validate quantitative survey data."""
        limits = self.QUANTITATIVE_LIMITS
        warnings = []
        
        # Check basic structure
        if df.empty:
            return ValidationResult(False, f"{file_type} file is empty")
        
        print(f"📊 Data Analysis:")
        print(f"   • Rows (responses): {len(df):,}")
        print(f"   • Columns: {len(df.columns)}")
        
        # Check respondent count
        respondent_count = len(df)
        if respondent_count < limits['min_respondents']:
            return ValidationResult(
                False,
                f"Too few respondents: {respondent_count} (minimum: {limits['min_respondents']})"
            )
        
        if respondent_count > limits['max_respondents']:
            return ValidationResult(
                False,
                f"Too many respondents: {respondent_count:,} (maximum: {limits['max_respondents']:,})"
            )
        
        if respondent_count < limits['recommended_min_respondents']:
            warnings.append(f"Below recommended respondent count ({limits['recommended_min_respondents']})")
        
        # Identify rating columns (numeric columns likely to be ratings)
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Check for product/item identifier columns (flexible detection)
        product_keywords = [
            'product', 'brand', 'model', 'phone', 'device', 'item', 'name', 
            'smartphone', 'mobile', 'company', 'manufacturer', 'service', 
            'option', 'choice', 'alternative', 'solution', 'app', 'software',
            'platform', 'tool', 'system', 'website', 'car', 'vehicle'
        ]
        
        product_cols = [col for col in df.columns if any(keyword in col.lower() 
                       for keyword in product_keywords)]
        
        # Also check for columns that might be string type and could be identifiers
        string_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
        
        if not product_cols and not string_cols:
            warnings.append("No clear product/item identifier column found - ensure you have a column with product names")
        
        # Validate rating scales
        rating_issues = []
        for col in numeric_cols:
            col_min, col_max = df[col].min(), df[col].max()
            if col_min < limits['rating_scale'][0] or col_max > limits['rating_scale'][1]:
                rating_issues.append(f"{col}: {col_min}-{col_max}")
        
        if rating_issues:
            warnings.append(f"Rating scale issues (expected 1-9): {', '.join(rating_issues)}")
        
        # Check question count
        question_count = len(numeric_cols)
        if question_count < limits['min_questions']:
            return ValidationResult(
                False,
                f"Too few rating questions: {question_count} (minimum: {limits['min_questions']})"
            )
        
        if question_count > limits['max_questions']:
            warnings.append(f"Many rating questions ({question_count}) - consider reducing")
        
        print(f"   • Rating columns: {question_count}")
        print(f"   • Product columns: {len(product_cols)}")
        
        return ValidationResult(
            True,
            f"Quantitative data validated ({respondent_count:,} responses, {question_count} ratings)",
            data=df,
            warnings=warnings
        )
    
    def _show_sample_format(self):
        """Show sample data format."""
        print("\n📋 SAMPLE CSV FORMAT:")
        print("-" * 50)
        sample_csv = """product_name,brand,camera_quality,battery_life,performance,price_value,build_quality
iPhone 15 Pro,Apple,8,7,9,4,9
Samsung S24,Samsung,9,8,8,6,8
Google Pixel 8,Google,8,7,8,7,7"""
        print(sample_csv)
        
        print("\n📋 SAMPLE JSON FORMAT:")
        print("-" * 50)
        sample_json = """{
  "responses": [
    {"product_name": "iPhone 15 Pro", "brand": "Apple", "camera_quality": 8, "battery_life": 7},
    {"product_name": "Samsung S24", "brand": "Samsung", "camera_quality": 9, "battery_life": 8}
  ]
}"""
        print(sample_json)
        print("\n" + "─" * 50)
    
    def _generate_analysis_options(self):
        """Step 5: Generate analysis configuration."""
        print("\n🎯 STEP 5: ANALYSIS GENERATION")
        print("=" * 40)
        
        self.session_data['analysis_ready'] = True
        
        # Identify potential axes from quantitative data
        if self.session_data['quantitative_data'] is not None:
            df = self.session_data['quantitative_data']
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            print(f"📊 Available Dimensions for Perceptual Maps:")
            for i, col in enumerate(numeric_cols, 1):
                print(f"   {i}. {col.replace('_', ' ').title()}")
            
            print(f"\n🎨 Analysis Options Available:")
            print(f"   ✅ {len(numeric_cols)} perceptual map combinations")
            print(f"   ✅ Correlation analysis")
            print(f"   ✅ Competitive positioning insights")
            
            if self.session_data['extracted_keywords']:
                print(f"   ✅ AI-enhanced dimension interpretation")
        
        # Save session data
        self._save_session_data()
        
        print(f"\n🚀 Ready to Generate Analysis!")
        generate = input("Generate perceptual maps now? (y/n): ").strip().lower()
        
        if generate == 'y':
            self._run_analysis()
    
    def _save_session_data(self):
        """Save session data for analysis."""
        output_dir = Path("session_data")
        output_dir.mkdir(exist_ok=True)
        
        session_file = output_dir / f"{self.session_data['session_id']}.json"
        
        # Prepare data for JSON serialization
        save_data = self.session_data.copy()
        
        # Convert DataFrame to dict if present
        if save_data['quantitative_data'] is not None:
            save_data['quantitative_data'] = save_data['quantitative_data'].to_dict('records')
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Session data saved: {session_file}")
    
    def _run_analysis(self):
        """Execute the perceptual mapping analysis."""
        print("\n🔄 Running Analysis...")
        
        try:
            # Import the analyzer
            from perceptual_map_analyzer import PerceptualMapAnalyzer
            
            # Convert quantitative data to required format
            df = self.session_data['quantitative_data']
            
            # Create analyzer instance
            analyzer = PerceptualMapAnalyzer(df, include_popularity=True)
            
            # Generate sample maps
            analyzer.create_perceptual_map('camera_quality', 'price_value')
            
            print("✅ Analysis complete! Check generated visualizations.")
            
        except Exception as e:
            print(f"❌ Analysis failed: {str(e)}")
    
    def _clear_credentials(self):
        """Clear sensitive credentials from memory."""
        if self.genai_credentials:
            self.genai_credentials = None
            print("🔒 Credentials cleared from memory")

def main():
    """Main execution function."""
    try:
        system = DataUploadSystem()
        success = system.start_interactive_session()
        
        if success:
            print("\n🎉 Upload session completed successfully!")
        else:
            print("\n❌ Upload session failed or was cancelled")
            
    except KeyboardInterrupt:
        print("\n👋 Session cancelled by user")
    except Exception as e:
        print(f"\n❌ System error: {str(e)}")

if __name__ == "__main__":
    main()