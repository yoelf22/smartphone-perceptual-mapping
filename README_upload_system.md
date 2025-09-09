# 📊 Interactive Data Upload System for Perceptual Mapping

Complete data upload and validation system with real-time monitoring, secure GenAI integration, and automated analysis generation.

## 🚀 Quick Start

### Option 1: Web Interface (Recommended)
```bash
pip install -r requirements_upload.txt
python enhanced_upload_interface.py
# Opens http://localhost:5000
```

### Option 2: Command Line Interface
```bash
python data_upload_system.py
# Interactive command-line session
```

## 📋 Features

### ✅ Data Input & Validation
- **Qualitative Data**: Text files, direct input, Reddit dumps
- **Quantitative Data**: CSV/JSON from Google Forms, SurveyMonkey
- **Real-time validation** with progress tracking
- **Word count monitoring** (100-5,000 words)
- **Drag & drop file uploads**

### 🤖 Secure GenAI Integration
- **Multi-service support**: OpenAI GPT, Anthropic Claude, Google Gemini
- **Keyword extraction** from qualitative data
- **In-memory credential handling** (never stored)
- **Automatic cleanup** after processing

### 📊 Analysis Generation
- **Perceptual map creation** with custom axis selection
- **Correlation analysis** between dimensions
- **Competitive positioning** insights
- **Bubble sizing** based on popularity/market share

## 📁 Data Requirements

### 1. Qualitative Data
**Word Count**: 100 - 5,000 words (recommended: 500-2,000)
**Sources**: 
- Interview summaries
- Focus group transcripts  
- Reddit/social media discussions
- User feedback collections

**Example Input**:
```
Users consistently mention camera quality as their top priority.
Battery life is crucial for daily usage patterns.
Performance matters for gaming and multitasking.
Price value is important for younger demographics.
```

### 2. Industry Context
**Character Limit**: 500 characters
**Content**: Market segment, target audience, key competitors

**Example**:
```
Premium smartphone market targeting professionals aged 25-45. 
Key competitors include Apple, Samsung, Google. Focus on camera 
quality, performance, and business features.
```

### 3. Quantitative Survey Data
**Requirements**:
- **Respondents**: 30 - 10,000 (recommended: 100+)
- **Questions**: 3 - 20 rating questions  
- **Scale**: 1-9 rating system
- **Format**: CSV or JSON

**CSV Example**:
```csv
product_name,brand,camera_quality,battery_life,performance,price_value
iPhone 15 Pro,Apple,8,7,9,4
Samsung S24,Samsung,9,8,8,6
Google Pixel 8,Google,8,7,8,7
```

**JSON Example**:
```json
{
  "responses": [
    {"product_name": "iPhone 15 Pro", "camera_quality": 8, "battery_life": 7},
    {"product_name": "Samsung S24", "camera_quality": 9, "battery_life": 8}
  ]
}
```

## 🔐 Security Features

### Credential Handling
- **In-memory processing**: API keys never stored to disk
- **Automatic clearing**: Credentials wiped after use
- **No logging**: No sensitive data in logs
- **Secure transmission**: HTTPS for all API calls

### Data Privacy
- **Local processing**: All data processed locally
- **No cloud storage**: Files processed and cleaned immediately
- **Session isolation**: Each upload session is independent

## 🎯 Complete Upload Sequence

### Step 1: Qualitative Data Upload
1. **File Upload** or **Direct Input**
2. **Real-time validation** with word count
3. **Progress tracking** with visual feedback
4. **Content quality assessment**

### Step 2: Industry Context
1. **Industry description** (500 char limit)
2. **Product category** specification
3. **Target market** definition
4. **Competitive landscape** overview

### Step 3: AI Keyword Extraction
1. **Service selection** (OpenAI/Anthropic/Google)
2. **Secure API key input** (hidden, not stored)
3. **Automated extraction** of key dimensions
4. **Keyword validation** and cleaning

### Step 4: Quantitative Data Upload
1. **CSV/JSON file upload** with validation
2. **Respondent count** verification (30-10,000)
3. **Rating scale** validation (1-9)
4. **Data structure** analysis

### Step 5: Analysis Generation
1. **Dimension identification** from data
2. **Axis selection** interface
3. **Perceptual map creation** 
4. **Results export** and visualization

## 🛠️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 Web Interface                           │
│  (Real-time validation, drag & drop, progress bars)    │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│              Data Upload System                         │
│  • Text validation     • File processing               │
│  • Industry context    • Session management            │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│           Secure GenAI Integration                      │
│  • Multi-service support  • Credential security        │
│  • Keyword extraction     • Automatic cleanup          │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│           Perceptual Map Analyzer                       │
│  • Map generation      • Correlation analysis          │
│  • Competitive insights • Export capabilities          │
└─────────────────────────────────────────────────────────┘
```

## 🔧 Configuration Options

### Validation Limits
```python
QUALITATIVE_WORD_LIMITS = {
    'min_words': 100,
    'max_words': 5000,
    'recommended_min': 500,
    'recommended_max': 2000
}

QUANTITATIVE_LIMITS = {
    'min_respondents': 30,
    'max_respondents': 10000,
    'min_questions': 3,
    'max_questions': 20,
    'rating_scale': (1, 9)
}
```

### GenAI Services
```python
SUPPORTED_SERVICES = {
    'openai': 'OpenAI GPT-3.5/4',
    'anthropic': 'Anthropic Claude',
    'google': 'Google Gemini Pro'
}
```

## 📈 Usage Analytics

The system tracks:
- **Session completion rates**
- **Data quality metrics** 
- **Processing times**
- **Error patterns**

## 🚨 Error Handling

### Common Issues & Solutions

**Qualitative Data**:
- *Too short*: Add more interview content or discussion excerpts
- *Too long*: Focus on key insights, remove filler content
- *Poor quality*: Ensure complete sentences and meaningful content

**Quantitative Data**:
- *Too few respondents*: Collect more survey responses (minimum 30)
- *Wrong scale*: Convert ratings to 1-9 scale before upload
- *Missing columns*: Ensure product names and rating columns are present

**GenAI Extraction**:
- *API errors*: Verify API key validity and service quotas
- *No keywords*: Check qualitative data quality and industry context
- *Service unavailable*: Try alternative GenAI service

## 💡 Best Practices

### Data Collection
1. **Survey Design**: Use 1-9 scales for better granularity than 1-5
2. **Sample Size**: Target 100+ respondents for reliable results
3. **Question Balance**: 8-12 dimensions optimal for perceptual maps
4. **Demographics**: Ensure representative sample of target market

### Qualitative Research
1. **Interview Length**: 30-60 minutes per participant
2. **Question Types**: Mix of open-ended and probing questions
3. **Transcription**: Include exact quotes, not summaries
4. **Content Volume**: 500-2,000 words provides optimal insights

### Analysis Setup
1. **Dimension Selection**: Choose complementary axes (avoid correlations)
2. **Market Context**: Include competitive products for benchmarking
3. **Popularity Data**: Add market share or brand awareness scores
4. **Validation**: Cross-check results with market knowledge

## 📞 Support & Troubleshooting

### Logs & Debugging
- Session logs saved in `session_data/` directory
- Error messages provide specific validation details
- Processing times tracked for performance monitoring

### File Format Issues
- Use UTF-8 encoding for international characters
- Ensure CSV headers match expected column names
- JSON arrays should contain consistent object structures

---

**🎯 Ready to transform your research data into actionable perceptual maps!**

Start with: `python enhanced_upload_interface.py` and open http://localhost:5000