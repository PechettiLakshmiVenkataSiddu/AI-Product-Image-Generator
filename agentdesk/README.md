# AgentDesk

AgentDesk is a LangChain autonomous research and task agent with both CLI and API interfaces. It uses tool-calling with explicit tools for web search, calculations, workspace file operations, and scratchpad notes.

## Prerequisites

1. **Python 3.11** installed
2. (Optional) **Ollama** installed for local no-API-key mode: https://ollama.com/download

## Setup (copy/paste in order)

```bash
git clone https://github.com/PechettiLakshmiVenkataSiddu/AI-Product-Image-Generator.git
cd AI-Product-Image-Generator/agentdesk
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## One manual step

Copy `.env.example` to `.env` and paste your OpenAI API key on **line 4**.

```bash
cp .env.example .env
```

That is the only required manual edit to run with OpenAI defaults.

## Run the CLI

Interactive mode:

```bash
python main.py chat
```

One-shot mode:

```bash
python main.py chat --message "Find current USD to EUR rate and convert 250 USD to EUR" --debug
```

Use `--debug` to include intermediate tool steps (reasoning trace).

## Run the API

```bash
uvicorn api:app --reload
```

Example request:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Search latest USD to EUR rate and compute 250 USD in EUR","session_id":"demo","debug":true}'
```

## Run tests

```bash
pytest -q
```

## Swap to Ollama (zero API key local usage)

1. Install and start Ollama.
2. Pull a model, for example:
   ```bash
   ollama pull llama3.1
   ```
3. Update `.env`:
   - `LLM_PROVIDER=ollama`
   - `MODEL_NAME=llama3.1`
   - You may leave `OPENAI_API_KEY` blank
4. Run AgentDesk normally (`python main.py chat` or `uvicorn api:app --reload`).

## Example multi-tool interaction

User goal:

> Search for the current USD to EUR rate and calculate 250 USD in EUR. Save the result to `workspace/fx_report.txt`.

Representative debug trace (abbreviated):

1. TOOL: `web_search` with query for live USD/EUR rate
2. TOOL: `calculator` to multiply `250 * <rate>`
3. TOOL: `write_workspace_file` to store the final report

Final answer includes the converted value and confirmation that `workspace/fx_report.txt` was written.

## Configuration reference

Environment variables are loaded with `pydantic-settings` from `.env`:

- `LLM_PROVIDER` (`openai` or `ollama`)
- `OPENAI_API_KEY` (required only when provider is `openai`)
- `MODEL_NAME`
- `OLLAMA_BASE_URL`
- `TAVILY_API_KEY` (optional; if missing, web search gracefully returns `search unavailable`)
- `LOG_LEVEL`
- `LOG_FILE`
- `WORKSPACE_DIR`
- `MAX_ITERATIONS`
- `TEMPERATURE`

## Logging

- Console: INFO level
- Rotating file logs: DEBUG level at `logs/agentdesk.log`
