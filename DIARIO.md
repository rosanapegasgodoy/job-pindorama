# Diário do projeto job-pindorama

Registro da adaptação do [ai-job-search](https://github.com/MadsLorentzen/ai-job-search) para o mercado de trabalho brasileiro.

---

## 2026-10-19: Sessão 1, ambiente e linha de base

**Objetivo:** preparar o computador (Windows 11), criar o fork público e o repositório privado, e deixar o projeto original funcionando antes de alterar qualquer coisa.

**Duração:** cerca de 35 minutos (das 16h50 às 17h25), contando a espera pelas instalações e o login no GitHub.

### O que foi instalado (via winget)

| Ferramenta | Versão | Para que serve |
|---|---|---|
| git | 2.53 (já existia) | Controle de versão |
| GitHub CLI (gh) | 2.102.0 | Criar o fork e o repositório privado pelo terminal |
| Python | 3.12.10 (já existia) | Scripts do projeto |
| Bun | 1.4.3 | Ferramentas de busca de vagas (TypeScript) |
| MiKTeX | 25.12 | Gera os PDFs de CV (lualatex) e carta (xelatex) |

Também instalei as 6 ferramentas de busca de portais que vêm no projeto, com `python tools\install_portal_clis.py`. Quase todas são de portais dinamarqueses, e trocá-las por portais brasileiros é o próximo desafio.

### Estrutura criada

- `job-pindorama`: fork **público**, só com o framework. Nunca recebe dados pessoais.
- `minha-busca`: repositório **privado** novo, que não é um fork. Fork de repositório público não pode ser privado. O `job-pindorama` está configurado como `upstream` só para receber atualizações, e o envio para ele foi bloqueado.

### Próxima sessão

- Rodar o `/setup` **só** no `minha-busca`, que é o privado.
- Começar a adaptação para o Brasil no `job-pindorama`.

---

## 2026-10-19 e 20: Sessão 2, tropicalização

**Objetivo:** adaptar o `job-pindorama` ao mercado brasileiro, no branch `tropicalizacao`.

**Decisões tomadas antes de começar:**
- Remover os 4 portais dinamarqueses (em vez de só deixá-los desligados).
- Traduzir **tudo** para português, inclusive as instruções internas (skills, comandos, agentes). Custo aceito: atualizações do projeto original vão exigir portar à mão.

### O que foi feito

| Frente | Resultado |
|---|---|
| Limpeza dinamarquesa | Jobindex, Jobnet, Jobbank e Jobdanmark removidos, inclusive das permissões e dos testes |
| Portal Gupy | CLI nova `gupy-search`: busca por cargo, cidade, UF, modelo (remoto/híbrido/presencial) e **regime** (CLT, PJ, estágio...); detalhe completo da vaga; 45 testes sem rede + 2 ao vivo |
| Salário em BRL | Sufixos Ltda., S.A., S/A, ME, EPP, EIRELI; planilhas com cabeçalhos acentuados e números `1.234,56`; testes com empresas brasileiras |
| Convenções BR | CLT × PJ na avaliação, sinais de golpe, vagas afirmativas, registro em conselho de classe, currículo sem foto/CPF/idade (LGPD), datas `MM/AAAA`, carta com "Atenciosamente" e data por extenso, processo seletivo brasileiro (testes da Gupy, vídeo gravado, dinâmica, pretensão salarial, aviso prévio), e-mails em português no `/gmail-sync`, Solides como ATS reconhecido |
| Gênero gramatical | Campo novo no perfil: os textos concordam conforme a pessoa escolher, nunca pelo nome |
| Tradução | Todos os comandos, skills, agentes, README, SETUP, SECURITY, CONTRIBUTING, modelos LaTeX e modelos do GitHub |

### Como os testes foram mantidos

Os testes do projeto conferem frases exatas dos arquivos de instrução (cerca de 650 verificações). A cada arquivo traduzido, um script listava as frases conferidas e um "mapa de âncoras" (inglês → português) atualizava os testes. Termos que são **dados** ficaram em inglês de propósito: status do tracker (`applied`, `no_response`...), vereditos (`PASS`, `Strong Fit`...), nomes de campo e marcadores `[YOUR_...]`.

Resultado final: os mesmos 768 testes que passavam antes continuam passando (774 no total; as 6 falhas são as antigas do `curl` do Windows, abaixo), mais os 45 testes da Gupy.

### Problemas e como foram resolvidos

1. **A API da Gupy que todo mundo cita não existe mais.** `portal.api.gupy.io/api/job` dá 404. *Solução:* descobri, no JavaScript do próprio portal, a rota que a página de busca usa (`portal.gupy.io/api/job-search/jobs`). Detalhes em `.agents/skills/gupy-search/url-reference.md`.
2. **Filtro com dois valores é ignorado em silêncio pela Gupy** (`type=clt&type=pj` devolve tudo). *Solução:* a CLI recusa listas e explica.
3. **URL no User-Agent virou brecha.** O teste de procedência pegou que uma URL do GitHub no User-Agent fazia `github.com` contar como portal confiável. *Solução:* User-Agent sem URL. O `freehire-search` original tem o mesmo defeito (não corrigido aqui, por ser código do original).
4. **"Salário" era partido em "sal" + "rio"** no conversor de planilhas, que só aceitava letras sem acento. *Solução:* a regra passou a aceitar qualquer letra acentuada.
5. **O LaTeX travou compilando.** O MiKTeX básico abria uma janela pedindo para instalar pacotes, escondida atrás do VS Code. *Solução:* `initexmf --set-config-value=[MPM]AutoInstall=1` (só para o usuário), instalar os pacotes que faltavam (`miktex packages install ...`) e `initexmf --update-fndb`.
6. **Falhas antigas do `fetch_page.py`.** O `curl` do Windows não aceita `--compressed`; seis testes já falhavam antes de qualquer mudança. *Solução documentada no SETUP:* instalar um curl completo (`winget install cURL.cURL`). Ainda não aplicada.

### Verificação

- Currículo e carta de exemplo compilados de verdade: 2 páginas e 1 página, acentos intactos na camada de texto (o que o ATS lê).
- Busca e detalhe da Gupy testados ao vivo.

### Commits (branch `tropicalizacao`)

| Commit | Frente |
|---|---|
| `7dcc962` | Remove os portais dinamarqueses |
| `bf1133b` | Skill de busca no Portal Gupy |
| `2e59eb1` | Referência salarial para empresas brasileiras |
| `2dfe2f5` | Tradução e convenções do mercado brasileiro |

Cada commit passa na suíte de testes sozinho (com as 6 falhas antigas do `curl`).

### Próxima sessão

- Revisar o branch `tropicalizacao`, fazer push e abrir o PR para o `master` do próprio `job-pindorama`.
- Instalar um curl completo e confirmar que as 6 falhas antigas somem.
- Levar o `job-pindorama` atualizado para o `minha-busca` e rodar o `/setup`.
- Candidatos a novos portais com o `/add-portal`: Vagas.com, Catho, InfoJobs, Trampos, Programathor (sujeitos à checagem de `robots.txt` e termos).

## 2026-10-20 e 21: Sessão 3, primeira busca real e expansão dos portais

**Objetivo:** pôr a ferramenta em uso de verdade (configurar o `minha-busca` e rodar buscas reais) e usar o que essas buscas revelaram para melhorar o `job-pindorama`.

**Decisões tomadas:**
- A busca pessoal serve de teste da ferramenta; o foco é melhorar o `job-pindorama`.
- Toda mudança genérica entra no `job-pindorama` por branch e PR, e depois é trazida para o `minha-busca`. Dados pessoais ficam só no `minha-busca`.
- Portais cujos termos proíbem acesso automatizado entram no repositório público com aviso destacado de uso pessoal e volume baixo, como o `linkedin-search` (decisão da mantenedora). Portais que o `robots.txt` proíbe ou que bloqueiam robôs ficam de fora, sem contorno.

### O que foi feito

| Frente | Resultado |
|---|---|
| `curl` no Windows | O `curl.exe` do System32 recusa `--compressed`. O `fetch_page.py` passou a consultar `curl --version` e só usa a opção quando há decodificador. Issue aberta no projeto original (#705) |
| Configuração | `/setup` (caminho B, importando um currículo) no `minha-busca`: perfil, avaliação de vagas, modelos de currículo e carta, exemplos STAR e buscas |
| Correções achadas na busca real | LinkedIn: `-l "Brasil"` é ignorado em silêncio (traz vagas dos EUA); o certo é `"Brazil"`. Gupy: o selo `disabilities` significa "também para PcD", não vaga exclusiva |
| `tools/posting_signals.py` | Lê o texto da vaga e aponta o modelo de trabalho declarado (o rótulo "Remoto" do portal não é prova), seleção interna, vaga exclusiva, intermediário (agregador ou consultoria) e senioridade fora da faixa. Linha nova `Senioridade-alvo` no CLAUDE.md, perguntada pelo `/setup` |
| `tools/scrape_run.py` | A parte mecânica do `/scrape`: lê as buscas por prioridade, roda os portais, tira o que já foi visto, junta a mesma vaga achada duas vezes e aplica os sinais; `record` grava o histórico sem sobrescrever o `/rank` |
| Portais (leva 1) | Sólides, VAGAS.com, InfoJobs e Remotar, com base comum (`cli/src/helpers.ts`) e um `parse.ts` por portal |
| Portais (leva 2) | Investigação de 36 portais sugeridos. Entram Greenhouse (lista de empresas em `boards.txt`), Programathor, GeekHunter, Michael Page, Robert Half, Trampos e PCD Online |
| Portais (leva 3, agro) | Agrobase (por profissão, pela API do WordPress) e AGROSearch |

Ao fim da sessão, o projeto tem **16 portais**: Gupy, Sólides, VAGAS.com, InfoJobs, Remotar, Greenhouse, Programathor, GeekHunter, Michael Page, Robert Half, Trampos, PCD Online, Agrobase, AGROSearch, LinkedIn e freehire. InfoJobs, Remotar, Robert Half, Trampos e PCD Online levam o aviso de uso pessoal.

### Portais investigados e deixados de fora

| Motivo | Portais |
|---|---|
| `robots.txt` proíbe o caminho | Hays (página de busca), Coodesh (API) |
| Bloqueiam robôs já na primeira visita | Catho, Glassdoor, Indeed |
| API exige token | Compleo (CTdoAgro) |
| Poucas vagas | EmpregaAgro (4), Perfil Agro (2) |
| Sem vagas públicas legíveis, fora do ar ou fora de escopo | Emprega Brasil (login gov.br), Emprego Rural (domínio estacionado), Pega Aula e Geração C3 (não existem), Vagas do Agro, Revelo, Nube, Hunter4Agro, AgroTalents, Workana, 99Freelas |

Viáveis para uma próxima leva: InHire, Empregos.com.br, BNE, Trabalha Brasil.

### Problemas e como foram resolvidos

1. **O rótulo do portal mentia.** Uma vaga "Remoto" na Gupy dizia no texto "atuação híbrida (4x presenciais)" em outra cidade. *Solução:* o `posting_signals.py` e a regra "vale o texto, não o rótulo" no `/scrape`, no `/rank` e na avaliação.
2. **Vaga de seleção interna passou como boa.** *Solução:* o mesmo `posting_signals.py` reconhece "funcionário com movimentação", "cargos elegíveis" e afins.
3. **InfoJobs: id de uma vaga, URL de outra.** O corte da página caía depois do id, e cada cartão ficava com o id do seguinte. *Solução:* cortar em `<div id="vacancy` e um teste de regressão.
4. **Sólides: parte das vagas não tem página.** Vagas do RH Gestor vêm com id alfanumérico e dão 404 em `/vaga/<id>`. *Solução:* usar a URL do RH Gestor que a própria API informa.
5. **Remotar: a API devolve o e-mail de quem cadastrou a vaga.** *Solução:* a CLI só repassa os campos da vaga, com teste.
6. **Busca larga demais.** Na Remotar, "product manager" trazia qualquer vaga com "product" ou "manager". *Solução:* `--category produto` (de ~130 para ~40 vagas, todas da área).
7. **JSON inválido na Michael Page.** O bloco `JobPosting` vinha com quebras de linha cruas dentro das strings. *Solução:* a leitura comum troca os caracteres de controle e aceita também o formato `@graph` (vale para todas as CLIs da base comum).
8. **Escapes no terminal do Windows.** Heredocs do Git Bash comiam barras invertidas, e o MSYS transformava `//` em `/` no começo dos argumentos. *Solução:* scripts escritos em arquivo, e nunca começar um argumento com `//`.

### Verificação

- Suíte Python completa e testes de cada CLI passando (os testes ao vivo, ligados por `<PORTAL>_LIVE=1`, rodaram contra os portais reais).
- `lint_skills`, `security_guards` e `check_framework_version` passando em todos os PRs.
- O `scrape_run.py` rodou nas buscas reais: 30 buscas em 6 portais em 7 segundos, com as duplicatas entre portais juntadas.

### PRs (todos mesclados no `master`)

| PR | Assunto |
|---|---|
| #2 | `fetch_page.py` só passa `--compressed` a um curl com decodificadores |
| #3 | Local "Brasil" do LinkedIn e rótulo PcD da Gupy |
| #4 | Sinais do texto da vaga (`posting_signals.py`) |
| #5 | Sólides, VAGAS.com, InfoJobs e Remotar |
| #6 | `posting_signals` reconhece consultoria que contrata para clientes |
| #7 | Executor do `/scrape` (`scrape_run.py`) |
| #8 | Greenhouse, Programathor, GeekHunter, Michael Page, Robert Half, Trampos e PCD Online |
| #9 | Agrobase e AGROSearch |

### Próxima sessão

- Portais ainda viáveis: InHire, Empregos.com.br, BNE, Trabalha Brasil.
- Guia de instalação para quem não usa terminal (VS Code, Bun, MiKTeX, `/setup`).
- Texto completo das vagas da Remotar (hoje só um resumo; a vaga inteira está no site da empresa).
- Sinal de conflito de modelo de trabalho entre portais (a mesma vaga "remota" num portal e "híbrida" em outro).

## 2026-10-21 e 22: Sessão 4, DigAÍ, Empregos.com.br e qualidade dos sinais

**Objetivo:** fechar os pendentes da sessão 3 e acrescentar o DigAÍ, plataforma em que a mantenedora fez uma entrevista.

**Decisões tomadas:**
- Portal cuja busca só sai por uma API não documentada não entra por essa API; usa-se o que as páginas públicas trazem prontas do servidor, nos caminhos que o `robots.txt` libera (DigAÍ pelas páginas de empresa, Empregos.com.br pelas páginas por cargo).
- A senioridade e o modelo de trabalho informados pelo portal servem de apoio, mas o texto da vaga continua valendo mais.

### O que foi feito

| Frente | Resultado |
|---|---|
| Documentação | Sessão 3 no diário e parágrafo sobre `scrape_run.py` e `posting_signals.py` no README |
| DigAÍ (`digai-search`) | A busca geral do site usa uma API não documentada; a CLI lê as páginas de carreira de cada empresa (`<empresa>.digai.ai`), com o filtro de cargo do próprio site. Lista de 70 empresas em `companies.txt`, tirada do sitemap. Até 12 vagas por empresa e por busca |
| Filtro de título | Copiado em seis CLIs, passou para a base comum e casa começo de palavra: "ia" não pega mais "Assistência" nem "Brasília" |
| Senioridade do portal | Quando o título não diz o nível, o `posting_signals.py` usa o campo do portal ("Gerência", "Sênior / Especialista"), com `seniority_source` dizendo de onde veio |
| Guia para leigos | `COMECE-AQUI.md`: VS Code e Git por cliques, a extensão do Claude Code e pedidos prontos em português para instalar o resto, baixar e atualizar o projeto |
| Portais que discordam | A mesma vaga "remota" num portal e "híbrida" em outro ganha `workplace_conflict` e um aviso; o `/scrape` decide pelo texto |
| Empregos.com.br (`empregos-search`) | A busca livre é proibida no `robots.txt`; a CLI lê as páginas por cargo (`/vagas/<cargo>`), filtra pelo título e, com `--remote`, pelo modelo do cartão |
| Pontuação | A limpeza de HTML deixava "backlog ," e "remota ."; corrigido na base comum das 15 CLIs |

Ao fim da sessão, o projeto tem **18 portais**: os 16 da sessão 3, mais DigAÍ e Empregos.com.br.

### Portais investigados e deixados de fora

| Portal | Motivo |
|---|---|
| BNE | Viável, adiado: só reconhece os cargos do catálogo dele e troca o resto por um "parecido" (Product Owner virou Gerente de Projetos) |
| InHire | As páginas de carreira são montadas no navegador e as vagas só saem por uma API não documentada |
| Trabalha Brasil | Os termos proíbem "qualquer tipo de uso ou reprodução" do conteúdo, e a busca traz outros cargos |

### Problemas e como foram resolvidos

1. **Chamada à API do DigAÍ bloqueada.** O controle de permissões do Claude Code barrou o teste da API não documentada. *Solução:* usar só as páginas de empresa, que o `robots.txt` libera e que já trazem as vagas.
2. **Vaga de gerência passou para uma faixa pleno–especialista.** O título "Gerente de Produto" é o cargo de PM, e o nível estava só no campo do portal. *Solução:* `portal_seniority()` e `seniority_source`.
3. **O site devolve vagas para qualquer texto.** Na Empregos.com.br, um cargo inventado trouxe 49 mil vagas. *Solução:* filtro de título na CLI.
4. **Barra invertida virando caractere de controle.** Um script Python gravou `\b` como backspace dentro de uma expressão regular. *Solução:* scripts com strings cruas (`r"..."`) e conferência de caracteres de controle depois de cada edição.
5. **Teste que esperava o defeito.** O teste da VAGAS.com tinha "Descrição : Resumo" como resultado esperado. *Solução:* corrigido junto com a pontuação.

### Verificação

- Testes de unidade das 15 CLIs da base comum e suíte Python passando; testes ao vivo do DigAÍ, da Empregos.com.br e dos portais afetados por cada mudança, passando.
- `lint_skills`, `security_guards` e `check_framework_version` passando em todos os PRs.
- Buscas reais no `minha-busca` depois de cada mudança, sem gravar histórico e sem candidatura.

### PRs (todos mesclados no `master`)

| PR | Assunto |
|---|---|
| #10 | Sessão 3 no diário e ferramentas do `/scrape` no README |
| #11 | `digai-search` |
| #12 | Filtro de título casa começo de palavra |
| #13 | `posting_signals` usa a senioridade informada pelo portal |
| #14 | `COMECE-AQUI.md`, instalação sem terminal |
| #15 | Aviso quando portais discordam do modelo de trabalho |
| #16 | `empregos-search` e investigação de 4 portais |
| #17 | Sem espaço antes de pontuação na limpeza de HTML |

### Próxima sessão

- Texto completo das vagas da Remotar (hoje só um resumo).
- BNE, se valer a pena para cargos operacionais.
- Testar o `COMECE-AQUI.md` com alguém sem experiência, num computador limpo.

---

## 2026-10-22: Sessão 5, o painel chama o Claude

**Objetivo:** fazer o painel local (PR #20) ir além da busca, avaliando a vaga e fazendo currículo e carta com botões, sem que a pessoa precise escrever o `/apply` na conversa.

**Decisões tomadas:**
- O painel chama o Claude Code sem conversa (`claude -p`), com o login do próprio computador. Não há chave de API nem servidor externo.
- Foram dois botões, e não um: avaliar primeiro e redigir só depois, a partir da avaliação gravada. Assim a pessoa lê a avaliação antes de gastar meia hora numa candidatura.
- Pelo painel, decisões viram parada: se o filtro de integridade acusar algo, o Claude para sem redigir, e a decisão fica para a conversa.
- O código não leva dado de ninguém. O pedido fala de "a pessoa candidata", e os dados vêm do perfil de cada fork.

### O que foi feito

| Frente | Resultado |
|---|---|
| Botões no painel | "Avaliar com o Claude" (Passos 0 e 1 do `/apply`) e "Fazer currículo e carta" (Passos 2 a 6b), na aba "Me interessam". Uma vaga por vez, só as marcadas ali |
| Resposta no painel | A avaliação e o relatório aparecem no cartão da vaga, em markdown montado nó a nó (nunca como HTML), com os links passando pelo `safeUrl` |
| Permissões | `tools/painel/claude-settings.json` soma às do projeto só a gravação dos arquivos do `/apply` e o `compile_doc.py` |
| `tools/compile_doc.py` | Compila só `cv/main_*.tex` e `cover_letters/cover_*.tex`, sempre com a execução de comandos do LaTeX desligada, e limpa os intermediários |
| `security_guards.py` | Checagem 6: o arquivo de permissões do painel só pode ter entradas da lista revisada |
| Aba "Meu perfil" | O começo do processo em botões: enviar o currículo e o PDF do LinkedIn, um formulário com o que o currículo não diz e um botão que roda o Caminho A do `/setup` sem conversa. Num perfil existente, grava o que é novo, mantém o que já está e lista os conflitos para revisão. Confere se o repositório é público antes de gravar. Esse Claude não tem web nem shell |
| Documentação | README (seções "O `/apply` pelo painel" e "Prefere botões?" do `/setup`), `COMECE-AQUI.md`, `SECURITY.md`, `documents/README.md`, CHANGELOG e este diário |
| `TUTORIAL.md` | O caminho inteiro com uma pessoa de exemplo, da instalação à entrevista, pelo painel e pela conversa, com checklist de revisão antes de enviar, rotina semanal, glossário e perguntas frequentes |
| `PAINEL.md` | Um guia só para o painel: o fluxo inteiro aba por aba, com diagrama, o que cada aviso quer dizer, quando o Claude para em vez de decidir, o que fazer quando algo falha, e por dentro: o que roda em cada botão, onde cada arquivo fica e o que cada Claude do painel pode fazer |

### Problemas e como foram resolvidos

1. **"Não consigo ver o painel".** O painel funcionava; o que confundia era fechar a janela preta (que é o próprio painel) e o navegador não abrir sozinho. *Solução:* o `COMECE-AQUI.md` agora diz para deixar a janela aberta e traz o endereço para colar.
2. **O filtro de integridade não rodou na primeira avaliação.** O agente de coleta chamou `python3 D:/.../tools/posting_guard.py`, com caminho absoluto, e as permissões só liberam `python tools/posting_guard.py`. Sem ninguém para aprovar, o comando foi negado, e o Claude deu um "veredito manual". *Solução:* o pedido exige caminhos relativos e proíbe veredito por conta própria.
3. **`python3` no Windows.** Aqui ele é só o atalho da Microsoft Store (sai com código 49). *Solução:* o painel manda usar `python` no Windows e `python3` nos outros sistemas.
4. **Faixa salarial atribuída a guias que ninguém abriu.** Na segunda avaliação, o Claude citou "guias Robert Half / Michael Page" sem ter feito nenhuma busca na web, o que o registro da sessão mostrou. *Solução:* referência salarial e fatos sobre a empresa só com uma página aberta na própria execução, com o endereço; senão, "não consultada". Na terceira avaliação, a faixa veio com as páginas consultadas.
5. **A primeira versão das permissões abria buracos.** Liberava `lualatex -interaction=nonstopmode main_:*`, que também aprovaria `-shell-escape`, e `rm -f cv/main_:*`, que apagaria qualquer arquivo depois do primeiro. O `security_guards.py` não olhava esse arquivo. *Solução:* o `compile_doc.py` no lugar do motor e do `rm`, e a checagem 6 no guarda.
6. **Um `&` na URL da vaga.** No Windows, o `claude` é um `.cmd`, e o `cmd.exe` interpretaria o `&`. *Solução:* o pedido vai pela entrada padrão; a linha de comando só tem opções fixas.

### Verificação

- Suíte Python inteira passando, com testes novos do painel, do `compile_doc.py` e da checagem 6.
- `security_guards` passando.
- Três avaliações reais pelo painel, numa vaga da Gupy, até sair sem os problemas 2 e 4.
- `compile_doc.py` testado com cópias do currículo e da carta de exemplo: 2 páginas e 1 página.
- **Não testado ainda:** os botões "Fazer currículo e carta" e "Montar meu perfil" de ponta a ponta.

### PRs

| PR | Assunto |
|---|---|
| #19 | Texto completo das vagas de agregadores (Remotar, Agrobase) |
| #20 | Painel local da busca (protótipo) |
| #21 | O painel com Meu perfil, avaliação de vagas e currículo e carta pelo Claude |
| #22 | `PAINEL.md` e `TUTORIAL.md`, e os testes do painel sem chamar o `gh` |

### Próxima sessão

- Rodar "Fazer currículo e carta" de ponta a ponta numa vaga real e conferir o checklist completo.
- Rodar "Montar meu perfil" num fork novo, só com um currículo, e conferir o que ele marca como inferido.
- Avaliar se o painel deve mostrar o currículo e a carta em PDF no próprio cartão.
- Testar o `COMECE-AQUI.md` com alguém sem experiência, num computador limpo.
