#!/usr/bin/env python3
"""
Generate HTML output for MCQ results.
Creates a formatted HTML page displaying the generated MCQs.
"""

import json
import sys
import os
from datetime import datetime
import argparse

def load_mcq_data():
    """Load MCQ data from JSON file."""
    try:
        with open('mcq_output.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: mcq_output.json not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in mcq_output.json - {e}")
        sys.exit(1)

def generate_html(mcqs, filename, difficulty, num_questions):
    """Generate HTML content for MCQ display."""
    
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCQs from {filename}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 2rem;
            font-weight: 300;
        }}
        
        .header-info {{
            opacity: 0.9;
            font-size: 0.9rem;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .mcq-item {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 25px;
            border-left: 4px solid #4facfe;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .question {{
            font-weight: 600;
            margin-bottom: 15px;
            color: #2c3e50;
            font-size: 1.1rem;
        }}
        
        .options {{
            margin-bottom: 15px;
        }}
        
        .option {{
            padding: 8px 12px;
            margin: 5px 0;
            background: white;
            border-radius: 5px;
            border: 1px solid #dee2e6;
            transition: all 0.2s ease;
        }}
        
        .option.correct {{
            background: #d4edda;
            border-color: #28a745;
            color: #155724;
            font-weight: 600;
        }}
        
        .explanation {{
            background: #e3f2fd;
            padding: 12px;
            border-radius: 5px;
            font-style: italic;
            color: #1976d2;
            border-left: 3px solid #2196f3;
        }}
        
        .stats {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
            color: #6c757d;
        }}
        
        .back-link {{
            text-align: center;
            margin-top: 30px;
        }}
        
        .back-link a {{
            color: #4facfe;
            text-decoration: none;
            font-weight: 600;
        }}
        
        .back-link a:hover {{
            text-decoration: underline;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                margin: 10px;
                border-radius: 10px;
            }}
            
            .header, .content {{
                padding: 20px;
            }}
            
            .header h1 {{
                font-size: 1.5rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 Generated MCQs</h1>
            <div class="header-info">
                <strong>Source:</strong> {filename} | 
                <strong>Difficulty:</strong> {difficulty.title()} | 
                <strong>Questions:</strong> {len(mcqs)} | 
                <strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}
            </div>
        </div>
        
        <div class="content">
            <div class="stats">
                📊 Study Session: {len(mcqs)} questions ready for practice
            </div>
"""

    # Add each MCQ
    for i, mcq in enumerate(mcqs, 1):
        html_template += f"""
            <div class="mcq-item">
                <div class="question">{i}. {mcq['question']}</div>
                <div class="options">"""
        
        for option in mcq['options']:
            is_correct = option.startswith(mcq['correct_answer'])
            css_class = 'correct' if is_correct else ''
            html_template += f'<div class="option {css_class}">{option}</div>'
        
        html_template += f"""
                </div>
                <div class="explanation">
                    <strong>💡 Explanation:</strong> {mcq['explanation']}
                </div>
            </div>"""

    html_template += """
            <div class="back-link">
                <a href="../index.html">← Back to Upload Page</a>
            </div>
        </div>
    </div>
</body>
</html>"""

    return html_template

def main():
    parser = argparse.ArgumentParser(description='Generate HTML output for MCQ results')
    parser.add_argument('filename', help='Original filename')
    parser.add_argument('difficulty', help='Difficulty level')
    parser.add_argument('num_questions', help='Number of questions requested')
    
    args = parser.parse_args()
    
    # Load MCQ data
    mcqs = load_mcq_data()
    
    # Generate HTML
    html_content = generate_html(mcqs, args.filename, args.difficulty, args.num_questions)
    
    # Create results directory if it doesn't exist
    os.makedirs('results', exist_ok=True)
    
    # Save HTML file
    output_filename = f"results/mcqs_{args.filename}.html"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML output generated: {output_filename}")
    print(f"Generated {len(mcqs)} MCQs from {args.filename}")

if __name__ == "__main__":
    main()
