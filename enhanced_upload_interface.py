#!/usr/bin/env python3
"""
Enhanced Interactive Upload Interface
=====================================

Complete web-based interface for data upload with real-time validation,
progress tracking, and analysis generation.

Features:
- Real-time word count monitoring
- Drag-and-drop file uploads
- Live validation feedback
- Secure GenAI integration
- Analysis generation dashboard

Usage:
    python enhanced_upload_interface.py
    # Opens web interface at http://localhost:5000
"""

import os
import json
import pandas as pd
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import tempfile
import uuid
from datetime import datetime
from typing import Dict, List, Optional
import threading
import time

from data_upload_system import DataUploadSystem, ValidationResult
from genai_integration import GenAIExtractor

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Random secret key for sessions

class EnhancedUploadInterface:
    """Web-based upload interface with real-time features."""
    
    def __init__(self):
        self.upload_system = DataUploadSystem()
        self.genai_extractor = GenAIExtractor()
        self.active_sessions = {}
        
        # Configure Flask app
        app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
        app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
        
    def create_session(self) -> str:
        """Create new upload session."""
        session_id = str(uuid.uuid4())
        self.active_sessions[session_id] = {
            'created_at': datetime.now(),
            'data': {
                'qualitative_data': None,
                'industry_context': None,
                'extracted_keywords': None,
                'quantitative_data': None,
                'analysis_ready': False
            },
            'status': 'initialized'
        }
        return session_id

# Global interface instance
interface = EnhancedUploadInterface()

@app.route('/')
def index():
    """Main upload interface."""
    session_id = interface.create_session()
    session['upload_session_id'] = session_id
    return render_template('upload_interface.html', session_id=session_id)

@app.route('/validate_text', methods=['POST'])
def validate_text():
    """Real-time text validation endpoint."""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        # Count words
        word_count = len(text.split()) if text else 0
        
        limits = interface.upload_system.QUALITATIVE_WORD_LIMITS
        
        # Validation status
        status = 'valid'
        message = f"{word_count:,} words"
        warnings = []
        
        if word_count == 0:
            status = 'empty'
            message = "No text entered"
        elif word_count < limits['min_words']:
            status = 'too_short'
            message = f"Too short: {word_count:,} words (min: {limits['min_words']:,})"
        elif word_count > limits['max_words']:
            status = 'too_long'  
            message = f"Too long: {word_count:,} words (max: {limits['max_words']:,})"
        else:
            if word_count < limits['recommended_min']:
                warnings.append(f"Below recommended minimum ({limits['recommended_min']:,})")
            if word_count > limits['recommended_max']:
                warnings.append(f"Above recommended maximum ({limits['recommended_max']:,})")
        
        return jsonify({
            'status': status,
            'word_count': word_count,
            'message': message,
            'warnings': warnings,
            'progress': min(100, (word_count / limits['recommended_max']) * 100)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload_file', methods=['POST'])
def upload_file():
    """Handle file uploads."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        file_type = request.form.get('file_type', 'qualitative')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process based on file type
        if file_type == 'qualitative':
            result = process_qualitative_file(filepath)
        elif file_type == 'quantitative':
            result = process_quantitative_file(filepath)
        else:
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Clean up temp file
        os.unlink(filepath)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def process_qualitative_file(filepath: str) -> Dict:
    """Process uploaded qualitative file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        result = interface.upload_system._validate_qualitative_text(content)
        
        return {
            'success': result.is_valid,
            'message': result.message,
            'data': result.data if result.is_valid else None,
            'warnings': result.warnings or []
        }
        
    except Exception as e:
        return {'success': False, 'message': f"File processing error: {str(e)}"}

def process_quantitative_file(filepath: str) -> Dict:
    """Process uploaded quantitative file."""
    try:
        # Determine file type and read
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
            file_type = 'CSV'
        elif filepath.endswith('.json'):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict) and 'responses' in data:
                df = pd.DataFrame(data['responses'])
            else:
                df = pd.json_normalize(data)
            file_type = 'JSON'
        else:
            return {'success': False, 'message': 'Unsupported file format'}
        
        result = interface.upload_system._validate_quantitative_data(df, file_type)
        
        return {
            'success': result.is_valid,
            'message': result.message,
            'data': result.data.to_dict('records') if result.is_valid else None,
            'warnings': result.warnings or [],
            'summary': {
                'rows': len(df),
                'columns': len(df.columns),
                'numeric_columns': len(df.select_dtypes(include=['number']).columns)
            }
        }
        
    except Exception as e:
        return {'success': False, 'message': f"File processing error: {str(e)}"}

@app.route('/extract_keywords', methods=['POST'])
def extract_keywords():
    """Extract keywords using GenAI."""
    try:
        data = request.get_json()
        
        qualitative_text = data.get('qualitative_text', '')
        industry_context = data.get('industry_context', '')
        service = data.get('service', 'openai')
        api_key = data.get('api_key', '')
        
        if not qualitative_text or not industry_context or not api_key:
            return jsonify({'error': 'Missing required data'}), 400
        
        # Start keyword extraction in background
        session_id = session.get('upload_session_id')
        if not session_id:
            return jsonify({'error': 'No active session'}), 400
        
        # Run extraction
        result = interface.genai_extractor.extract_keywords(
            qualitative_text=qualitative_text,
            industry_context=industry_context,
            service=service,
            api_key=api_key
        )
        
        return jsonify({
            'success': result.success,
            'keywords': result.keywords,
            'message': result.message,
            'processing_time': result.processing_time
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_analysis', methods=['POST'])
def generate_analysis():
    """Generate perceptual mapping analysis."""
    try:
        data = request.get_json()
        
        # Get session data (optional for direct API calls)
        session_id = session.get('upload_session_id')
        if session_id and session_id in interface.active_sessions:
            session_data = interface.active_sessions[session_id]
        else:
            # Allow direct API calls without session
            session_data = {'data': {}}
        
        # Validate we have required data
        if not data.get('quantitative_data'):
            return jsonify({'error': 'No quantitative data provided'}), 400
        
        # Convert to DataFrame
        df = pd.DataFrame(data['quantitative_data'])
        
        # Fix column naming for compatibility - flexible product name detection
        def find_product_column(df):
            """Find the most likely product name column."""
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
        
        # Rename the product column to phone_model for analyzer compatibility
        product_col = find_product_column(df)
        if product_col and product_col != 'phone_model':
            df = df.rename(columns={product_col: 'phone_model'})
        
        # Ensure required columns exist for analyzer compatibility
        if 'phone_model' not in df.columns:
            # Use first string column as phone_model
            string_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
            if string_cols:
                df = df.rename(columns={string_cols[0]: 'phone_model'})
        
        if 'brand' not in df.columns:
            # Create a brand column from phone_model or use a default
            if 'phone_model' in df.columns:
                df['brand'] = df['phone_model'].apply(lambda x: str(x).split()[0] if pd.notnull(x) else 'Unknown')
            else:
                df['brand'] = 'Unknown'
        
        if 'tier' not in df.columns:
            # Add a default tier column
            df['tier'] = 'Standard'
        
        # Set matplotlib backend for web use
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
        
        # Import and create data-driven analyzer
        from data_driven_analyzer import DataDrivenAnalyzer
        analyzer = DataDrivenAnalyzer(df)
        
        # Get available dimensions (automatically detected)
        dimensions = analyzer.get_available_dimensions()
        
        # Generate analysis summary (data-driven)
        analysis_summary = analyzer.get_analysis_summary()
        analysis_summary['session_id'] = session_id
        
        return jsonify({
            'success': True,
            'analysis_summary': analysis_summary,
            'available_dimensions': dimensions,
            'message': f'Analysis ready: {len(dimensions)} dimensions available'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/create_map', methods=['POST'])
def create_map():
    """Create specific perceptual map."""
    print("🚨 CREATE MAP ROUTE CALLED!")  # Force debug output
    try:
        data = request.get_json()
        print(f"🚨 Raw request data keys: {data.keys() if data else 'None'}")
        
        x_dimension = data.get('x_dimension')
        y_dimension = data.get('y_dimension')
        quantitative_data = data.get('quantitative_data')
        
        if not all([x_dimension, y_dimension, quantitative_data]):
            return jsonify({'error': 'Missing required parameters'}), 400
        
        # Create DataFrame - let DataDrivenAnalyzer handle all preprocessing
        df = pd.DataFrame(quantitative_data)
        
        print(f"🌐 Web Interface FULL Debug:")
        print(f"   📊 Received {len(df)} rows, {len(df.columns)} columns")
        print(f"   📋 Columns: {df.columns.tolist()}")
        print(f"   📈 ALL data:\n{df.to_string()}")
        print(f"   🔍 Data types:\n{df.dtypes}")
        
        # Check for specific issues
        if x_dimension in df.columns and y_dimension in df.columns:
            print(f"   📊 {x_dimension} values: {df[x_dimension].tolist()}")
            print(f"   📊 {y_dimension} values: {df[y_dimension].tolist()}")
            print(f"   📈 {x_dimension} range: {df[x_dimension].min()} to {df[x_dimension].max()}")
            print(f"   📈 {y_dimension} range: {df[y_dimension].min()} to {df[y_dimension].max()}")
            print(f"   🎯 Unique {x_dimension} values: {df[x_dimension].nunique()}")
            print(f"   🎯 Unique {y_dimension} values: {df[y_dimension].nunique()}")
            print(f"   📊 Actual unique {x_dimension}: {sorted(df[x_dimension].unique())}")
            print(f"   📊 Actual unique {y_dimension}: {sorted(df[y_dimension].unique())}")
        
        # Set matplotlib backend for web use
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
        
        # Create data-driven analyzer - let IT handle all preprocessing
        from data_driven_analyzer import DataDrivenAnalyzer
        analyzer = DataDrivenAnalyzer(df)
        
        print(f"   ✅ Analyzer created successfully")
        print(f"   📊 Processed data: {len(analyzer.processed_data)} rows")
        print(f"   📋 Processed columns: {analyzer.processed_data.columns.tolist()}")
        
        # Debug processed data for the specific dimensions
        if x_dimension in analyzer.processed_data.columns and y_dimension in analyzer.processed_data.columns:
            print(f"   🔧 PROCESSED {x_dimension} values: {analyzer.processed_data[x_dimension].tolist()}")
            print(f"   🔧 PROCESSED {y_dimension} values: {analyzer.processed_data[y_dimension].tolist()}")
            print(f"   📈 PROCESSED {x_dimension} range: {analyzer.processed_data[x_dimension].min()} to {analyzer.processed_data[x_dimension].max()}")
            print(f"   📈 PROCESSED {y_dimension} range: {analyzer.processed_data[y_dimension].min()} to {analyzer.processed_data[y_dimension].max()}")
            
            # Show sample coordinate pairs
            print(f"   📍 Sample coordinates:")
            for i in range(min(5, len(analyzer.processed_data))):
                row = analyzer.processed_data.iloc[i]
                print(f"     {i+1}. {row.get('phone_model', 'Unknown')}: ({row[x_dimension]}, {row[y_dimension]})")
        
        # Get valid dimensions (automatically detected)
        valid_dimensions = analyzer.get_available_dimensions()
        
        if x_dimension not in valid_dimensions:
            return jsonify({'error': f'X dimension "{x_dimension}" not found in valid dimensions: {valid_dimensions}'}), 400
        
        if y_dimension not in valid_dimensions:
            return jsonify({'error': f'Y dimension "{y_dimension}" not found in valid dimensions: {valid_dimensions}'}), 400
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{x_dimension}_vs_{y_dimension}_{timestamp}.png"
        filepath = os.path.join('results', filename)
        
        # Ensure results directory exists
        os.makedirs('results', exist_ok=True)
        
        # Create map using data-driven analyzer
        import matplotlib.pyplot as plt
        
        fig, ax = analyzer.create_perceptual_map(
            x_dimension, 
            y_dimension,
            save_path=filepath
        )
        
        plt.close(fig)  # Close figure to prevent display issues
        
        return jsonify({
            'success': True,
            'map_file': filename,
            'map_url': f'/view_map/{filename}',
            'message': f'Map created: {x_dimension} vs {y_dimension}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/view_map/<filename>')
def view_map(filename):
    """Serve generated map images."""
    try:
        return send_from_directory('results', filename)
    except FileNotFoundError:
        return "Map not found", 404

@app.route('/list_maps')
def list_maps():
    """List all available generated maps."""
    try:
        results_dir = 'results'
        if not os.path.exists(results_dir):
            return jsonify({'maps': []})
        
        maps = []
        for filename in os.listdir(results_dir):
            if filename.endswith('.png'):
                filepath = os.path.join(results_dir, filename)
                stats = os.stat(filepath)
                maps.append({
                    'filename': filename,
                    'created': datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                    'url': f'/view_map/{filename}'
                })
        
        # Sort by creation time, most recent first
        maps.sort(key=lambda x: x['created'], reverse=True)
        return jsonify({'maps': maps})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# HTML Template (would typically be in templates/upload_interface.html)
UPLOAD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Perceptual Mapping Data Upload</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .step { margin-bottom: 30px; padding: 20px; border: 2px solid #e0e0e0; border-radius: 8px; }
        .step.active { border-color: #4CAF50; }
        .step.completed { border-color: #4CAF50; background-color: #f8fff8; }
        .step-header { font-size: 1.4em; font-weight: bold; margin-bottom: 10px; color: #333; }
        .progress-bar { width: 100%; height: 20px; background: #e0e0e0; border-radius: 10px; overflow: hidden; margin: 10px 0; }
        .progress-fill { height: 100%; background: #4CAF50; transition: width 0.3s; }
        .word-counter { font-size: 0.9em; color: #666; margin-top: 5px; }
        .warning { color: #ff6600; }
        .error { color: #ff0000; }
        .success { color: #4CAF50; }
        textarea { width: 100%; min-height: 200px; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-family: monospace; }
        input[type="text"], input[type="password"], select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; margin: 5px 0; }
        button { background: #4CAF50; color: white; border: none; padding: 12px 20px; border-radius: 4px; cursor: pointer; font-size: 1em; }
        button:hover { background: #45a049; }
        button:disabled { background: #ccc; cursor: not-allowed; }
        .file-drop { border: 2px dashed #ccc; border-radius: 8px; padding: 40px; text-align: center; color: #666; margin: 10px 0; }
        .file-drop.dragover { border-color: #4CAF50; background: #f8fff8; }
        .hidden { display: none; }
        .keyword-list { display: flex; flex-wrap: wrap; gap: 5px; margin: 10px 0; }
        .keyword-tag { background: #e3f2fd; padding: 5px 10px; border-radius: 15px; font-size: 0.9em; }
        .analysis-summary { background: #f0f8ff; padding: 15px; border-radius: 8px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 Perceptual Mapping Data Upload System</h1>
        <p>Upload your research data to generate perceptual maps and competitive analysis.</p>
        
        <!-- Step 1: Qualitative Data -->
        <div class="step active" id="step1">
            <div class="step-header">📝 Step 1: Qualitative Data Upload</div>
            <p><strong>Requirements:</strong> 100 - 5,000 words (recommended: 500 - 2,000)</p>
            
            <div class="file-drop" id="qualitative-drop">
                <p>📁 Drag & drop text files here or click to browse</p>
                <input type="file" id="qualitative-file" accept=".txt" style="display: none;">
                <button onclick="document.getElementById('qualitative-file').click()">Browse Files</button>
            </div>
            
            <p><strong>Or paste text directly:</strong></p>
            <textarea id="qualitative-text" placeholder="Paste your qualitative research data here (interviews, discussions, Reddit posts, etc.)..."></textarea>
            
            <div class="progress-bar">
                <div class="progress-fill" id="text-progress" style="width: 0%;"></div>
            </div>
            <div class="word-counter" id="word-counter">0 words</div>
            
            <button id="validate-text-btn">Validate Text</button>
        </div>
        
        <!-- Step 2: Industry Context -->
        <div class="step" id="step2">
            <div class="step-header">🏭 Step 2: Industry & Product Context</div>
            <p><strong>Limit:</strong> 500 characters</p>
            
            <input type="text" id="industry-context" placeholder="Describe your industry and product category..." maxlength="500">
            <div class="word-counter" id="context-counter">0/500 characters</div>
            
            <button id="save-context-btn">Save Context</button>
        </div>
        
        <!-- Step 3: Keyword Extraction -->
        <div class="step" id="step3">
            <div class="step-header">🤖 Step 3: AI Keyword Extraction</div>
            <p><strong>🔒 Security:</strong> API keys processed in-memory only, never stored</p>
            
            <select id="genai-service">
                <option value="openai">OpenAI GPT</option>
                <option value="anthropic">Anthropic Claude</option>
                <option value="google">Google Gemini</option>
            </select>
            
            <input type="password" id="api-key" placeholder="Enter your API key (will be cleared after use)">
            
            <button id="extract-keywords-btn">Extract Keywords</button>
            
            <div id="keywords-result" class="hidden">
                <p><strong>Extracted Keywords:</strong></p>
                <div class="keyword-list" id="keyword-list"></div>
            </div>
        </div>
        
        <!-- Step 4: Quantitative Data -->
        <div class="step" id="step4">
            <div class="step-header">📊 Step 4: Quantitative Survey Data</div>
            <p><strong>Requirements:</strong> 30+ respondents, 3-20 questions, 1-9 rating scale</p>
            
            <div class="file-drop" id="quantitative-drop">
                <p>📊 Drag & drop CSV/JSON files here or click to browse</p>
                <input type="file" id="quantitative-file" accept=".csv,.json" style="display: none;">
                <button onclick="document.getElementById('quantitative-file').click()">Browse Files</button>
            </div>
            
            <div id="quantitative-summary" class="analysis-summary hidden">
                <h4>Data Summary:</h4>
                <div id="data-summary-content"></div>
            </div>
        </div>
        
        <!-- Step 5: Generate Analysis -->
        <div class="step" id="step5">
            <div class="step-header">🎯 Step 5: Generate Analysis</div>
            
            <button id="generate-analysis-btn" disabled>Generate Perceptual Maps</button>
            
            <div id="analysis-options" class="hidden">
                <h4>Select Dimensions for Perceptual Map:</h4>
                <select id="x-dimension"></select>
                <select id="y-dimension"></select>
                <button id="create-map-btn">Create Map</button>
            </div>
            
            <div id="final-results" class="analysis-summary hidden">
                <h4>🎉 Analysis Complete!</h4>
                <div id="results-content"></div>
            </div>
        </div>
    </div>
    
    <script>
        // Real-time text validation
        document.getElementById('qualitative-text').addEventListener('input', function() {
            const text = this.value;
            const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0;
            
            // Update counter
            document.getElementById('word-counter').textContent = wordCount.toLocaleString() + ' words';
            
            // Update progress bar
            const progress = Math.min(100, (wordCount / 2000) * 100);
            document.getElementById('text-progress').style.width = progress + '%';
            
            // Real-time validation
            fetch('/validate_text', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({text: text})
            })
            .then(response => response.json())
            .then(data => {
                const counter = document.getElementById('word-counter');
                counter.className = 'word-counter ' + data.status;
                counter.textContent = data.message;
                
                if (data.warnings && data.warnings.length > 0) {
                    counter.textContent += ' (' + data.warnings.join(', ') + ')';
                }
            });
        });
        
        // Industry context character counter
        document.getElementById('industry-context').addEventListener('input', function() {
            const length = this.value.length;
            document.getElementById('context-counter').textContent = length + '/500 characters';
        });
        
        // File upload handling
        function setupFileUpload(dropId, fileId, fileType) {
            const dropZone = document.getElementById(dropId);
            const fileInput = document.getElementById(fileId);
            
            dropZone.addEventListener('dragover', function(e) {
                e.preventDefault();
                this.classList.add('dragover');
            });
            
            dropZone.addEventListener('dragleave', function(e) {
                e.preventDefault();
                this.classList.remove('dragover');
            });
            
            dropZone.addEventListener('drop', function(e) {
                e.preventDefault();
                this.classList.remove('dragover');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    handleFileUpload(files[0], fileType);
                }
            });
            
            fileInput.addEventListener('change', function() {
                if (this.files.length > 0) {
                    handleFileUpload(this.files[0], fileType);
                }
            });
        }
        
        function handleFileUpload(file, fileType) {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('file_type', fileType);
            
            fetch('/upload_file', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (fileType === 'qualitative') {
                        document.getElementById('qualitative-text').value = data.data;
                        document.getElementById('qualitative-text').dispatchEvent(new Event('input'));
                    } else if (fileType === 'quantitative') {
                        displayQuantitativeData(data);
                    }
                } else {
                    alert('Error: ' + data.message);
                }
            });
        }
        
        function displayQuantitativeData(data) {
            const summary = document.getElementById('quantitative-summary');
            const content = document.getElementById('data-summary-content');
            
            content.innerHTML = 
                '<p><strong>Rows:</strong> ' + data.summary.rows.toLocaleString() + '</p>' +
                '<p><strong>Columns:</strong> ' + data.summary.columns + '</p>' +
                '<p><strong>Numeric Columns:</strong> ' + data.summary.numeric_columns + '</p>' +
                (data.warnings.length > 0 ? '<p class="warning"><strong>Warnings:</strong> ' + data.warnings.join(', ') + '</p>' : '');
            
            summary.classList.remove('hidden');
            
            // Store data for analysis
            window.quantitativeData = data.data;
            
            // Enable analysis generation
            document.getElementById('generate-analysis-btn').disabled = false;
        }
        
        // Setup file uploads
        setupFileUpload('qualitative-drop', 'qualitative-file', 'qualitative');
        setupFileUpload('quantitative-drop', 'quantitative-file', 'quantitative');
        
        // Keyword extraction
        document.getElementById('extract-keywords-btn').addEventListener('click', function() {
            const qualitativeText = document.getElementById('qualitative-text').value;
            const industryContext = document.getElementById('industry-context').value;
            const service = document.getElementById('genai-service').value;
            const apiKey = document.getElementById('api-key').value;
            
            if (!qualitativeText || !industryContext || !apiKey) {
                alert('Please fill in all required fields');
                return;
            }
            
            this.textContent = 'Extracting...';
            this.disabled = true;
            
            fetch('/extract_keywords', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    qualitative_text: qualitativeText,
                    industry_context: industryContext,
                    service: service,
                    api_key: apiKey
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const keywordList = document.getElementById('keyword-list');
                    keywordList.innerHTML = '';
                    
                    data.keywords.forEach(keyword => {
                        const tag = document.createElement('span');
                        tag.className = 'keyword-tag';
                        tag.textContent = keyword;
                        keywordList.appendChild(tag);
                    });
                    
                    document.getElementById('keywords-result').classList.remove('hidden');
                } else {
                    alert('Keyword extraction failed: ' + data.message);
                }
            })
            .finally(() => {
                this.textContent = 'Extract Keywords';
                this.disabled = false;
                // Clear API key for security
                document.getElementById('api-key').value = '';
            });
        });
        
        // Generate analysis
        document.getElementById('generate-analysis-btn').addEventListener('click', function() {
            if (!window.quantitativeData) {
                alert('Please upload quantitative data first');
                return;
            }
            
            this.textContent = 'Generating...';
            this.disabled = true;
            
            fetch('/generate_analysis', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    quantitative_data: window.quantitativeData
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Populate dimension selectors
                    const xSelect = document.getElementById('x-dimension');
                    const ySelect = document.getElementById('y-dimension');
                    
                    xSelect.innerHTML = '';
                    ySelect.innerHTML = '';
                    
                    data.available_dimensions.forEach(dim => {
                        const option1 = new Option(dim.replace('_', ' '), dim);
                        const option2 = new Option(dim.replace('_', ' '), dim);
                        xSelect.add(option1);
                        ySelect.add(option2);
                    });
                    
                    document.getElementById('analysis-options').classList.remove('hidden');
                } else {
                    alert('Analysis generation failed: ' + data.error);
                }
            })
            .finally(() => {
                this.textContent = 'Generate Perceptual Maps';
                this.disabled = false;
            });
        });
        
        // Create specific map
        document.getElementById('create-map-btn').addEventListener('click', function() {
            const xDim = document.getElementById('x-dimension').value;
            const yDim = document.getElementById('y-dimension').value;
            
            if (xDim === yDim) {
                alert('Please select different dimensions for X and Y axes');
                return;
            }
            
            this.textContent = 'Creating Map...';
            this.disabled = true;
            
            fetch('/create_map', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    x_dimension: xDim,
                    y_dimension: yDim,
                    quantitative_data: window.quantitativeData
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const results = document.getElementById('results-content');
                    results.innerHTML += '<p>✅ ' + data.message + '</p>';
                    
                    // Display the generated map
                    if (data.map_url) {
                        results.innerHTML += `
                            <div style="margin-top: 20px; text-align: center;">
                                <img src="${data.map_url}" alt="Perceptual Map" style="max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 8px;">
                            </div>
                        `;
                    }
                    
                    document.getElementById('final-results').classList.remove('hidden');
                } else {
                    alert('Map creation failed: ' + data.error);
                }
            })
            .finally(() => {
                this.textContent = 'Create Map';
                this.disabled = false;
            });
        });
    </script>
</body>
</html>
"""

@app.template_global()
def render_upload_interface():
    """Render the upload interface template."""
    return UPLOAD_TEMPLATE

# Create templates directory and save template
def setup_templates():
    """Setup Flask templates directory."""
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    template_path = os.path.join(templates_dir, 'upload_interface.html')
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(UPLOAD_TEMPLATE)

def run_interface():
    """Run the enhanced upload interface."""
    print("🌐 Starting Enhanced Upload Interface")
    print("🔗 Access at: http://localhost:8080")
    print("🔒 Security: All credentials handled in-memory only")
    print("\n" + "=" * 50)
    
    # Setup templates
    setup_templates()
    
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=8080)

if __name__ == "__main__":
    run_interface()