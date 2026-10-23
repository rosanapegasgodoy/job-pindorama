<p align="center">
  <img src="assets/mascot/pip_flight_loop.gif" alt="Pip, o passarinho mensageiro" width="200">
</p>

# job-pindorama

*A sua busca de emprego, rodando na sua máquina — adaptada ao mercado brasileiro.*

O **job-pindorama** é a adaptação para o Brasil do [ai-job-search](https://github.com/MadsLorentzen/ai-job-search), de Mads Lorentzen: um projeto que transforma o [Claude Code](https://claude.com/claude-code) num assistente completo de candidaturas. Você preenche o seu perfil e o Claude avalia vagas, personaliza o currículo, escreve cartas de apresentação e prepara você para entrevistas.

O que muda em relação ao original:

- **Tudo em português do Brasil** — instruções, comandos, documentação e os textos que o Claude produz.
- **Portal Gupy** — uma CLI nova (`gupy-search`) busca no Portal Gupy, onde milhares de empresas brasileiras publicam vagas, com filtro por cidade, estado (UF), modelo de trabalho e **regime de contratação**.
- **CLT × PJ** — a avaliação de vagas compara a remuneração total de cada regime (13º, férias + 1/3, FGTS, benefícios, impostos do PJ) em vez de comparar o número do anúncio.
- **Currículo à brasileira** — sem foto, CPF, idade ou estado civil (LGPD), datas `MM/AAAA`, títulos de seção em português, `R\$` com escape no LaTeX.
- **Processo seletivo brasileiro** — testes da Gupy, vídeo-entrevista gravada, dinâmica de grupo, pretensão salarial, aviso prévio, perguntas eliminatórias, vagas afirmativas, registro em conselho de classe.
- **Sinais de golpe** — a avaliação interrompe e avisa diante de vagas falsas (pedido de Pix, de dados bancários, contato só por WhatsApp).
- **Salário em BRL** — a ferramenta de referência salarial reconhece Ltda., S.A., S/A, ME, EPP e EIRELI, e lê planilhas com cabeçalhos acentuados e números no formato `1.234,56`.
- **Gênero gramatical** — o perfil registra como a pessoa quer ser tratada nos textos ("formada", "formado" ou neutro); nada é deduzido pelo nome.

> Este é um projeto independente, de código aberto, sem afiliação com a Anthropic nem com a Gupy. A Anthropic, o Claude Code e a Gupy são citados só para descrever as ferramentas que o fluxo usa.

## Funciona mesmo?

O autor do projeto original é geofísico. Quando o cargo dele foi cortado no fim de 2025, ele construiu este fluxo para a própria busca de emprego — os mesmos `/scrape`, `/apply` e `/interview` deste repositório, usados toda semana. Foram 69 candidaturas personalizadas, 20 primeiras entrevistas e um contrato assinado: em junho de 2026 ele começou como engenheiro de IA. A versão longa da história está no [LinkedIn dele](https://www.linkedin.com/in/mads-lorentzen/).

Se o projeto original ajudou você, considere [pagar um café ao autor](https://ko-fi.com/madslorentzen). ☕

## O que é

Um fluxo estruturado que transforma o Claude Code num assistente de candidaturas de ponta a ponta. O núcleo (autoconhecimento do perfil, avaliação de encaixe e o fluxo de redação com revisão) funciona em qualquer idioma e país; esta versão vem configurada para o Brasil.

```
/setup          /scrape              /apply <url>
  |                |                     |
  v                v                     v
Preenche o     Busca nos            Avalia o encaixe
seu perfil     portais              Pontua e recomenda
  |                |                     |
  v                v                     v
Arquivos de    Mostra as vagas      Rascunho de currículo + carta
perfil prontos com o encaixe        (LaTeX, personalizado)
                   |                     |
                   v                     v
               Escolhe uma          Agente revisor critica
               -> /apply            -> Revisa -> Resultado final
```

O projeto incorpora boas práticas de orientação de carreira: critérios de avaliação estruturados, cartas voltadas ao futuro e, opcionalmente, referência salarial.

## Pré-requisitos

- [Claude Code](https://claude.com/claude-code) (CLI). O Claude Code não tem plano gratuito: é preciso uma assinatura Claude Pro/Max/Team ou créditos da API da Anthropic (pagamento por uso, geralmente mais barato para uso ocasional). Usa outro agente (Codex, Antigravity, Gemini CLI)? Comece pelo [`AGENTS.md`](AGENTS.md) — as skills de busca em portais funcionam lá direto.
- Python 3.10 ou mais novo
- [Bun](https://bun.sh) (para as CLIs de busca de vagas)
- Uma distribuição LaTeX com `lualatex` e `xelatex`: [MiKTeX](https://miktex.org/) (comum no Windows), [TeX Live](https://tug.org/texlive/), [MacTeX](https://tug.org/mactex/) ou [TinyTeX](https://yihui.org/tinytex/). O currículo compila com `lualatex` (o `pdflatex` costuma falhar no MiKTeX recente com erros de expansão de fonte do `fontawesome5`); a carta compila com `xelatex`, porque o `cover.cls` exige `fontspec`. Com uma instalação mínima, como TinyTeX ou BasicTeX, instale os pacotes extras listados no [SETUP.md](SETUP.md#instalação-mínima-de-tex-tinytexbasictex).
- Opcional: `pip install pypdf` para a checagem de leitura por ATS do `/apply` (licença BSD; sem precisar do Poppler). O `pdftotext` do Poppler continua como plano B (macOS: `brew install poppler`, Debian/Ubuntu: `apt install poppler-utils`, Windows: `choco install poppler`). Sem os dois, a checagem vira uma revisão visual das palavras-chave.

## Início rápido

> **Nunca usou terminal nem GitHub?** Siga o [COMECE-AQUI.md](COMECE-AQUI.md): você instala
> dois programas com cliques e pede o resto ao Claude, em português.
>
> **Prefere botões a comandos?** O painel local faz o caminho inteiro (perfil, busca, triagem,
> avaliação, currículo e carta) sem você escrever nada. O [PAINEL.md](PAINEL.md) mostra o fluxo
> aba por aba.
>
> **Quer ver o caminho inteiro de uma vez?** O [TUTORIAL.md](TUTORIAL.md) acompanha uma pessoa de
> exemplo da instalação à entrevista: perfil, busca, avaliação, currículo e carta, revisão, envio
> e acompanhamento, pelo painel e pela conversa.

### 1. Fork e clone

```bash
gh repo fork rosanapegasgodoy/job-pindorama --clone
cd job-pindorama
```

> [!IMPORTANT]
> **Um fork deste repositório é sempre público** — o GitHub não permite forks privados
> de repositórios públicos — e o `/setup` (passo 3 abaixo) grava os seus dados pessoais
> (nome, contatos, histórico profissional, pretensão salarial) em arquivos **rastreados pelo git**.
> Se esta cópia é para a sua própria busca de emprego, e não para contribuir com mudanças,
> use um **repositório privado** com este como `upstream` — a receita de dois minutos está na
> [seção 8 do SETUP.md](SETUP.md#8-trazendo-atualizações-do-upstream-para-o-seu-fork),
> e todo fluxo de atualização funciona igual. Faça fork só para contribuir.

### 2. Instalar as ferramentas de busca

```bash
python3 tools/install_portal_clis.py   # Windows: python tools\install_portal_clis.py
```

Ele roda `bun install` em toda CLI de portal em `.agents/skills/*/cli/` — descobertas, não listadas, então um portal que você acrescentar com o `/add-portal` ou copiar de outro fork entra num clone novo. Uma CLI cujo `package.json` declare um script de ciclo de vida na instalação (lifecycle script) é pulada e informada, em vez de executada. `--dry-run` mostra o que seria instalado.

Para todas as CLIs de portal que vêm no projeto a instalação é opcional: nenhuma tem dependências de execução e rodam só com o `bun`; o `bun install` só traz os tipos do TypeScript.

### 3. Configurar o seu perfil

```bash
claude
# Depois, dentro do Claude Code:
/setup
```

> **Prefere botões?** A aba **Meu perfil** do painel (`python3 tools/painel.py`) recebe o currículo e o PDF do LinkedIn (gravados em `documents/cv/` e `documents/linkedin/`), um formulário com o que o currículo não diz (gravado em `documents/perfil/respostas.json`, fora do git) e um botão que roda o Caminho A do `/setup` sem conversa, com o formulário no lugar das perguntas. Num perfil que já existe, ele acrescenta o que é novo, mantém o que está gravado e lista os conflitos, o que foi inferido e as lacunas. Antes, o painel confere se o `origin` é público e, se for (ou se não der para saber), pede confirmação. Esse Claude não tem acesso à web nem ao shell, e só grava os arquivos que o `/setup` grava (`tools/painel/claude-settings-perfil.json`).

O `/setup` oferece três caminhos: ler a sua pasta `documents/` se você a preencheu (currículo em PDF, exportação do LinkedIn, diplomas, cartas de recomendação, candidaturas anteriores), importar um único currículo colado no chat, ou conduzir uma entrevista. Ele detecta o que você tem e pergunta. O modo da pasta de documentos é idempotente e pode rodar de novo à medida que você acrescentar material; veja o `documents/README.md` para a organização.

### 4. Buscar vagas

> **Prefere botões?** `python3 tools/painel.py` (no Windows, dois cliques em `abrir-painel.bat`)
> abre um painel local no navegador: busca, lista com filtros e avisos, "me interessa" e
> "descartar" gravados no histórico, e as candidaturas. A busca é a parte mecânica do `/scrape`,
> sem o Claude. Na aba "Me interessam", dois botões chamam o Claude Code sem conversa para
> avaliar a vaga e para fazer currículo e carta (veja [O `/apply` pelo painel](#o-apply-pelo-painel)
> e o fluxo completo no [PAINEL.md](PAINEL.md)).

```bash
/scrape
```

Busca vagas compatíveis com o seu perfil em vários portais (Gupy, Sólides, VAGAS.com, InfoJobs, Remotar, Greenhouse, Programathor, GeekHunter, Michael Page, Robert Half, Trampos, PCD Online, Agrobase, AGROSearch, DigAÍ, Empregos.com.br, LinkedIn, freehire), elimina duplicatas e apresenta tudo ordenado por encaixe, com o regime (CLT, PJ, estágio) quando o portal informa. Escolha uma vaga para rodar o `/apply` direto — ou, quando a busca trouxer mais vagas do que dá para olhar, rode `/rank` para pontuar todas em lote e receber uma lista final ordenada.

A parte mecânica do `/scrape` fica em `tools/scrape_run.py`. O subcomando `search` lê as buscas do `search-queries.md` por prioridade e roda os portais. Ele também descarta as vagas já vistas e junta numa só a mesma vaga encontrada em portais diferentes. O resultado é gravado fora do repositório. Depois da apresentação, o `record` grava o histórico. Em cada vaga, o `tools/posting_signals.py` lê o texto e aponta o que o rótulo do portal esconde: modelo de trabalho declarado (uma vaga "Remoto" que no texto é híbrida), seleção interna, vaga exclusiva para um grupo, intermediário e senioridade fora da linha `Senioridade-alvo` do `CLAUDE.md`. Vale o texto, não o rótulo.

### 5. Candidatar-se a uma vaga

```bash
/apply https://empresa.gupy.io/jobs/12345678
```

Se a URL não puder ser lida (alguns portais bloqueiam acesso automatizado), cole a descrição da vaga:

```bash
/apply <cole aqui o texto completo da vaga>
```

Isso roda o fluxo completo: avalia o encaixe, rascunha currículo + carta, revisa com um segundo agente, ajusta e apresenta o resultado final. A vaga passa antes por um filtro determinístico de integridade (texto escondido, caracteres invisíveis, linhas com cara de instrução, links escondidos), e o veredito dele abre a avaliação; os agentes que coletam e revisam só leem.

As vagas são tratadas como entrada não confiável (o fluxo não segue instruções embutidas nelas e não acessa links do texto delas), mas as defesas de um agente são instruções, não uma caixa de areia — num portal desconhecido, dê uma olhada no que foi coletado e escrito antes de enviar. Detalhes no [SECURITY.md](SECURITY.md).

## Outros comandos

`/setup`, `/scrape` e `/apply` formam o fluxo principal. Mais dez comandos o ampliam quando o perfil está pronto:

- **`/interview`** prepara você para uma entrevista marcada de uma candidatura registrada. Monta um material específico para a etapa a partir do arquivo da candidatura (a vaga exata, o currículo e a carta que quem entrevista leu, a devolutiva das rodadas anteriores), pesquisa a empresa e quem vai entrevistar com a regra de verificar antes de usar, associa as perguntas prováveis aos seus exemplos STAR (incluindo pretensão salarial e disponibilidade) e oferece uma simulação. Lacunas recebem respostas honestas, nunca experiência inventada.
- **`/outcome`** registra o que aconteceu com uma candidatura — etapas de entrevista, propostas, recusas, silêncio. Arquiva o currículo, a carta e o texto da vaga em `documents/applications/<company>_<role>/`, mantém o `outcome.md` no formato que o Caminho A do `/setup` lê e atualiza o tracker. Também cuida do trecho antes do resultado: `/outcome followup` mostra candidaturas abertas em silêncio (padrão de 10 dias), redige um follow-up curto no seu estilo, usando só afirmações dos materiais já enviados (só rascunho, nunca envia; no máximo duas vezes por candidatura), e oferece uma mensagem de agradecimento quando uma etapa de entrevista é registrada. Quando algumas candidaturas se resolvem, ele sugere voltar ao `/setup` para calibrar o método de avaliação pelo que de fato rendeu entrevistas.
- **`/notion-sync`** publica uma visão só de leitura, de mão única, do seu funil num banco de dados do Notion pelo servidor MCP oficial do Notion (OAuth, sem chaves de API) — uma linha por vaga pontuada mais cada candidatura registrada. Os arquivos do repositório continuam sendo o registro oficial: nada volta do Notion, e documentos sincronizam só como nomes de arquivo.
- **`/gmail-sync`** lê o seu Gmail (pelo conector do Gmail) atrás de sinais de status das candidaturas abertas — convites para entrevista, testes, propostas, recusas, inclusive os e-mails em português da Gupy e da Solides — e os propõe num lote para você aprovar antes de qualquer gravação, citando o e-mail de origem em cada mudança.
- **`/rank`** faz a ponte entre `/scrape` e `/apply`: pontua em lote as vagas recém-coletadas com o método de avaliação (agentes em paralelo coletam cada vaga e pontuam as cinco dimensões) e devolve uma lista final ordenada, com pontos fortes e lacunas honestos por vaga. Deal-breakers (local, idioma, regime) vetam, prazos ganham alerta de urgência, vagas mortas viram encerradas.
- **`/expand`** enriquece o seu perfil examinando fontes públicas que você já citou nele (GitHub, portfólio, Kaggle, Google Scholar, Currículo Lattes) e consultando as ementas de cursos e certificações citados. As competências descobertas entram no perfil com a origem marcada.
- **`/upskill`** analisa a distância entre o seu perfil e as vagas que você acompanha — ou uma única vaga, com `/upskill <URL>`. Produz um mapa de calor priorizado das lacunas e um plano de estudos com materiais encontrados na web (inclusive opções brasileiras) e estimativas de tempo.
- **`/html-report`** gera um painel HTML autossuficiente, em português, a partir do `job_search_tracker.csv` e dos arquivos das candidaturas — cartões de números, gráficos de status, setor, canal e funil (SVG inline, sem dependências externas) e uma tabela filtrável. Abre direto no navegador, sem internet.
- **`/add-template`** registra o seu próprio modelo de currículo ou carta (LaTeX, Typst ou outra ferramenta) no lugar dos padrões. Veja [Modelos próprios](#modelos-próprios) abaixo.
- **`/add-portal`** gera uma skill de busca para um portal de vagas do seu mercado. Veja [Ferramentas de busca](#ferramentas-de-busca) abaixo.

O `/reset` também está disponível; veja [Recomeçar do zero](#recomeçar-do-zero) abaixo.

## Estrutura dos arquivos

```
job-pindorama/
├── CLAUDE.md                          # Perfil principal + regras do fluxo
├── DIARIO.md                          # Diário da adaptação para o Brasil
├── .claude/
│   ├── commands/
│   │   ├── apply.md                   # /apply: fluxo de redação e revisão
│   │   ├── setup.md                   # /setup: configuração (pasta de documentos, currículo ou entrevista)
│   │   ├── expand.md                  # /expand: ampliar competências pelos documentos e pela presença online
│   │   ├── add-template.md            # /add-template: registrar modelos próprios (LaTeX, Typst, ...)
│   │   ├── add-portal.md              # /add-portal: gerar uma skill de busca para um portal do seu mercado
│   │   ├── rank.md                    # /rank: triar as vagas coletadas numa lista final ordenada
│   │   ├── outcome.md                 # /outcome: registrar resultados e arquivar materiais
│   │   ├── gmail-sync.md              # /gmail-sync: detectar o status das candidaturas pelo Gmail
│   │   ├── interview.md               # /interview: material por etapa + simulação de entrevista
│   │   ├── html-report.md             # /html-report: gerar o painel de candidaturas
│   │   ├── notion-sync.md             # /notion-sync: visão de mão única num banco do Notion
│   │   └── reset.md                   # /reset: apagar os dados do perfil ou a pasta de documentos
│   ├── agents/                        # Agentes de menor privilégio (coleta, pontuação, revisão)
│   ├── skills/
│   │   ├── job-application-assistant/ # Skill principal de candidaturas
│   │   │   ├── SKILL.md               # Definição da skill
│   │   │   ├── 01-candidate-profile.md # Formação, experiência, competências
│   │   │   ├── 02-behavioral-profile.md# Perfil comportamental (PI, DISC, teste da Gupy...)
│   │   │   ├── 03-writing-style.md    # Tom, estrutura, o que fazer e o que evitar
│   │   │   ├── 04-job-evaluation.md   # Método de avaliação, CLT × PJ, sinais de golpe
│   │   │   ├── 05-cv-templates.md     # Currículo em LaTeX + convenções brasileiras
│   │   │   ├── 06-cover-letter-templates.md # Carta de apresentação em LaTeX
│   │   │   ├── 07-interview-prep.md   # Exemplos STAR + processo seletivo brasileiro
│   │   │   ├── 08-application-forms.md # Campos de formulário, pretensão salarial
│   │   │   └── 09-web-research.md     # Coleta na web e verificação de afirmações
│   │   ├── job-scraper/               # Orquestração da busca de vagas
│   │   └── upskill/                   # /upskill: lacunas e plano de estudos
│   └── settings.json                  # Permissões do Claude Code (compartilhadas, restritas)
├── .agents/skills/                    # CLIs de busca em portais
│   ├── gupy-search/                   # Portal Gupy (Brasil)
│   ├── solides-search/                # Sólides Vagas (Brasil, empresas pequenas e médias)
│   ├── vagas-search/                  # VAGAS.com (Brasil, generalista)
│   ├── infojobs-search/               # InfoJobs Brasil (generalista; uso pessoal)
│   ├── remotar-search/                # Remotar (Brasil, só remotas; uso pessoal)
│   ├── greenhouse-search/             # Boards do Greenhouse (empresas de tecnologia; lista em boards.txt)
│   ├── programathor-search/           # Programathor (tecnologia)
│   ├── geekhunter-search/             # GeekHunter (tecnologia)
│   ├── michaelpage-search/            # Michael Page (gestão e especialistas)
│   ├── roberthalf-search/             # Robert Half (especialistas; uso pessoal)
│   ├── trampos-search/                # Trampos (comunicação, marketing, design; uso pessoal)
│   ├── pcd-search/                    # PCD Online (vagas exclusivas PcD; uso pessoal)
│   ├── agrobase-search/               # Agrobase (agronegócio, por profissão)
│   ├── agrosearch-search/             # AGROSearch (consultoria do agronegócio)
│   ├── digai-search/                  # DigAÍ (empresas com entrevista por IA)
│   ├── empregos-search/               # Empregos.com.br (generalista, busca por cargo)
│   ├── linkedin-search/               # Vagas públicas do LinkedIn (qualquer país)
│   └── freehire-search/               # Agregador freehire.me (tecnologia, vários mercados)
├── cv/
│   └── main_example.tex               # Modelo de currículo moderncv em LaTeX
├── cover_letters/
│   ├── cover.cls                      # Classe LaTeX própria da carta
│   ├── cover_example.tex              # Carta de exemplo (referência + teste do CI)
│   └── OpenFonts/                     # Fontes Lato + Raleway
├── templates/                         # Modelos próprios registrados pelo /add-template
├── documents/                         # Materiais de carreira para o /setup e o /expand
├── .github/workflows/ci.yml           # CI: compilações LaTeX, lint das skills, tipagem das CLIs
├── salary_lookup.py                   # Referência salarial (com os seus dados)
├── tools/                             # Ferramentas de apoio (verificação de PDF, filtro de vagas, ...)
├── abrir-painel.bat                   # Painel local (Windows, dois cliques; veja PAINEL.md)
├── job_scraper/                       # Estado da busca (vagas vistas, resultados)
├── gmail_sync/                        # Estado do /gmail-sync
├── upskill/                           # Relatórios do /upskill
├── job_search_tracker.csv             # Planilha de acompanhamento das candidaturas
├── COMECE-AQUI.md                     # Instalação sem terminal (cliques + pedidos ao Claude)
├── PAINEL.md                          # O painel local: o fluxo inteiro em botões
├── TUTORIAL.md                        # Tutorial completo, da instalação à entrevista
└── SETUP.md                           # Guia de instalação detalhado
```

## Como o `/apply` funciona

O comando `/apply` roda um **fluxo de redação e revisão** com compilação obrigatória dos PDFs:

1. **Interpreta** a vaga (URL ou texto)
2. **Avalia o encaixe** com o seu perfil (competências, experiência, cultura, local, carreira, regime)
3. **Rascunha** um currículo e uma carta personalizados em LaTeX
4. **Cria um agente revisor** que pesquisa a empresa e critica os rascunhos
5. **Revisa** com base no retorno do revisor
6. **Compila e inspeciona** os dois PDFs: lualatex para o currículo, xelatex para a carta. O Claude lê as páginas geradas e ajusta o LaTeX até o currículo ter exatamente 2 páginas, sem títulos órfãos, e a carta exatamente 1 página, com a assinatura visível e as fontes consistentes.
7. **Confere o currículo como um ATS**: extrai a camada de texto do PDF e verifica como um leitor de ATS a vê — contatos como texto literal, nada embaralhado, acentos intactos, ordem de leitura certa — e mede a cobertura das palavras-chave da vaga. Palavras-chave que o perfil sustenta entram; lacunas reais ficam visíveis, nunca enchidas.
8. **Apresenta** o resultado final com um checklist de verificação

Toda afirmação do currículo e da carta é conferida com o seu perfil real. O sistema nunca inventa competências nem experiência.

### O que diferencia este fluxo

- **Ciclo de verificação do PDF.** A maioria dos modelos de currículo em LaTeX produz resultados que "parecem certos no .tex" e quebram no PDF: títulos de cargo órfãos na página seguinte, carta indo para a página 2, fonte dos tópicos trocada. O `/apply` compila e inspeciona cada PDF e aplica correções pontuais até o layout ficar limpo.
- **Verificação de ATS na camada de texto.** O ATS (Gupy, Solides, Workday...) lê o texto embutido no PDF, não a página desenhada. O `/apply` extrai a camada de texto do currículo compilado e confere contatos, ordem de leitura e cobertura de palavras-chave contra o que um leitor de fato vê.
- **Corte por relevância.** Quando o currículo passa de 2 páginas, o fluxo não corta mecanicamente a seção "mais antiga": pontua cada linha por relevância para a vaga, exclusividade e dependência da carta, e corta primeiro a de menor pontuação.
- **Separação entre redação e revisão.** Quem redige escreve; um segundo agente, com contexto novo, pesquisa a empresa e critica. Depois quem redige revisa. Isso pega palavras-chave esquecidas, enquadramentos fracos e linguagem genérica.

### O `/apply` pelo painel

Na aba **Me interessam** do painel local (`tools/painel.py`), cada vaga marcada tem dois botões que rodam o Claude Code sem conversa (`claude -p`, com o login do Claude Code do seu computador):

- **Avaliar com o Claude** roda os passos 1 e 2 acima (coleta, filtro de integridade e avaliação de encaixe) e mostra a avaliação no cartão da vaga. Leva alguns minutos.
- **Fazer currículo e carta** só fica ativo depois da avaliação. Roda o resto do fluxo, a partir da avaliação gravada, e registra a candidatura no `job_search_tracker.csv`. Pode levar meia hora.

Diferenças em relação à conversa:

- **Ninguém aprova nada no meio.** O Claude roda com as permissões do projeto mais as de `tools/painel/claude-settings.json`, que só deixam gravar o currículo, a carta, a pesquisa de empresas, a pasta `documents/applications/` e o tracker, e compilar pelo `tools/compile_doc.py`. Todo o resto é negado. O `tools/security_guards.py` confere esse arquivo em todo PR.
- **Decisões viram parada.** Se o filtro de integridade acusar algo na vaga ou o host não for verificado, ele para sem redigir e explica, porque essa decisão é sua, na conversa. Os campos de formulário da Gupy e um modelo próprio do `/add-template` também ficam para a conversa.
- **Sem fonte, sem número.** A referência salarial e os fatos sobre a empresa só entram com uma página consultada na própria execução. Sem isso, a avaliação diz "não consultada".
- **As respostas ficam em `documents/applications/_painel/`**, fora do git. Uma vaga por vez.

Quer acompanhar e corrigir junto? O botão **Copiar pedido** continua lá: cole o `/apply` na conversa.

## Personalização

### Arquivos para editar à mão

Se preferir editar os arquivos direto em vez de usar o `/setup`:

| Arquivo | O que mudar |
|---------|-------------|
| `CLAUDE.md` | O seu perfil completo (nome, formação, experiência, competências, objetivos, deal-breakers) |
| `01-candidate-profile.md` | Versão estruturada dos dados do currículo |
| `02-behavioral-profile.md` | A sua avaliação comportamental ou autoavaliação |
| `04-job-evaluation.md` | Áreas de competência, objetivos de carreira, filtros de motivação |
| `05-cv-templates.md` | Modelos de resumo profissional por tipo de vaga |
| `07-interview-prep.md` | Os seus exemplos STAR da experiência real |
| `search-queries.md` | Buscas de vagas para as suas competências e o seu local |

### Atualizar as buscas

À medida que as prioridades mudam, dá para refazer só a configuração da busca, sem refazer o perfil inteiro:

```
/setup --section search
```

### Modelos próprios

O currículo usa o [moderncv](https://ctan.org/pkg/moderncv) (estilo banking). A carta usa um `cover.cls` próprio com as fontes Lato e Raleway. Os dois são LaTeX.

Para usar um modelo seu — LaTeX, [Typst](https://typst.app/) ou outra ferramenta que gere PDF pela linha de comando —, rode:

```
/add-template
```

O comando entrevista você sobre as instruções do modelo — extensão do fonte, comando de compilação, fontes, regras de estilo, limite de páginas —, guarda tudo em `templates/`, roda uma compilação de teste obrigatória e ativa o modelo para o `/apply` usar. Os modelos são guardados com marcadores `[PLACEHOLDER]` no lugar dos dados pessoais, então podem ser versionados e compartilhados.

- `/add-template --list` mostra os modelos registrados
- `/add-template --use <nome>` troca entre eles
- `/add-template --use default` volta aos modelos padrão (moderncv / cover.cls)

### Ferramentas de busca

O projeto vem com dezoito skills de portal em `.agents/skills/`:

- **`gupy-search`** — busca no [Portal Gupy](https://portal.gupy.io) pela mesma rota pública que a página de busca do portal usa, e lê o detalhe na página pública de cada vaga. Filtra por cidade, UF, modelo de trabalho (remoto, híbrido, presencial) e regime (CLT, PJ, estágio, trainee e outros). **Sem dependências de execução.** Veja `.agents/skills/gupy-search/SKILL.md` e, para os detalhes técnicos, o `url-reference.md` ao lado.
- **`solides-search`** — busca na [Sólides Vagas](https://vagas.solides.com.br) pela rota JSON pública do portal: vagas de empresas pequenas e médias, com modelo de trabalho, regime, senioridade e "exclusiva PcD" já informados. Filtra por modelo, regime e senioridade. **Sem dependências de execução.**
- **`vagas-search`** — busca na [VAGAS.com](https://www.vagas.com.br) pela página pública de resultados, com filtro de 100% home office; o detalhe traz regime e salário. **Sem dependências de execução.**
- **`infojobs-search`** — busca na [InfoJobs Brasil](https://www.infojobs.com.br) pela página pública de resultados, com salário e modelo de trabalho no cartão. **Só para uso pessoal**: os termos da InfoJobs proíbem acesso automatizado, então mantenha o volume baixo.
- **`remotar-search`** — busca na [Remotar](https://remotar.com.br), portal só de vagas remotas, pela API pública do site, com filtro de categoria e opção de tirar as vagas internacionais. **Só para uso pessoal**: os termos da Remotar proíbem acesso automatizado.
- **`greenhouse-search`** — consulta a Job Board API pública do Greenhouse, o sistema de recrutamento de muitas empresas de tecnologia (Stone, C6 Bank, XP, QuintoAndar, Wellhub, VTEX…). Não há busca entre empresas: a lista fica em `boards.txt`, que você edita. **Sem dependências de execução.**
- **`programathor-search`** e **`geekhunter-search`** — portais de vagas de tecnologia; o Programathor busca por tecnologia (`python`, `react`) e não tem página de detalhe pública; o GeekHunter traz nível, modelo, regime e salário.
- **`michaelpage-search`** — vagas de média e alta gestão e especialistas da Michael Page; a empresa contratante é um cliente, em geral confidencial.
- **`roberthalf-search`**, **`trampos-search`** e **`pcd-search`** — Robert Half (especialistas), Trampos (comunicação, marketing, design, tecnologia) e PCD Online (vagas exclusivas para pessoas com deficiência). **Só para uso pessoal**: os termos dos três proíbem acesso automatizado.
- **`agrobase-search`** e **`agrosearch-search`** — agronegócio: o Agrobase (maior agregador do setor, busca por profissão: agrônomo, veterinário, zootecnista, técnico agrícola…) e as vagas da consultoria AGROSearch.
- **`digai-search`** — vagas do [DigAÍ](https://jobs.digai.ai), plataforma de recrutamento com entrevista por IA (Raízen, Localiza, Afya, Hapvida, Stefanini, iFood…), pelas páginas de carreira de cada empresa, que já trazem modelo de trabalho e senioridade. A lista de empresas fica em `companies.txt`, que você edita. **Sem dependências de execução.**
- **`empregos-search`** — busca na [Empregos.com.br](https://www.empregos.com.br), portal generalista, pelas páginas públicas por cargo (a busca livre do site é proibida no `robots.txt`); o cartão traz modelo de trabalho, salário e a descrição. **Sem dependências de execução.**
- **`linkedin-search`** — usa as rotas públicas e sem login do LinkedIn (`jobs-guest`). Funciona para qualquer mercado (`-l "São Paulo, Brasil"`, `-l "Remoto"`), sem dependências de execução. **Só para uso pessoal** — acesso automatizado vai contra os Termos de Serviço do LinkedIn, então mantenha o volume baixo.
- **`freehire-search`** — consulta a API pública do agregador [freehire.me](https://freehire.me) (JSON, sem chave). Focado em tecnologia, vários mercados (`--country BR`, `--region latam`, `--remote`), sem dependências de execução.

Para acrescentar outro portal brasileiro, rode o comando abaixo. A investigação de outubro de 2026 deixou de fora, por bloqueio de robôs ou `robots.txt`: Catho, Indeed, Glassdoor, Hays e Coodesh. Também ficaram de fora a InHire (as vagas só saem por uma API não documentada) e a Trabalha Brasil (os termos proíbem qualquer uso do conteúdo, e a busca devolve vagas de outros cargos). Rode:

```
/add-portal
```

Informe a URL do portal. O comando investiga o portal (padrão da URL de busca, estrutura dos resultados, regras de `robots.txt` e de acesso), monta uma skill de CLI com a mesma estrutura, comandos e formato de saída das que vêm no projeto, e testa uma busca ao vivo antes de registrar qualquer coisa. Portais atrás de login são recusados, e portais com termos restritivos ganham um aviso destacado de uso apenas pessoal.

### Ampliando o projeto: portais, modelos, critérios — e emprestando de outros forks

O projeto tem três pontos de extensão, e nenhum exige mexer no upstream:

1. **Skills de portal** — o sistema de módulos dos portais. Toda skill `*-search` é uma pasta independente em `.agents/skills/` com o mesmo contrato (uma CLI `search`/`detail`, saída `--format json|table|plain`, uma chave `enabled:` no `SKILL.md`, testes próprios). O `/scrape` descobre sozinho qualquer skill instalada que siga o contrato. O [índice de portais da comunidade](https://github.com/MadsLorentzen/ai-job-search/discussions/78) do projeto original cataloga as que outros forks construíram.
2. **Modelos de documento** — o `/add-template` registra qualquer ferramenta de currículo ou carta que gere PDF pela linha de comando.
3. **Critérios de avaliação** — os deal-breakers e as preferências do seu perfil são livres, e a avaliação pontua contra o que você puser ali. "Não aceito PJ", "plano de saúde para dependentes", "no máximo 2 dias presenciais", "sem sobreaviso" — cada um é uma linha do perfil, sem código, e pesa de verdade no `/rank` e no `/apply`. O idioma é o único tipo de deal-breaker com tratamento estruturado: o `/setup` registra cada idioma em que você trabalha e o seu nível numa tabela de Idiomas, e o filtro de idioma (`04-job-evaluation.md`) rejeita uma vaga que exige um idioma que você não declarou, mas só sinaliza — sem rejeitar — uma que pede nível mais alto num idioma declarado.

**Emprestar uma skill de portal de outro fork** é o caminho previsto para ter um portal que este projeto não traz: abra o fork e copie a pasta para o seu `.agents/skills/`. Antes de rodar:

- **Leia o código.** Inteiro — essas CLIs rodam pré-aprovadas na sua máquina (o `.claude/settings.json` as autoriza) contra os seus dados de carreira. Confira que as únicas chamadas de rede vão para o portal que ela diz buscar, que o `package.json` não tem `dependencies` nem scripts de ciclo de vida (`postinstall` etc.) e que nada lê ou grava fora da própria pasta.
- **Rode os testes sem internet** (`bun test` na pasta `cli/` da skill) — os testes de uma skill bem feita passam sem rede.
- Confira a chave `enabled:` e as observações sobre termos de uso da skill.

A cópia é manual de propósito: um instalador que buscasse skills de repositórios de terceiros pularia justamente a checagem que importa — você lendo o código antes.

### Referência salarial

A ferramenta de salário funciona com os dados que você fornecer (pesquisas salariais, guias de consultorias, exportações do Glassdoor, pesquisa própria). Veja `tools/README_SALARY_TOOL.md` para o formato. Sem dados, o passo de salário é simplesmente pulado, e a avaliação usa fontes públicas, dizendo qual.

### Recomeçar do zero

Para apagar os dados do perfil e recomeçar:

```
/reset profile    # limpa os arquivos de skill, preserva as regras do projeto
/reset documents  # apaga os arquivos da pasta documents/
/reset all        # os dois
```

O `/reset` mostra exatamente o que vai ser apagado e exige que você digite `RESET` para confirmar.

### Mantendo-se atualizado

O projeto original evolui rápido. Para trazer as novidades dele para cá, veja a [seção 8 do SETUP.md](SETUP.md#8-trazendo-atualizações-do-upstream-para-o-seu-fork). `python3 tools/check_upstream_updates.py` mostra quais arquivos personalizados uma atualização toca antes de você mesclar, e `python3 tools/upstream_triage.py` separa os commits pendentes em "vale revisar" e "provavelmente pular". Como este fork traduziu os arquivos de instrução, a maioria das atualizações do original exige portar à mão — o relatório semanal ajuda a decidir o que vale.

## Dicas para resultados melhores

### A profundidade do perfil importa

O fator que mais pesa na qualidade do resultado é o detalhe que você põe no perfil. Um perfil raso produz candidaturas genéricas; um detalhado permite resultados realmente personalizados.

- **Descrição dos cargos:** não liste só os títulos. Descreva o que você de fato fez em cada posição: projetos, ferramentas, responsabilidades e conquistas mensuráveis.
- **Competências em contexto:** em vez de "Python" ou "gestão de projetos", descreva como e onde aplicou. "Construí pipelines de ML para previsão de churn em Python com scikit-learn" dá muito mais material que "Python, machine learning".
- **Qualquer caminho de configuração serve:** pasta de documentos, currículo colado ou entrevista — o princípio é o mesmo: entrada mais rica, saída mais afiada.

### Descoberta de caminhos de carreira

O projeto apoia dois modos de busca:

- **Alvo explícito:** você sabe que cargos ou setores quer. O sistema ajuda a refinar e priorizar pelo encaixe.
- **Oportunidades latentes:** analisando a sua trajetória inteira (não só os cargos, mas o trabalho de fato), o sistema pode revelar caminhos que você não considerou — competências transferíveis para setores inesperados, padrões no que você gostou ou em que se destacou, cargos novos que combinam o seu domínio com tecnologia nova.

Para aproveitar isso, invista tempo no `/setup` descrevendo não só a experiência, mas o que dava energia, o que drenava e o que você gostaria de fazer mais.

## Contribuindo

Este fork recebe contribuições para a adaptação ao Brasil (portais brasileiros, convenções do mercado, correções de texto). Melhorias no núcleo do fluxo, que valem para qualquer país, devem ir para o [projeto original](https://github.com/MadsLorentzen/ai-job-search) — leia o [CONTRIBUTING.md](CONTRIBUTING.md) antes.

## Agradecimentos

- [Mads Lorentzen](https://github.com/MadsLorentzen), autor do [ai-job-search](https://github.com/MadsLorentzen/ai-job-search), de onde este projeto deriva
- [Mikkel Krogholm](https://github.com/mikkelkrogsholm) ([repositório de skills](https://github.com/mikkelkrogsholm/skills)), pelas skills originais de CLI de busca de vagas
- Feito com o [Claude Code](https://claude.com/claude-code), da [Anthropic](https://anthropic.com)

## Licença

MIT — veja [LICENSE](LICENSE). O aviso de copyright do projeto original é mantido.
