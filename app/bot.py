import re, os, json, asyncio
from typing import Callable, Dict, Any, List
import openai
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage

openai.api_key = os.getenv("OPENAI_API_KEY")

# Carrega embeddings (se existirem) ou inicializa vazio
if os.path.exists("app/embeddings"):
    try:
        db = FAISS.load_local("app/embeddings", OpenAIEmbeddings())
    except Exception:
        db = None
else:
    db = None

_sessions: Dict[str, Dict[str, Any]] = {}

async def handle_message(phone: str, text: str, send: Callable[[str, str], Any]) -> str | None:
    """Processa a mensagem e decide próximo passo."""
    state = _sessions.get(phone, {})
    text = text.strip()

    # Etapa de coleta de CEP, plano e área
    if state.get("awaiting"):
        field = state["awaiting"]
        state[field] = text
        next_map = {"cep": "plano", "plano": "area", "area": None}
        next_field = next_map[field]
        if next_field:
            state["awaiting"] = next_field
            _sessions[phone] = state
            await send(phone, f"Perfeito! Agora informe o {next_field.upper()}: ")
            return None
        # Temos os 3 dados → chama scraper
        clinics = await _run_scraper(state["cep"], state["plano"], state["area"])
        if not clinics:
            await send(phone, "Desculpe, não encontrei clínicas com esses critérios. 😕")
        else:
            msg = "🏥 Clínicas encontradas:\n" + "\n".join(
                f"{i+1}. {c['nome']} — {c['endereco']}" for i, c in enumerate(clinics)
            )
            await send(phone, msg)
        _sessions.pop(phone, None)
        return None

    # Detecta intenção de procurar clínicas
    if re.search(r"\b(cl[ií]nica|m[eé]dico|guia)\b", text, re.I):
        _sessions[phone] = {"awaiting": "cep"}
        await send(phone, "Vamos lá! Digite seu CEP ou endereço completo:")
        return None

    # Caso contrário → usa RAG ou responde padrão
    if db:
        docs = db.similarity_search(text, k=3)
        context = "\n\n".join(d.page_content for d in docs)
        prompt = f"Você é um corretor de planos. Responda usando **apenas** as informações abaixo.\n\n{context}\n\nPergunta: {text}\nResposta:"
    else:
        prompt = f"Você é um corretor de planos de saúde. Responda de forma clara e objetiva.\n\nPergunta: {text}\nResposta:"

    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.2)
    resp: AIMessage = await llm.agenerate([[prompt]])
    return resp.generations[0][0].text.strip()

async def _run_scraper(cep: str, plano: str, area: str) -> List[Dict[str, str]]:
    """Executa o scraper em subprocesso para não travar o loop."""
    proc = await asyncio.create_subprocess_exec(
        "python", "-m", "app.scraper", cep, plano, area,
        stdout=asyncio.subprocess.PIPE
    )
    out, _ = await proc.communicate()
    try:
        return json.loads(out.decode())
    except Exception:
        return []
