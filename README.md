# Local LLM Chatbot Optimization

A local chatbot application built with **Python, Streamlit and Ollama**, allowing users to interact with locally hosted Large Language Models and compare their performance.

## Project Overview

This project focuses on improving and evaluating a chatbot powered by local LLMs. It provides a conversational interface and a benchmarking module to compare models under the same experimental conditions.

## Features

- Chat interface powered by local language models.
- Integration with Ollama.
- Support for multiple installed models.
- Adjustable generation parameters:
  - Temperature
  - Top K
  - Top P
  - Maximum number of tokens
- Conversation history management.
- Create and delete conversations.
- Export conversations in TXT and JSON formats.
- Model performance comparison.
- Benchmark metrics:
  - Total response time
  - Time to First Token (TTFT)
  - Number of generated tokens
  - Tokens per second
  - CPU and RAM usage
- Performance visualization and CSV export.

## Technologies

- Python
- Streamlit
- Ollama
- Pandas
- Plotly
- psutil

## Models Evaluated

The project uses the following models:

- **Llama 3.2** (`llama3.2:latest`)
- **Qwen 0.5B** (`qwen:0.5b`)

## Project Structure

```text
atelier_ollama/
├── app.py
├── modules/
│   ├── __init__.py
│   ├── conversation.py
│   ├── monitoring.py
│   ├── model_comparison.py
│   └── performance.py
├── data/
├── exports/
├── tests/
├── requirements.txt
├── README.md
└── .gitignore
```

## Prerequisites

- Python 3.10 or later
- Ollama installed and running
- Git

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/NinflasLeila/local-llm-chatbot-optimization.git
cd local-llm-chatbot-optimization
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Download the models

```bash
ollama pull llama3.2:latest
ollama pull qwen:0.5b
```

Make sure the Ollama service is running before launching the application.

### 5. Run the application

The main entry point is `app.py`.

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal, usually:

```text
http://localhost:8501
```

## Experimental Evaluation

The benchmarking module compares Llama 3.2 and Qwen 0.5B using different tasks:

1. Concept explanation
2. Logical reasoning
3. Python code generation
4. Text summarization
5. Translation

The objective is to evaluate response quality, generation speed and hardware resource consumption.

## Project Objective

The main objective is to study the trade-off between response quality and computational efficiency when running Large Language Models locally, particularly on machines with limited hardware resources.

---

**Author:** Laila Nineflas  
**Project:** Improvement and Evaluation of a Chatbot Based on Local LLMS 
