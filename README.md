# 🤖 PilotHub (Multi-AI Intelligence Hub)

[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen?style=flat-square)]()
[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)]()
[![Integration](https://img.shields.io/badge/NeoCortex-Interconnected-blueviolet?style=flat-square)]()

A unified multi-model AI routing hub and interface. PilotHub provides a single control plane to interact with cloud AI providers (OpenAI, Gemini, DeepSeek, Grok), free privacy models (DuckDuckGo), and the local **NeoCortex** intelligence layer for NeOS.

---

## ✨ Features

- **Multi-Provider AI Routing**:
  - 🤖 **NeoCortex**: Local-first capability-gated intelligence layer for NeOS (native AF_UNIX IPC protocol & HTTP fallback)
  - 🤖 **OpenAI ChatGPT**: GPT-4, GPT-4o
  - 🤖 **Google Gemini**: High-speed reasoning & multimodal analysis
  - 🤖 **DeepSeek**: Coding and reasoning models
  - 🤖 **Grok (xAI)**: Real-time knowledge models
  - 🤖 **DuckDuckGo AI**: Free private query engine
- **Media Generation**:
  - 🎨 **DALL-E 3**: Prompt-to-image synthesis
  - 🎥 **Replicate**: Video generation pipeline
- **Three Unified Interfaces**:
  - 💻 **Interactive CLI**: Rich terminal client with provider switching, history, and `/arena` mode
  - 🌐 **Web Interface**: Clean dashboard with chat and instant media generation
  - 🔌 **OpenAI-Compatible API**: Serves `/v1/chat/completions` (with SSE streaming) and `/v1/models` so external systems like NeoCortex can route through PilotHub

---

## ⚡ NeoCortex Interconnection Architecture

PilotHub and [NeoCortex](file:///home/nimuthu/NeoCortex) interconnect bidirectionally:

```
┌──────────────────────────┐          AF_UNIX IPC           ┌──────────────────────────┐
│         PilotHub         │  ◄──────────────────────────►  │    NeoCortex (NeOS)      │
│  (Multi-Model Orchestr.) │     core.sock framing          │  (Local OS Intelligence) │
│                          │                                │                          │
│  OpenAI-Compatible Server│  ◄───────────────────────────  │  OpenRouter / SSE Client │
│  :5000/v1/chat/complet   │     Model Streaming Route      │  (core.toml)             │
└──────────────────────────┘                                └──────────────────────────┘
```

1. **PilotHub → NeoCortex**:
   PilotHub queries NeoCortex via the binary-framed length-prefixed protocol on `$XDG_RUNTIME_DIR/neocortex/core.sock`. NeoCortex can also be benchmarked alongside other models in CLI `/arena` mode.

2. **NeoCortex → PilotHub**:
   NeoCortex can configure its `core.toml` model section to point to PilotHub's OpenAI-compatible endpoint (`http://127.0.0.1:5000/v1`), using PilotHub as its upstream intelligence engine.

---

## 🚀 Installation & Setup

1. **Run the Automated Setup**:
   ```bash
   ./setup.sh
   ```
   Or manually:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure API Keys**:
   ```bash
   cp .env.example .env
   # Edit .env with your provider credentials
   ```

---

## 🛠️ Usage

### 1. Interactive CLI
```bash
python cli.py
```
**Commands within CLI:**
- `/providers` — List active providers (e.g. `duckduckgo`, `neocortex`, `openai`, `gemini`)
- `/switch <provider>` — Switch active provider mid-session
- `/arena <prompt>` — Dispatch prompt across multiple models concurrently and compare answers
- `/image <prompt>` — Generate an image via DALL-E
- `/reset` — Clear conversation history
- `/exit` — Quit

### 2. One-Off CLI Invocation
```bash
python main.py --provider neocortex --prompt "Run system health audit"
python main.py --provider duckduckgo --prompt "Explain Btrfs snapshots"
```

### 3. Web Dashboard & API Gateway
```bash
python web_app.py
```
- Web UI: `http://127.0.0.1:5000`
- OpenAI endpoint for NeoCortex / curl:
  ```bash
  curl -X POST http://127.0.0.1:5000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{"model": "duckduckgo", "messages": [{"role": "user", "content": "Hello!"}]}'
  ```

---

## 🧪 Testing

Run both test suites:
```bash
# Chatbot integration and file validation
python test_chatbot.py

# Unittest test suite (including NeoCortex socket and OpenAI API bridge)
python -m unittest discover -s tests -p "test_*.py"
```
