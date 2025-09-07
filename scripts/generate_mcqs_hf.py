#!/usr/bin/env python3
"""
Generate MCQs using Hugging Face Transformers API
This uses free Hugging Face inference endpoints
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

class HuggingFaceClient:
    """Client for Hugging Face Inference API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('HUGGINGFACE_API_KEY')
        self.base_url = "https://api-inference.huggingface.co/models"
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({'Authorization': f'Bearer {self.api_key}'})
    
    def generate_text(self, model: str, prompt: str, **kwargs) -> str:
        """Generate text using Hugging Face API"""
        url = f"{self.base_url}/{model}"
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 1000,
                "temperature": 0.7,
                "top_p": 0.9,
                "return_full_text": False,
                **kwargs
            }
        }
        
        try:
            response = self.session.post(url, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', '')
            else:
                return str(result)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to process response: {e}")
            raise

def create_mcq_prompt(text: str, difficulty: str, num_questions: int) -> str:
    """Create a structured prompt for MCQ generation"""
    
    # Truncate text if too long (Hugging Face has token limits)
    max_length = 2000
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    prompt = f"""Generate {num_questions} multiple choice questions from this text. Difficulty: {difficulty}.

Text: {text}

Format as JSON array:
[
  {{
    "question": "Question text?",
    "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
    "correct_answer": "A",
    "explanation": "Explanation here"
  }}
]

Generate {num_questions} questions:"""

    return prompt

def generate_mcqs_with_hf(text: str, difficulty: str, num_questions: int, 
                         model: str = "microsoft/DialoGPT-medium") -> List[Dict[str, Any]]:
    """
    Generate MCQs using Hugging Face API
    
    Args:
        text: Extracted text content
        difficulty: Difficulty level (easy/medium/hard)
        num_questions: Number of questions to generate
        model: Hugging Face model to use
        
    Returns:
        List of MCQ dictionaries
    """
    client = HuggingFaceClient()
    
    # Create prompt
    prompt = create_mcq_prompt(text, difficulty, num_questions)
    
    logger.info(f"Generating {num_questions} MCQs with difficulty {difficulty}")
    
    # Generate MCQs
    response = client.generate_text(
        model=model,
        prompt=prompt,
        max_new_tokens=1500,
        temperature=0.7
    )
    
    logger.info("MCQ generation completed")
    
    # Parse JSON response
    try:
        # Clean response
        response = response.strip()
        
        # Try to extract JSON from response
        if '[' in response and ']' in response:
            start = response.find('[')
            end = response.rfind(']') + 1
            json_str = response[start:end]
        else:
            json_str = response
        
        mcqs = json.loads(json_str)
        
        if not isinstance(mcqs, list):
            raise ValueError("Response is not a JSON array")
        
        logger.info(f"Successfully parsed {len(mcqs)} MCQs")
        return mcqs
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        logger.error(f"Raw response: {response[:500]}...")
        
        # Fallback: create a simple MCQ structure
        logger.info("Creating fallback MCQ structure")
        return create_fallback_mcqs(text, difficulty, num_questions)
        
    except Exception as e:
        logger.error(f"Error processing response: {e}")
        return create_fallback_mcqs(text, difficulty, num_questions)

def create_fallback_mcqs(text: str, difficulty: str, num_questions: int) -> List[Dict[str, Any]]:
    """Create fallback MCQs if API fails"""
    
    # Simple keyword-based MCQ generation
    words = text.split()
    important_words = [w for w in words if len(w) > 5 and w.isalpha()][:10]
    
    mcqs = []
    for i in range(min(num_questions, 3)):  # Limit to 3 for fallback
        if i < len(important_words):
            word = important_words[i]
            mcq = {
                "question": f"What is the main topic related to '{word}' in the text?",
                "options": [
                    f"A) {word} is a key concept",
                    f"B) {word} is mentioned briefly",
                    f"C) {word} is not important",
                    f"D) {word} is undefined"
                ],
                "correct_answer": "A",
                "explanation": f"The text discusses {word} as an important concept."
            }
            mcqs.append(mcq)
    
    return mcqs

def main():
    parser = argparse.ArgumentParser(description='Generate MCQs using Hugging Face API')
    parser.add_argument('filename', help='Original filename')
    parser.add_argument('difficulty', help='Difficulty level')
    parser.add_argument('num_questions', help='Number of questions')
    parser.add_argument('--model', default='microsoft/DialoGPT-medium', help='Hugging Face model to use')
    
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
        mcqs = generate_mcqs_with_hf(
            text=text,
            difficulty=args.difficulty,
            num_questions=int(args.num_questions),
            model=args.model
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
