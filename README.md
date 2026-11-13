# 🤖 PilotHub — AI Integration Tool

This repository provides a unified interface to interact with multiple AI providers, including ChatGPT (OpenAI), DeepSeek, Grok (xAI), Google Gemini, OpenRouter, DuckDuckGo, and the NeoCortex local intelligence layer.

## Prerequisites

- Python 3.8+
- API Keys for the providers you wish to use (free models available via DuckDuckGo and local NeoCortex).

## Installation

1. Clone the repository.
2. Run the automated setup:
   ```bash
   ./setup.sh
   ```
   Or set up a virtual environment manually:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Set up your environment variables:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Open `.env` and fill in your API keys (e.g. `OPENROUTER_API_KEY`, `OPENAI_API_KEY`).

## Usage

You can use the tool via the Command Line Interface (CLI), the Web Application, or the OpenAI-compatible REST API.

### Command Line Interface (CLI)

#### 1. Interactive Mode:
```bash
python cli.py
```
**Available Commands:**
- `/providers` — List available providers
- `/switch <provider>` — Switch to a different provider
- `/arena <prompt>` — Benchmark responses across multiple providers concurrently
- `/image <prompt>` — Generate an image (DALL-E)
- `/status` — View current system status
- `/reset` — Clear conversation history
- `/exit` — Quit

#### 2. Single Execution:
```bash
python main.py --provider <provider_name> --prompt "<your_message>"
```

### Available Providers

- `openrouter` (OpenRouter Cloud Streaming / Auto-routing)
- `neocortex` (NeoCortex Local Intelligence Layer via `AF_UNIX` IPC)
- `openai` (ChatGPT & DALL-E)
- `gemini` (Google Gemini)
- `deepseek` (DeepSeek)
- `grok` (xAI)
- `duckduckgo` (Free AI Search & Chat)

### Examples

**Using OpenRouter:**
```bash
python main.py --provider openrouter --prompt "Explain quantum computing in simple terms."
```

**Using NeoCortex:**
```bash
python main.py --provider neocortex --prompt "Audit system service status."
```

**Using ChatGPT:**
```bash
python main.py --provider openai --prompt "Hello, how are you?"
```

**Using DeepSeek:**
```bash
python main.py --provider deepseek --prompt "Write a Python script for binary analysis."
```

### Web Interface & GitHub Pages Chatbot

- **Local Web Server & API Gateway:**
  ```bash
  python web_app.py
  ```
  Accessible at `http://127.0.0.1:5000` with OpenAI-compatible endpoint at `/v1/chat/completions`.

- **GitHub Pages Serverless Client:**
  The repository includes a static client in `docs/index.html` configured for GitHub Pages (`https://nimuthuganegoda.github.io/PilotHub/`).

## Testing

Run the validation test suites:
```bash
# Chatbot and environment test suite
python test_chatbot.py

# Complete unit tests
python -m unittest discover -s tests -p "test_*.py"
```
