# Local LLM Chat Application

A simple chat interface powered by Ollama that runs completely locally on your machine.

## Prerequisites
- Python 3.12 or higher
- [Ollama](https://ollama.ai) installed on your system

## Setup

### 1. Create a Python Virtual Environment

**Linux/macOS**:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows**:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

### 2. Install Required Packages

```bash
pip install flask==3.1.0 requests==2.32.3 rich==13.9.4 ollama==0.4.7
```

### 3. Install Ollama

**Linux**:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**macOS**:
- Download from [ollama.ai](https://ollama.ai)
- Or using Homebrew:

```bash
brew install ollama
```

**Windows**:
- Download and install from [ollama.ai](https://ollama.ai/download/windows)
- Run the installer
- Launch Ollama from the Start menu

### 4. Verify Ollama Installation

**Linux/macOS**:

```bash
ollama --version
```

**Windows**:

```powershell
ollama.exe --version
```

## Running the Application

1. **Start the application**:

```bash
python app.py
```

2. The application will automatically:
   - Check if Ollama is installed and running
   - Download the DeepSeek model if not present (~4GB)
   - Launch the web interface in your default browser
   - Available at `http://localhost:5000`

## Common Issues

- **"Ollama is not installed"**: Follow the installation steps at ollama.ai
- **"Failed to connect to Ollama"**: Run `ollama serve` in a separate terminal
- **"Model not found"**: First run takes time to download the model (~4GB)
- **Browser doesn't open**: Navigate to `http://localhost:5000` manually

## Requirements

The application requires the following Python packages:

```txt
flask==3.1.0
requests==2.32.3
rich==13.9.4
ollama==0.4.7
```

## License

MIT License - Feel free to use and modify for your needs.
