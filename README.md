# 📚 PDF/PPT to MCQ Generator

A GitHub-powered system that converts PDF and PowerPoint documents into AI-generated multiple choice questions using Ollama. This system leverages GitHub Actions and GitHub Pages to create a complete hosting solution.

## 🌟 Features

- **File Upload Interface**: Beautiful web interface for uploading PDF/PPT files
- **AI-Powered MCQ Generation**: Uses Ollama with Llama2 to generate high-quality questions
- **Multiple Difficulty Levels**: Easy, Medium, Hard question generation
- **Customizable Question Count**: Generate 1-20 questions per document
- **Automatic Text Extraction**: Supports PDF, PPT, and PPTX formats
- **GitHub Hosting**: Complete solution using GitHub Actions and Pages
- **Real-time Processing**: Live updates on generation progress
- **Responsive Design**: Works on desktop and mobile devices

## 🏗️ Architecture

```
GitHub Pages (Frontend) → GitHub Actions (Backend) → Self-hosted Runner → Ollama → Results
```

1. **Frontend**: GitHub Pages hosts the web interface
2. **Trigger**: User uploads file and triggers GitHub Action
3. **Processing**: Self-hosted runner processes the file with Ollama
4. **Results**: Generated MCQs are committed back to the repository
5. **Display**: Results are automatically displayed on the web interface

## 🚀 Quick Start

### Prerequisites

- GitHub repository with Actions enabled
- Self-hosted runner with Linux OS
- Ollama installed on the runner
- Python 3.9+ on the runner

### 1. Repository Setup

1. **Fork or clone this repository**
2. **Enable GitHub Pages**:
   - Go to Settings → Pages
   - Source: Deploy from a branch
   - Branch: `main` (or your default branch)

3. **Enable GitHub Actions**:
   - Go to Settings → Actions → General
   - Allow all actions and reusable workflows

### 2. Self-Hosted Runner Setup

#### Install Ollama on Runner

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve &

# Pull Llama2 model (this may take a while)
ollama pull llama2

# Create custom MCQ model
ollama create mcq-generator -f Modelfile
```

#### Register Runner with GitHub

1. **Go to your repository Settings → Actions → Runners**
2. **Click "New self-hosted runner"**
3. **Select Linux and follow the setup commands**:

```bash
# Download and configure runner
mkdir actions-runner && cd actions-runner
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz
tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz

# Configure runner
./config.sh --url https://github.com/YOUR_USERNAME/YOUR_REPO --token YOUR_TOKEN

# Install as service
sudo ./svc.sh install
sudo ./svc.sh start
```

### 3. Install Python Dependencies

On your runner, install required Python packages:

```bash
pip install PyPDF2 python-pptx python-docx
```

### 4. Test the Setup

1. **Upload a test PDF** to the `uploads/` directory
2. **Go to Actions tab** in your GitHub repository
3. **Run the "Generate MCQs from PDF/PPT" workflow manually**
4. **Check the results** in the `results/` directory

## 📁 Project Structure

```
Quizzer/
├── .github/
│   └── workflows/
│       └── generate-mcqs.yml          # Main GitHub Action workflow
├── scripts/
│   ├── extract_text.py                # Text extraction from PDF/PPT
│   └── generate_html.py               # HTML generation for results
├── uploads/                           # Directory for uploaded files
├── results/                           # Directory for generated HTML results
├── index.html                         # Main web interface
├── Modelfile                          # Ollama custom model configuration
├── prompt_template.txt                # MCQ generation prompt template
├── mcq_output.json                    # Generated MCQs (created by workflow)
└── README.md                          # This file
```

## 🔧 Configuration

### Customizing the Model

Edit `Modelfile` to adjust the Ollama model behavior:

```dockerfile
FROM llama2
SYSTEM "Your custom system prompt here..."
PARAMETER temperature 0.7
```

### Adjusting Difficulty Levels

Modify the prompt template in `prompt_template.txt` to customize difficulty guidelines.

### Changing Question Count Limits

Update the HTML form validation and workflow inputs to allow different question count ranges.

## 🎯 Usage

### For Users

1. **Visit your GitHub Pages URL** (e.g., `https://yourusername.github.io/Quizzer/`)
2. **Upload a PDF or PowerPoint file**
3. **Select difficulty level** (Easy/Medium/Hard)
4. **Choose number of questions** (1-20)
5. **Click "Generate MCQs"**
6. **Wait for processing** (usually 2-5 minutes)
7. **View generated questions** with explanations

### For Developers

#### Manual Workflow Trigger

```bash
# Trigger workflow via GitHub CLI
gh workflow run "Generate MCQs from PDF/PPT" \
  --field filename="document.pdf" \
  --field difficulty="medium" \
  --field num_questions="5"
```

#### API Integration

The system can be integrated with external applications using GitHub's API to trigger workflows.

## 🛠️ Troubleshooting

### Common Issues

#### 1. Ollama Not Found
```bash
# Check if Ollama is running
ps aux | grep ollama

# Restart Ollama service
ollama serve &
```

#### 2. Python Dependencies Missing
```bash
# Install missing packages
pip install PyPDF2 python-pptx python-docx
```

#### 3. Runner Not Responding
```bash
# Check runner status
sudo systemctl status actions.runner.*

# Restart runner service
sudo ./svc.sh restart
```

#### 4. File Upload Issues
- Ensure `uploads/` directory exists
- Check file permissions
- Verify file format (PDF, PPT, PPTX only)

#### 5. JSON Parsing Errors
- Check Ollama output format
- Verify prompt template
- Review model configuration

### Debug Mode

Enable debug logging by modifying the workflow:

```yaml
- name: Debug Ollama Output
  run: |
    echo "Raw Ollama output:"
    cat mcq_output.json
    echo "--- End Output ---"
```

## 🔒 Security Considerations

- **File Size Limits**: Consider adding file size restrictions
- **File Type Validation**: Ensure only PDF/PPT files are processed
- **Content Filtering**: Add content moderation if needed
- **Rate Limiting**: Implement usage limits to prevent abuse
- **Access Control**: Consider authentication for sensitive documents

## 📈 Performance Optimization

### For Large Documents

1. **Text Chunking**: Split large documents into smaller sections
2. **Parallel Processing**: Generate questions for multiple sections simultaneously
3. **Caching**: Cache extracted text to avoid re-processing

### For High Traffic

1. **Multiple Runners**: Scale with additional self-hosted runners
2. **Load Balancing**: Distribute workload across runners
3. **Queue Management**: Implement job queuing system

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source. Feel free to use, modify, and distribute.

## 🆘 Support

- **Issues**: Report bugs and request features via GitHub Issues
- **Discussions**: Join community discussions
- **Documentation**: Check this README and inline code comments

## 🔮 Future Enhancements

- [ ] Support for more file formats (DOCX, TXT, etc.)
- [ ] Multiple AI models (GPT, Claude, etc.)
- [ ] Question difficulty auto-detection
- [ ] Export to various formats (PDF, Word, etc.)
- [ ] User accounts and question history
- [ ] Collaborative question editing
- [ ] Analytics and usage statistics

---

**Happy Studying! 📚✨**
