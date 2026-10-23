"""A aba "Meu perfil" do painel (tools/painel.py): o começo do /setup em botões.

  * Documentos - o currículo e a exportação do LinkedIn, em PDF, gravados em
                 documents/cv/ e documents/linkedin/ (fora do git), onde o
                 Caminho A do /setup os lê;
  * Formulário - o que o currículo não diz (gênero gramatical, modelo de
                 trabalho, regimes, pretensão, níveis, cargos a buscar...),
                 gravado em documents/perfil/respostas.json (fora do git);
  * Privacidade - para onde o repositório publica, conferido antes de o Claude
                 propor o perfil, que vai para arquivos rastreados pelo git;
  * Proposta   - o Claude não grava o perfil: escreve a versão nova de cada
                 arquivo em documents/perfil/proposta/, o painel mostra o que
                 muda e só o clique em "Aplicar" copia para o lugar. Sem
                 conversa, o Claude Code trata qualquer caminho com `.claude/`
                 como sensível e recusa a gravação mesmo com a permissão
                 liberada; por isso a proposta usa `claude/` no lugar.

Funções puras, testadas sem servidor; quem chama o Claude é o painel.
"""

import base64
import difflib
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
STAGING = DOCUMENTS / "perfil" / "proposta"
# Os arquivos que o /setup grava; qualquer outro arquivo na proposta é ignorado.
TARGETS = re.compile(r"^(CLAUDE\.md|\.claude/skills/job-application-assistant/0[1-9]-[\w-]+\.md"
                     r"|\.claude/skills/job-scraper/search-queries\.md|cv/main_example\.tex)$")
MAX_DIFF_LINES = 400

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


# ---------------------------------------------------------------------------
# Proposta: o perfil novo, revisado antes de ir para o lugar
# ---------------------------------------------------------------------------

def staging_name(target: str) -> str:
    """O caminho na proposta: `.claude/` vira `claude/` (o Claude Code recusa `.claude` sem conversa)."""
    return "claude/" + target[len(".claude/"):] if target.startswith(".claude/") else target


def target_name(staged: str) -> str:
    return ".claude/" + staged[len("claude/"):] if staged.startswith("claude/") else staged


def proposal(root: Path = ROOT, staging: Path = STAGING) -> dict:
    """O que a proposta muda, arquivo por arquivo, com o diff; arquivos fora do perfil são ignorados."""
    files, ignored = [], []
    if not staging.is_dir():
        return {"files": files, "ignored": ignored}
    for path in sorted(staging.rglob("*")):
        if not path.is_file():
            continue
        staged = path.relative_to(staging).as_posix()
        target = target_name(staged)
        if path.is_symlink() or not TARGETS.match(target):
            ignored.append(staged)
            continue
        try:
            new = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        except (OSError, UnicodeDecodeError):
            ignored.append(staged)
            continue
        current = root / target
        old = current.read_text(encoding="utf-8").replace("\r\n", "\n") if current.is_file() else ""
        if new == old:
            continue
        diff = list(difflib.unified_diff(old.splitlines(), new.splitlines(), "atual", "proposta", n=2, lineterm=""))[2:]
        files.append({
            "path": target, "new_file": not current.is_file(),
            "added": sum(1 for l in diff if l.startswith("+")), "removed": sum(1 for l in diff if l.startswith("-")),
            "diff": diff[:MAX_DIFF_LINES], "truncated": len(diff) > MAX_DIFF_LINES,
        })
    return {"files": files, "ignored": ignored}


def apply_proposal(paths: list | None = None, root: Path = ROOT, staging: Path = STAGING) -> list:
    """Copia para o lugar os arquivos da proposta (todos, ou só `paths`), mantendo o fim de linha de cada um."""
    applied = []
    for item in proposal(root, staging)["files"]:
        target = item["path"]
        if paths is not None and target not in paths:
            continue
        staged = staging / staging_name(target)
        new = staged.read_text(encoding="utf-8").replace("\r\n", "\n")
        current = root / target
        crlf = current.is_file() and b"\r\n" in current.read_bytes()
        current.parent.mkdir(parents=True, exist_ok=True)
        current.write_bytes((new.replace("\n", "\r\n") if crlf else new).encode("utf-8"))
        staged.unlink()
        applied.append(target)
    if not proposal(root, staging)["files"]:
        discard_proposal(staging)
    return applied


def discard_proposal(staging: Path = STAGING) -> None:
    shutil.rmtree(staging, ignore_errors=True)


def profile_ready(claude_md: Path = ROOT / "CLAUDE.md") -> bool:
    """O /setup já rodou: o CLAUDE.md não tem mais o marcador do modelo."""
    try:
        return "[YOUR_NAME]" not in claude_md.read_text(encoding="utf-8")
    except OSError:
        return False
