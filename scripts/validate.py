#!/usr/bin/env python3
"""
Error handling and validation utilities for the MCQ generation system.
"""

import json
import os
import sys
import logging
from typing import List, Dict, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCQValidator:
    """Validates MCQ data structure and content."""
    
    @staticmethod
    def validate_mcq_structure(mcq: Dict[str, Any]) -> List[str]:
        """Validate a single MCQ structure."""
        errors = []
        
        # Required fields
        required_fields = ['question', 'options', 'correct_answer', 'explanation']
        for field in required_fields:
            if field not in mcq:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return errors
        
        # Validate question
        if not isinstance(mcq['question'], str) or len(mcq['question'].strip()) < 10:
            errors.append("Question must be a non-empty string with at least 10 characters")
        
        # Validate options
        if not isinstance(mcq['options'], list) or len(mcq['options']) != 4:
            errors.append("Options must be a list with exactly 4 items")
        else:
            for i, option in enumerate(mcq['options']):
                if not isinstance(option, str) or len(option.strip()) < 3:
                    errors.append(f"Option {i+1} must be a non-empty string with at least 3 characters")
        
        # Validate correct answer
        valid_answers = ['A', 'B', 'C', 'D']
        if mcq['correct_answer'] not in valid_answers:
            errors.append(f"Correct answer must be one of: {valid_answers}")
        
        # Validate explanation
        if not isinstance(mcq['explanation'], str) or len(mcq['explanation'].strip()) < 10:
            errors.append("Explanation must be a non-empty string with at least 10 characters")
        
        return errors
    
    @staticmethod
    def validate_mcq_list(mcqs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate a list of MCQs."""
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'stats': {
                'total_questions': len(mcqs),
                'valid_questions': 0,
                'invalid_questions': 0
            }
        }
        
        if not isinstance(mcqs, list):
            result['valid'] = False
            result['errors'].append("MCQs must be provided as a list")
            return result
        
        if len(mcqs) == 0:
            result['valid'] = False
            result['errors'].append("No MCQs provided")
            return result
        
        # Validate each MCQ
        for i, mcq in enumerate(mcqs):
            errors = MCQValidator.validate_mcq_structure(mcq)
            if errors:
                result['stats']['invalid_questions'] += 1
                for error in errors:
                    result['errors'].append(f"Question {i+1}: {error}")
            else:
                result['stats']['valid_questions'] += 1
        
        # Overall validation
        if result['stats']['invalid_questions'] > 0:
            result['valid'] = False
        
        # Add warnings
        if result['stats']['valid_questions'] < len(mcqs) * 0.8:
            result['warnings'].append("More than 20% of questions failed validation")
        
        return result

class FileValidator:
    """Validates uploaded files."""
    
    ALLOWED_EXTENSIONS = ['.pdf', '.ppt', '.pptx']
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    @staticmethod
    def validate_file(file_path: str) -> Dict[str, Any]:
        """Validate an uploaded file."""
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'file_info': {}
        }
        
        # Check if file exists
        if not os.path.exists(file_path):
            result['valid'] = False
            result['errors'].append(f"File not found: {file_path}")
            return result
        
        # Get file info
        file_size = os.path.getsize(file_path)
        file_ext = os.path.splitext(file_path)[1].lower()
        
        result['file_info'] = {
            'path': file_path,
            'size': file_size,
            'extension': file_ext,
            'name': os.path.basename(file_path)
        }
        
        # Validate file extension
        if file_ext not in FileValidator.ALLOWED_EXTENSIONS:
            result['valid'] = False
            result['errors'].append(f"Unsupported file type: {file_ext}. Allowed types: {FileValidator.ALLOWED_EXTENSIONS}")
        
        # Validate file size
        if file_size > FileValidator.MAX_FILE_SIZE:
            result['valid'] = False
            result['errors'].append(f"File too large: {file_size} bytes. Maximum size: {FileValidator.MAX_FILE_SIZE} bytes")
        
        # Add warnings
        if file_size > 10 * 1024 * 1024:  # 10MB
            result['warnings'].append("Large file detected. Processing may take longer")
        
        return result

class TextValidator:
    """Validates extracted text content."""
    
    MIN_TEXT_LENGTH = 100
    MAX_TEXT_LENGTH = 100000
    
    @staticmethod
    def validate_text(text: str) -> Dict[str, Any]:
        """Validate extracted text."""
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'stats': {
                'length': len(text),
                'word_count': len(text.split()),
                'line_count': len(text.split('\n'))
            }
        }
        
        if not isinstance(text, str):
            result['valid'] = False
            result['errors'].append("Text must be a string")
            return result
        
        text = text.strip()
        
        # Check minimum length
        if len(text) < TextValidator.MIN_TEXT_LENGTH:
            result['valid'] = False
            result['errors'].append(f"Text too short: {len(text)} characters. Minimum: {TextValidator.MIN_TEXT_LENGTH}")
        
        # Check maximum length
        if len(text) > TextValidator.MAX_TEXT_LENGTH:
            result['valid'] = False
            result['errors'].append(f"Text too long: {len(text)} characters. Maximum: {TextValidator.MAX_TEXT_LENGTH}")
        
        # Add warnings
        if len(text) < 500:
            result['warnings'].append("Short text detected. May result in fewer quality questions")
        
        if len(text) > 50000:
            result['warnings'].append("Very long text detected. Consider splitting into sections")
        
        return result

class WorkflowValidator:
    """Validates workflow inputs and parameters."""
    
    @staticmethod
    def validate_workflow_inputs(filename: str, difficulty: str, num_questions: str) -> Dict[str, Any]:
        """Validate workflow input parameters."""
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'parameters': {
                'filename': filename,
                'difficulty': difficulty,
                'num_questions': num_questions
            }
        }
        
        # Validate filename
        if not filename or not isinstance(filename, str):
            result['valid'] = False
            result['errors'].append("Filename is required and must be a string")
        
        # Validate difficulty
        valid_difficulties = ['easy', 'medium', 'hard']
        if difficulty not in valid_difficulties:
            result['valid'] = False
            result['errors'].append(f"Invalid difficulty: {difficulty}. Must be one of: {valid_difficulties}")
        
        # Validate number of questions
        try:
            num_q = int(num_questions)
            if num_q < 1 or num_q > 20:
                result['valid'] = False
                result['errors'].append(f"Number of questions must be between 1 and 20, got: {num_q}")
        except ValueError:
            result['valid'] = False
            result['errors'].append(f"Number of questions must be a valid integer, got: {num_questions}")
        
        return result

def main():
    """Test the validation functions."""
    # Test MCQ validation
    test_mcq = {
        "question": "What is the capital of France?",
        "options": ["A) London", "B) Berlin", "C) Paris", "D) Madrid"],
        "correct_answer": "C",
        "explanation": "Paris is the capital and largest city of France."
    }
    
    validator = MCQValidator()
    errors = validator.validate_mcq_structure(test_mcq)
    print(f"MCQ validation errors: {errors}")
    
    # Test file validation
    file_validator = FileValidator()
    # This would test with an actual file path
    print("File validation ready")
    
    # Test text validation
    text_validator = TextValidator()
    test_text = "This is a sample text for testing validation."
    result = text_validator.validate_text(test_text)
    print(f"Text validation result: {result}")

if __name__ == "__main__":
    main()
