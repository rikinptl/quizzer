#!/bin/bash

# Quick setup script for the MCQ Generator system
# This script helps set up the environment quickly

set -e

echo "🚀 Setting up PDF/PPT to MCQ Generator..."

# Check if we're in a Git repository
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit: PDF/PPT to MCQ Generator"
fi

# Create necessary directories
echo "📂 Creating directory structure..."
mkdir -p uploads results scripts .github/workflows

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x scripts/*.py scripts/*.sh

# Check Python dependencies
echo "🐍 Checking Python dependencies..."
if ! python3 -c "import PyPDF2, pptx" 2>/dev/null; then
    echo "📦 Installing Python dependencies..."
    pip3 install -r requirements.txt
fi

# Check if Ollama is installed
echo "🤖 Checking Ollama installation..."
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama not found. Please install Ollama first:"
    echo "   curl -fsSL https://ollama.ai/install.sh | sh"
    echo "   Then run: ollama pull llama2"
else
    echo "✅ Ollama is installed"
    
    # Check if llama2 model is available
    if ! ollama list | grep -q "llama2"; then
        echo "📥 Pulling Llama2 model (this may take a while)..."
        ollama pull llama2
    fi
    
    # Create custom model if Modelfile exists
    if [ -f "Modelfile" ]; then
        echo "🔧 Creating custom MCQ model..."
        ollama create mcq-generator -f Modelfile
    fi
fi

# Create sample files
echo "📄 Creating sample files..."
if [ ! -f "uploads/sample.pdf" ]; then
    echo "Creating sample PDF placeholder..."
    echo "Sample PDF content would go here" > uploads/sample.pdf
fi

# Set up Git hooks (optional)
echo "🔗 Setting up Git hooks..."
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook to validate files
echo "Running pre-commit validation..."

# Check if Python scripts are valid
python3 -m py_compile scripts/extract_text.py
python3 -m py_compile scripts/generate_html.py
python3 -m py_compile scripts/validate.py

echo "Pre-commit validation passed!"
EOF

chmod +x .git/hooks/pre-commit

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Push your repository to GitHub"
echo "2. Enable GitHub Pages in repository settings"
echo "3. Set up a self-hosted runner"
echo "4. Configure the runner with Ollama"
echo "5. Test the system with a sample file"
echo ""
echo "📖 For detailed instructions, see README.md"
echo ""
echo "🌐 Your MCQ Generator will be available at:"
echo "   https://yourusername.github.io/Quizzer/"
