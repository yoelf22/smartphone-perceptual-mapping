#!/usr/bin/env python3
"""
Secure GenAI Integration Module
==============================

Handles secure integration with various GenAI services for keyword extraction.
Supports OpenAI GPT, Anthropic Claude, and Google Gemini.

Security Features:
- In-memory only credential handling
- No storage or logging of API keys
- Automatic credential clearing
- Secure prompt handling

Usage:
    from genai_integration import GenAIExtractor
    
    extractor = GenAIExtractor()
    keywords = extractor.extract_keywords(text, context, service='openai', api_key=key)
"""

import os
import json
import requests
import time
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import logging

# Disable logging for security
logging.getLogger().setLevel(logging.CRITICAL)

@dataclass
class ExtractionResult:
    """Result of keyword extraction."""
    success: bool
    keywords: List[str]
    message: str
    processing_time: float = 0.0

class GenAIExtractor:
    """Secure GenAI integration for keyword extraction."""
    
    SUPPORTED_SERVICES = {
        'openai': {
            'name': 'OpenAI GPT',
            'endpoint': 'https://api.openai.com/v1/chat/completions',
            'model': 'gpt-3.5-turbo'
        },
        'anthropic': {
            'name': 'Anthropic Claude',
            'endpoint': 'https://api.anthropic.com/v1/messages',
            'model': 'claude-3-haiku-20240307'
        },
        'google': {
            'name': 'Google Gemini',
            'endpoint': 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent',
            'model': 'gemini-pro'
        }
    }
    
    def __init__(self):
        """Initialize the extractor."""
        self._active_credentials = None
        
    def extract_keywords(self, 
                        qualitative_text: str, 
                        industry_context: str, 
                        service: str, 
                        api_key: str,
                        max_keywords: int = 12) -> ExtractionResult:
        """
        Extract keywords using specified GenAI service.
        
        Args:
            qualitative_text: The qualitative research text
            industry_context: Industry and product context
            service: Service identifier ('openai', 'anthropic', 'google')
            api_key: API key for the service
            max_keywords: Maximum number of keywords to extract
            
        Returns:
            ExtractionResult with keywords and metadata
        """
        start_time = time.time()
        
        try:
            # Store credentials temporarily
            self._active_credentials = api_key
            
            # Validate service
            if service not in self.SUPPORTED_SERVICES:
                return ExtractionResult(
                    False, 
                    [], 
                    f"Unsupported service: {service}"
                )
            
            # Create extraction prompt
            prompt = self._create_extraction_prompt(
                qualitative_text, 
                industry_context, 
                max_keywords
            )
            
            # Call appropriate service
            if service == 'openai':
                result = self._call_openai(prompt, api_key)
            elif service == 'anthropic':
                result = self._call_anthropic(prompt, api_key)
            elif service == 'google':
                result = self._call_google(prompt, api_key)
            else:
                result = ExtractionResult(False, [], "Service not implemented")
            
            # Add processing time
            result.processing_time = time.time() - start_time
            
            return result
            
        except Exception as e:
            return ExtractionResult(
                False,
                [],
                f"Extraction failed: {str(e)}",
                time.time() - start_time
            )
        finally:
            # Always clear credentials
            self._clear_credentials()
    
    def _create_extraction_prompt(self, 
                                 qualitative_text: str, 
                                 industry_context: str, 
                                 max_keywords: int) -> str:
        """Create optimized prompt for keyword extraction."""
        
        # Truncate text if too long (API limits)
        max_text_length = 3000
        if len(qualitative_text) > max_text_length:
            qualitative_text = qualitative_text[:max_text_length] + "..."
        
        prompt = f"""You are an expert in perceptual mapping and market research. Analyze the following qualitative research data to extract key product attributes/dimensions that are important to users.

INDUSTRY CONTEXT:
{industry_context}

QUALITATIVE RESEARCH DATA:
{qualitative_text}

TASK:
Extract exactly {max_keywords} key product attributes that users care about most. These will be used for perceptual mapping analysis.

REQUIREMENTS:
1. Each attribute should be a measurable product characteristic
2. Use clear, actionable attribute names (e.g., "Camera_Quality", "Battery_Life")
3. Focus on attributes mentioned or implied by users
4. Avoid redundant or overlapping attributes
5. Prioritize attributes that differentiate products in this market

FORMAT YOUR RESPONSE EXACTLY AS:
1. Attribute_Name_1
2. Attribute_Name_2
3. Attribute_Name_3
...
{max_keywords}. Attribute_Name_{max_keywords}

Do not include explanations, descriptions, or additional text. Only provide the numbered list of attribute names."""

        return prompt
    
    def _call_openai(self, prompt: str, api_key: str) -> ExtractionResult:
        """Call OpenAI GPT API."""
        try:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.SUPPORTED_SERVICES['openai']['model'],
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': 300,
                'temperature': 0.3
            }
            
            response = requests.post(
                self.SUPPORTED_SERVICES['openai']['endpoint'],
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code != 200:
                return ExtractionResult(
                    False,
                    [],
                    f"OpenAI API error: {response.status_code}"
                )
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            keywords = self._parse_keywords_from_response(content)
            
            return ExtractionResult(
                True,
                keywords,
                f"Successfully extracted {len(keywords)} keywords via OpenAI"
            )
            
        except Exception as e:
            return ExtractionResult(False, [], f"OpenAI call failed: {str(e)}")
    
    def _call_anthropic(self, prompt: str, api_key: str) -> ExtractionResult:
        """Call Anthropic Claude API."""
        try:
            headers = {
                'x-api-key': api_key,
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            }
            
            data = {
                'model': self.SUPPORTED_SERVICES['anthropic']['model'],
                'max_tokens': 300,
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            }
            
            response = requests.post(
                self.SUPPORTED_SERVICES['anthropic']['endpoint'],
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code != 200:
                return ExtractionResult(
                    False,
                    [],
                    f"Anthropic API error: {response.status_code}"
                )
            
            result = response.json()
            content = result['content'][0]['text']
            
            keywords = self._parse_keywords_from_response(content)
            
            return ExtractionResult(
                True,
                keywords,
                f"Successfully extracted {len(keywords)} keywords via Anthropic"
            )
            
        except Exception as e:
            return ExtractionResult(False, [], f"Anthropic call failed: {str(e)}")
    
    def _call_google(self, prompt: str, api_key: str) -> ExtractionResult:
        """Call Google Gemini API."""
        try:
            url = f"{self.SUPPORTED_SERVICES['google']['endpoint']}?key={api_key}"
            
            data = {
                'contents': [
                    {
                        'parts': [
                            {
                                'text': prompt
                            }
                        ]
                    }
                ],
                'generationConfig': {
                    'maxOutputTokens': 300,
                    'temperature': 0.3
                }
            }
            
            response = requests.post(url, json=data, timeout=30)
            
            if response.status_code != 200:
                return ExtractionResult(
                    False,
                    [],
                    f"Google API error: {response.status_code}"
                )
            
            result = response.json()
            content = result['candidates'][0]['content']['parts'][0]['text']
            
            keywords = self._parse_keywords_from_response(content)
            
            return ExtractionResult(
                True,
                keywords,
                f"Successfully extracted {len(keywords)} keywords via Google"
            )
            
        except Exception as e:
            return ExtractionResult(False, [], f"Google call failed: {str(e)}")
    
    def _parse_keywords_from_response(self, response_text: str) -> List[str]:
        """Parse keywords from AI response."""
        keywords = []
        
        # Split into lines and look for numbered items
        lines = response_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for numbered format: "1. Keyword" or "1) Keyword"
            import re
            match = re.match(r'^\d+[\.\)]\s*(.+)', line)
            if match:
                keyword = match.group(1).strip()
                # Clean up the keyword
                keyword = re.sub(r'[^\w\s_]', '', keyword)  # Remove special chars
                keyword = keyword.replace(' ', '_')  # Replace spaces with underscores
                keywords.append(keyword)
            elif line and not any(char.isdigit() for char in line[:3]):
                # Handle cases where numbering might be missing
                keyword = line.strip()
                keyword = re.sub(r'[^\w\s_]', '', keyword)
                keyword = keyword.replace(' ', '_')
                if keyword:
                    keywords.append(keyword)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword not in seen:
                seen.add(keyword)
                unique_keywords.append(keyword)
        
        return unique_keywords[:12]  # Limit to max 12 keywords
    
    def _clear_credentials(self):
        """Clear credentials from memory."""
        if self._active_credentials:
            # Overwrite the credential string
            self._active_credentials = 'X' * len(self._active_credentials)
            self._active_credentials = None
    
    def get_supported_services(self) -> Dict[str, str]:
        """Get list of supported services."""
        return {
            service_id: config['name'] 
            for service_id, config in self.SUPPORTED_SERVICES.items()
        }

def test_extraction():
    """Test function for keyword extraction."""
    print("🧪 Testing GenAI Extraction")
    
    sample_text = """
    Users consistently mention that camera quality is their top priority when choosing a smartphone.
    Battery life is crucial for daily usage, with many preferring all-day battery performance.
    Performance and speed are important for gaming and multitasking.
    Price value matters significantly, especially for younger demographics.
    Build quality and premium feel influence purchase decisions.
    """
    
    sample_context = "Premium smartphone market targeting professionals aged 25-45"
    
    extractor = GenAIExtractor()
    
    print("📋 Supported services:")
    for service_id, name in extractor.get_supported_services().items():
        print(f"  • {service_id}: {name}")
    
    print(f"\n📝 Sample text length: {len(sample_text)} characters")
    print(f"📝 Context: {sample_context}")
    
    # Note: Actual testing would require real API keys
    print("\n⚠️  Note: Real testing requires valid API keys")
    print("   Use the main data upload system for actual extraction")

if __name__ == "__main__":
    test_extraction()