#!/bin/bash

# Enhanced error handling script for the MCQ generation workflow
# This script provides comprehensive error checking and recovery

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Error handling function
handle_error() {
    local exit_code=$?
    local line_number=$1
    log_error "Error occurred at line $line_number with exit code $exit_code"
    
    # Cleanup on error
    cleanup_on_error
    
    exit $exit_code
}

# Cleanup function
cleanup_on_error() {
    log_info "Performing cleanup..."
    
    # Remove temporary files
    rm -f prompt.txt ollama_error.log extracted_text.txt
    
    # Log current state
    log_info "Current directory contents:"
    ls -la
    
    # Log any partial outputs
    if [ -f "mcq_output.json" ]; then
        log_info "Partial MCQ output found:"
        head -20 mcq_output.json
    fi
}

# Set error trap
trap 'handle_error $LINENO' ERR

# Function to check if Ollama is running
check_ollama() {
    log_info "Checking Ollama status..."
    
    if ! command -v ollama &> /dev/null; then
        log_error "Ollama is not installed or not in PATH"
        exit 1
    fi
    
    # Check if Ollama service is running
    if ! pgrep -f "ollama serve" > /dev/null; then
        log_warning "Ollama service not running, attempting to start..."
        ollama serve &
        sleep 5
        
        if ! pgrep -f "ollama serve" > /dev/null; then
            log_error "Failed to start Ollama service"
            exit 1
        fi
    fi
    
    log_success "Ollama is running"
}

# Function to check if required models are available
check_models() {
    log_info "Checking available Ollama models..."
    
    # List available models
    ollama list
    
    # Check if llama2 is available
    if ! ollama list | grep -q "llama2"; then
        log_error "Llama2 model not found. Please run: ollama pull llama2"
        exit 1
    fi
    
    # Check if custom MCQ model exists
    if ! ollama list | grep -q "mcq-generator"; then
        log_warning "Custom MCQ model not found. Creating from Modelfile..."
        if [ -f "Modelfile" ]; then
            ollama create mcq-generator -f Modelfile
            log_success "Custom MCQ model created"
        else
            log_warning "Modelfile not found, using default llama2"
        fi
    fi
    
    log_success "Required models are available"
}

# Function to validate file
validate_file() {
    local file_path=$1
    
    log_info "Validating file: $file_path"
    
    if [ ! -f "$file_path" ]; then
        log_error "File not found: $file_path"
        exit 1
    fi
    
    # Check file size
    file_size=$(stat -f%z "$file_path" 2>/dev/null || stat -c%s "$file_path" 2>/dev/null)
    max_size=$((50 * 1024 * 1024))  # 50MB
    
    if [ "$file_size" -gt "$max_size" ]; then
        log_error "File too large: $file_size bytes (max: $max_size bytes)"
        exit 1
    fi
    
    # Check file extension
    file_ext="${file_path##*.}"
    case "$file_ext" in
        pdf|ppt|pptx)
            log_success "Valid file type: $file_ext"
            ;;
        *)
            log_error "Unsupported file type: $file_ext"
            exit 1
            ;;
    esac
    
    log_success "File validation passed"
}

# Function to validate text extraction
validate_text_extraction() {
    local text_file=$1
    
    log_info "Validating text extraction..."
    
    if [ ! -f "$text_file" ]; then
        log_error "Text file not found: $text_file"
        exit 1
    fi
    
    # Check if file has content
    if [ ! -s "$text_file" ]; then
        log_error "No text extracted from document"
        exit 1
    fi
    
    # Check minimum text length
    text_length=$(wc -c < "$text_file")
    min_length=100
    
    if [ "$text_length" -lt "$min_length" ]; then
        log_error "Extracted text too short: $text_length characters (min: $min_length)"
        exit 1
    fi
    
    log_success "Text extraction validation passed ($text_length characters)"
}

# Function to validate Ollama output
validate_ollama_output() {
    local output_file=$1
    
    log_info "Validating Ollama output..."
    
    if [ ! -f "$output_file" ]; then
        log_error "Ollama output file not found: $output_file"
        exit 1
    fi
    
    if [ ! -s "$output_file" ]; then
        log_error "Ollama output is empty"
        exit 1
    fi
    
    # Check if output is valid JSON
    if ! python3 -c "import json; json.load(open('$output_file'))" 2>/dev/null; then
        log_error "Ollama output is not valid JSON"
        log_info "Raw output:"
        head -10 "$output_file"
        exit 1
    fi
    
    # Validate JSON structure using Python script
    if ! python3 scripts/validate.py "$output_file"; then
        log_error "MCQ validation failed"
        exit 1
    fi
    
    log_success "Ollama output validation passed"
}

# Function to retry Ollama generation
retry_ollama_generation() {
    local max_attempts=3
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log_info "Ollama generation attempt $attempt/$max_attempts"
        
        if ollama run llama2 < prompt.txt > mcq_output.json 2> ollama_error.log; then
            log_success "Ollama generation successful on attempt $attempt"
            return 0
        else
            log_warning "Ollama generation failed on attempt $attempt"
            if [ -f "ollama_error.log" ]; then
                log_info "Error log:"
                cat ollama_error.log
            fi
            
            attempt=$((attempt + 1))
            sleep 5
        fi
    done
    
    log_error "Ollama generation failed after $max_attempts attempts"
    exit 1
}

# Function to check system resources
check_system_resources() {
    log_info "Checking system resources..."
    
    # Check available memory
    if command -v free &> /dev/null; then
        available_memory=$(free -m | awk 'NR==2{printf "%.0f", $7}')
        if [ "$available_memory" -lt 2048 ]; then
            log_warning "Low memory available: ${available_memory}MB (recommended: 2GB+)"
        fi
    fi
    
    # Check disk space
    available_space=$(df . | awk 'NR==2{print $4}')
    if [ "$available_space" -lt 1048576 ]; then  # 1GB in KB
        log_warning "Low disk space available: ${available_space}KB"
    fi
    
    log_success "System resource check completed"
}

# Main validation function
main() {
    log_info "Starting comprehensive validation..."
    
    # Check system resources
    check_system_resources
    
    # Check Ollama
    check_ollama
    
    # Check models
    check_models
    
    log_success "All validations passed"
}

# Run main function if script is executed directly
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi
