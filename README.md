# zapi-bot

Backend em Python (FastAPI) para integrar WhatsApp (Z‑API) com ChatGPT e um scraper Selenium que busca clínicas no site da Unimed.

## Como usar

1. Faça **fork** ou clone este repositório.
2. Crie um arquivo `.env` com:
   ```
   INSTANCE_ID=....
   INSTANCE_TOKEN=....
   OPENAI_API_KEY=sk-...
   ```
3. Gere embeddings dos planos executando `python scripts/build_embeddings.py` (opcional).
4. Rode localmente:
   ```
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
5. Faça deploy na Render: o arquivo `render.yaml` já traz a configuração.

## Estrutura

```
app/
  main.py      # ponto de entrada FastAPI
  bot.py       # fluxo conversacional + RAG
  scraper.py   # Selenium headless
requirements.txt
render.yaml
```
