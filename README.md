# Simple AI Agent (Python)

A minimal terminal-based AI agent using the OpenAI Python SDK.

## 1) Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 2) Install dependencies

```powershell
pip install -r requirements.txt
```

## 3) Configure environment variables

Copy `.env.example` to `.env` and set your key:

```powershell
copy .env.example .env
```

Edit `.env` and set:

- `OPENAI_API_KEY`
- optional: `OPENAI_MODEL` (default: `gpt-4o-mini`)

## 4) Run

Interactive mode:

```powershell
python agent.py
```

Single message mode:

```powershell
python agent.py -m "Give me a 3-step plan to learn FastAPI"
```
