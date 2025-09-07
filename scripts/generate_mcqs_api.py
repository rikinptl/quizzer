#!/usr/bin/env python3
"""
Generate MCQs using Ollama API (external service)
This script calls Ollama running on a remote server or cloud service
"""

import requests
import json
import sys
import os
import argparse
import logging
from typing import Dict, Any, List

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OllamaAPIClient:
    """Client for interacting with Ollama API"""
    
    def __init__(self, base_url: str = None, api_key: str = None):
        """
        Initialize Ollama API client
        
        Args:
            base_url: Base URL for Ollama API (default: localhost)
            api_key: API key for authentication (if required)
        """
        self.base_url = base_url or os.getenv('OLLAMA_API_URL', 'http://localhost:11434')
        self.api_key = api_key or os.getenv('OLLAMA_API_KEY')
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({'Authorization': f'Bearer {self.api_key}'})
    
    def generate_text(self, model: str, prompt: str, **kwargs) -> str:
        """
        Generate text using Ollama API
        
        Args:
            model: Model name (e.g., 'llama2')
            prompt: Input prompt
            **kwargs: Additional parameters (temperature, top_p, etc.)
            
        Returns:
            Generated text
        """
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            **kwargs
        }
        
        try:
            response = self.session.post(url, json=payload, timeout=300)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '')
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse API response: {e}")
            raise
    
    def list_models(self) -> List[str]:
        """List available models"""
        url = f"{self.base_url}/api/tags"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return [model['name'] for model in result.get('models', [])]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to list models: {e}")
            return []

def create_mcq_prompt(text: str, difficulty: str, num_questions: int) -> str:
    """Create a structured prompt for MCQ generation"""
    
    prompt = f"""You are an expert educational content creator. Generate {num_questions} high-quality multiple choice questions from the provided text content.

## Instructions:
- Difficulty Level: {difficulty}
- Create questions that test understanding, not just memorization
- Each question must have exactly 4 options (A, B, C, D)
- Only one correct answer per question
- Make distractors plausible but clearly incorrect
- Provide educational explanations that teach concepts

## Difficulty Guidelines:
- **Easy**: Basic recall, definitions, simple concepts
- **Medium**: Application of concepts, analysis, moderate complexity
- **Hard**: Synthesis, evaluation, complex reasoning, critical thinking

## Output Format:
Return ONLY a valid JSON array with this exact structure:

```json
[
  {{
    "question": "What is the main purpose of photosynthesis?",
    "options": [
      "A) To produce oxygen for animals",
      "B) To convert sunlight into chemical energy",
      "C) To remove carbon dioxide from the atmosphere",
      "D) To create water molecules"
    ],
    "correct_answer": "B",
    "explanation": "Photosynthesis primarily converts light energy into chemical energy (glucose), which plants use for growth and metabolism. While it does produce oxygen as a byproduct, that's not its main purpose."
  }}
]
```

## Text Content:
{text}

Generate {num_questions} questions now. Return only the JSON array, no additional text."""

    return prompt

def generate_mcqs_with_api(text: str, difficulty: str, num_questions: int, 
                          model: str = "llama2", api_url: str = None) -> List[Dict[str, Any]]:
    """
    Generate MCQs using Ollama API
    
    Args:
        text: Extracted text content
        difficulty: Difficulty level (easy/medium/hard)
        num_questions: Number of questions to generate
        model: Ollama model to use
        api_url: Custom API URL
        
    Returns:
        List of MCQ dictionaries
    """
    client = OllamaAPIClient(base_url=api_url)
    
    # Create prompt
    prompt = create_mcq_prompt(text, difficulty, num_questions)
    
    logger.info(f"Generating {num_questions} MCQs with difficulty {difficulty}")
    
    # Generate MCQs
    response = client.generate_text(
        model=model,
        prompt=prompt,
        temperature=0.7,
        top_p=0.9,
        top_k=40
    )
    
    logger.info("MCQ generation completed")
    
    # Parse JSON response
    try:
        # Clean response (remove markdown formatting if present)
        response = response.strip()
        if response.startswith('```json'):
            response = response[7:]
        if response.endswith('```'):
            response = response[:-3]
        
        mcqs = json.loads(response)
        
        if not isinstance(mcqs, list):
            raise ValueError("Response is not a JSON array")
        
        logger.info(f"Successfully parsed {len(mcqs)} MCQs")
        return mcqs
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        logger.error(f"Raw response: {response[:500]}...")
        raise
    except Exception as e:
        logger.error(f"Error processing response: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Generate MCQs using Ollama API')
    parser.add_argument('filename', help='Original filename')
    parser.add_argument('difficulty', help='Difficulty level')
    parser.add_argument('num_questions', help='Number of questions')
    parser.add_argument('--model', default='llama2', help='Ollama model to use')
    parser.add_argument('--api-url', help='Custom Ollama API URL')
    
    args = parser.parse_args()
    
    try:
        # Read extracted text
        if not os.path.exists('extracted_text.txt'):
            logger.error("extracted_text.txt not found")
            sys.exit(1)
        
        with open('extracted_text.txt', 'r', encoding='utf-8') as f:
            text = f.read()
        
        if not text.strip():
            logger.error("No text content found")
            sys.exit(1)
        
        # Generate MCQs
        mcqs = generate_mcqs_with_api(
            text=text,
            difficulty=args.difficulty,
            num_questions=int(args.num_questions),
            model=args.model,
            api_url=args.api_url
        )
        
        # Save results
        with open('mcq_output.json', 'w', encoding='utf-8') as f:
            json.dump(mcqs, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Generated {len(mcqs)} MCQs and saved to mcq_output.json")
        
    except Exception as e:
        logger.error(f"Failed to generate MCQs: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
