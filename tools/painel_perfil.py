"""A aba "Meu perfil" do painel (tools/painel.py): o começo do /setup em botões.

  * Documentos - o currículo e a exportação do LinkedIn, em PDF, gravados em
                 documents/cv/ e documents/linkedin/ (fora do git), onde o
                 Caminho A do /setup os lê;
  * Formulário - o que o currículo não diz (gênero gramatical, modelo de
                 trabalho, regimes, pretensão, níveis, cargos a buscar...),
                 gravado em documents/perfil/respostas.json (fora do git);
  * Privacidade - para onde o repositório publica, conferido antes de o Claude
                 gravar o perfil em arquivos rastreados pelo git.

Funções puras, testadas sem servidor; quem chama o Claude é o painel.
"""

import base64
import json
import os
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCUMENTS = ROOT / "documents"
ANSWERS = DOCUMENTS / "perfil" / "respostas.json"
PROFILE_MD = ROOT / ".claude" / "skills" / "job-application-assistant" / "01-candidate-profile.md"
UPLOAD_KINDS = {"cv": "cv", "linkedin": "linkedin"}
MAX_UPLOAD = 10_000_000

LEVELS = ["estagio", "junior", "pleno", "senior", "especialista", "staff", "lead", "gestao"]

# Seções do formulário: (título, campos). Tipos: text, textarea, lines (uma
# entrada por linha, gravada como lista), choice (uma opção), multi (várias).
SCHEMA = [
    ("Quem é você", [
        {"key": "cidade", "label": "Cidade e UF", "type": "text", "placeholder": "Campinas - SP"},
        {"key": "genero", "label": "Nos textos em português, escrever no", "type": "choice",
         "options": ["feminino", "masculino", "neutro"],
         "help": "Feminino: \"formada\"; masculino: \"formado\"; neutro: \"tenho formação em\"."},
        {"key": "idiomas", "label": "Idiomas e nível, um por linha", "type": "lines",
         "placeholder": "Português - nativo\nInglês - avançado",
         "help": "Seja realista: uma vaga que exige um idioma fora desta lista é descartada."},
        {"key": "situacao", "label": "Situação atual", "type": "text",
         "placeholder": "Empregada CLT, buscando a próxima posição"},
    ]),
    ("O trabalho que você busca", [
        {"key": "cargos", "label": "Cargos a buscar, um por linha", "type": "lines",
         "placeholder": "Product Manager\nProduct Owner"},
        {"key": "senioridade", "label": "Níveis que fazem sentido", "type": "multi", "options": LEVELS},
        {"key": "setores", "label": "Setores de interesse, um por linha", "type": "lines"},
        {"key": "competencias_busca", "label": "Competências que aparecem nas vagas, uma por linha", "type": "lines"},
        {"key": "empresas", "label": "Empresas que você quer acompanhar (opcional)", "type": "lines"},
        {"key": "motivacao", "label": "O que te motiva no trabalho", "type": "textarea"},
    ]),
    ("Condições", [
        {"key": "modelo", "label": "Modelo de trabalho aceito", "type": "multi", "options": ["remoto", "hibrido", "presencial"]},
        {"key": "locais", "label": "Cidades aceitas para híbrido ou presencial", "type": "text"},
        {"key": "regimes", "label": "Regimes aceitos", "type": "multi",
         "options": ["CLT", "PJ", "estagio", "temporario", "freelance"]},
        {"key": "pretensao_clt", "label": "Pretensão em CLT (bruto mensal)", "type": "text", "placeholder": "R$ 8 a 10 mil"},
        {"key": "pretensao_pj", "label": "Mínimo em PJ, se aceitar", "type": "text"},
        {"key": "deal_breakers", "label": "O que você não aceita de jeito nenhum", "type": "textarea"},
    ]),
    ("Opcional", [
        {"key": "idioma_cv", "label": "Idioma do currículo", "type": "choice", "options": ["português", "inglês"]},
        {"key": "comportamental", "label": "Perfil comportamental (resultado de PI, DISC, Gupy... ou como você trabalha melhor)",
         "type": "textarea"},
    ]),
]
FIELDS = {f["key"]: f for _, fields in SCHEMA for f in fields}


# ---------------------------------------------------------------------------
# Formulário
# ---------------------------------------------------------------------------

def clean_answers(data: dict) -> dict:
    """Só os campos do formulário, nos tipos certos; o resto é descartado."""
    out = {}
    for key, field in FIELDS.items():
        value = data.get(key)
        kind = field["type"]
        if kind in ("text", "textarea", "choice") and isinstance(value, str):
            value = value.strip()[:4000]
            if kind == "choice" and value not in field["options"]:
                continue
            if value:
                out[key] = value
        elif kind in ("lines", "multi"):
            items = value.splitlines() if isinstance(value, str) else value if isinstance(value, list) else []
            items = [i.strip()[:200] for i in items if isinstance(i, str) and i.strip()][:30]
            if kind == "multi":
                items = [i for i in field["options"] if i in items]
            if items:
                out[key] = items
    return out


def load_answers(path: Path = ANSWERS) -> dict:
    try:
        return clean_answers(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError, AttributeError):
        return {}


def save_answers(data: dict, path: Path = ANSWERS) -> dict:
    answers = clean_answers(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({**answers, "atualizado": datetime.now().isoformat(timespec="seconds")},
                               ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return answers


def format_answers(answers: dict) -> str:
    """As respostas como "Pergunta: resposta", para o pedido ao Claude."""
    lines = []
    for _, fields in SCHEMA:
        for f in fields:
            value = answers.get(f["key"])
            if value:
                lines.append(f"{f['label']}: {'; '.join(value) if isinstance(value, list) else value}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Documentos
# ---------------------------------------------------------------------------

def safe_name(name: str) -> str:
    """Só o nome do arquivo, com letras, números, espaço, ponto, hífen e sublinhado, terminando em .pdf."""
    base = re.sub(r"[^\w.\- ]", "_", Path(str(name).replace("\\", "/")).name).strip(" .")[:100]
    if not base.lower().endswith(".pdf") or len(base) <= 4:
        raise ValueError("envie um arquivo PDF (no Word: Arquivo > Salvar como > PDF)")
    return base[:-4] + ".pdf"


def save_upload(kind: str, name: str, data_b64: str, base: Path = DOCUMENTS) -> str:
    if kind not in UPLOAD_KINDS:
        raise ValueError(f"tipo de documento desconhecido: {kind}")
    name = safe_name(name)
    try:
        raw = base64.b64decode(data_b64 or "", validate=True)
    except (ValueError, TypeError):
        raise ValueError("o arquivo chegou corrompido; tente de novo")
    if len(raw) > MAX_UPLOAD:
        raise ValueError("arquivo grande demais (máximo 10 MB)")
    if not raw.startswith(b"%PDF-"):
        raise ValueError("isto não é um PDF de verdade")
    folder = base / UPLOAD_KINDS[kind]
    folder.mkdir(parents=True, exist_ok=True)
    (folder / name).write_bytes(raw)
    return name


def list_uploads(base: Path = DOCUMENTS) -> dict:
    out = {}
    for kind, sub in UPLOAD_KINDS.items():
        folder = base / sub
        files = sorted(p for p in folder.glob("*") if p.is_file() and p.name != ".gitkeep") if folder.is_dir() else []
        out[kind] = [{"name": p.name, "size": p.stat().st_size,
                      "modified": datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec="minutes")} for p in files]
    return out


def remove_upload(kind: str, name: str, base: Path = DOCUMENTS) -> None:
    """Apaga só um arquivo que a listagem mostra, pelo nome exato."""
    if kind not in UPLOAD_KINDS or name not in {f["name"] for f in list_uploads(base)[kind]}:
        raise ValueError("arquivo não encontrado")
    (base / UPLOAD_KINDS[kind] / name).unlink()


def has_documents(base: Path = DOCUMENTS) -> bool:
    return any(list_uploads(base).values())


# ---------------------------------------------------------------------------
# Privacidade: para onde este repositório publica
# ---------------------------------------------------------------------------

def github_repo(url: str) -> str | None:
    """owner/repo de um remoto do GitHub (https ou ssh), ou None."""
    m = re.match(r"^(?:https://github\.com/|git@github\.com:|ssh://git@github\.com/)([\w.-]+)/([\w.-]+?)(?:\.git)?/?$", url.strip())
    return f"{m.group(1)}/{m.group(2)}" if m else None


def privacy(root: Path = ROOT) -> dict:
    """status: local (sem remoto), privado, outro (remoto fora do GitHub), publico ou desconhecido."""
    try:
        origin = subprocess.run(["git", "remote", "get-url", "origin"], cwd=root, capture_output=True,
                                text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        origin = ""
    if not origin:
        return {"status": "local", "repo": None}
    repo = github_repo(origin)
    if not repo:
        return {"status": "outro", "repo": None}
    gh = shutil.which("gh")
    if not gh:
        return {"status": "desconhecido", "repo": repo}
    try:
        # Curto: a página espera por isto, e um gh lento ou sem login vira "desconhecido".
        proc = subprocess.run([gh, "repo", "view", repo, "--json", "visibility"], capture_output=True,
                              text=True, timeout=8, env={**os.environ, "GH_PROMPT_DISABLED": "1"})
        visibility = json.loads(proc.stdout).get("visibility") if proc.returncode == 0 else None
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
        visibility = None
    status = {"PRIVATE": "privado", "INTERNAL": "privado", "PUBLIC": "publico"}.get(visibility, "desconhecido")
    return {"status": status, "repo": repo}


def needs_confirmation(info: dict) -> bool:
    return info.get("status") in ("publico", "desconhecido")


def profile_text(path: Path = PROFILE_MD) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def profile_ready(claude_md: Path = ROOT / "CLAUDE.md") -> bool:
    """O /setup já rodou: o CLAUDE.md não tem mais o marcador do modelo."""
    try:
        return "[YOUR_NAME]" not in claude_md.read_text(encoding="utf-8")
    except OSError:
        return False
