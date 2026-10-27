# Tutorial completo: da instalação à candidatura acompanhada

Este tutorial leva você do zero até uma candidatura enviada e acompanhada, passo a passo.
Seguimos uma pessoa de exemplo, a **Ana** (fictícia), em cada etapa, para você ver o que
fazer e o que esperar.

> **A Ana:** analista de dados com 4 anos de experiência, mora em Recife, quer uma vaga
> **remota**, aceita **CLT ou PJ**, busca nível **pleno ou sênior** e pretende **R$ 9 a 11 mil**
> em CLT.

Em cada etapa há dois caminhos. Escolha o que preferir, e misture à vontade:

| Caminho | Como é | Bom para |
|---|---|---|
| **Painel** | Botões numa página do navegador ([PAINEL.md](PAINEL.md)) | Quem não quer escrever comandos |
| **Conversa** | Você escreve para o Claude no VS Code (ex.: `/apply <link>`) | Acompanhar cada passo e corrigir junto |

---

## Sumário

1. [Antes de começar](#1-antes-de-começar)
2. [Monte o seu perfil](#2-monte-o-seu-perfil) (uma vez, 15 a 30 minutos)
3. [Encontre vagas](#3-encontre-vagas) (sempre que quiser, 5 minutos)
4. [Avalie uma vaga](#4-avalie-uma-vaga) (3 minutos por vaga)
5. [Gere currículo e carta](#5-gere-currículo-e-carta) (até meia hora por vaga)
6. [Revise antes de enviar](#6-revise-antes-de-enviar) (10 minutos, **não pule**)
7. [Envie a candidatura](#7-envie-a-candidatura)
8. [Acompanhe depois do envio](#8-acompanhe-depois-do-envio)
9. [Prepare-se para a entrevista](#9-prepare-se-para-a-entrevista)
10. [Sua rotina semanal](#10-sua-rotina-semanal)
11. [Mantenha tudo atualizado](#11-mantenha-tudo-atualizado)
12. [Glossário](#12-glossário)
13. [Perguntas frequentes](#13-perguntas-frequentes)

---

## 1. Antes de começar

**O que você vai precisar:**
- um computador com Windows, Mac ou Linux;
- uma assinatura do Claude (Pro ou Max), que você usa para conversar com ele;
- o seu currículo em PDF.

**Instalação:** se você nunca usou terminal nem GitHub, siga o [COMECE-AQUI.md](COMECE-AQUI.md)
até o Passo 5. Você instala dois programas com cliques (VS Code e Git) e pede o resto ao
Claude, em português. Se você já é da área técnica, o [README](README.md#início-rápido) e o
[SETUP.md](SETUP.md) são mais diretos.

**O que este projeto faz e o que não faz:**

| Faz | Não faz |
|---|---|
| Busca vagas em vários portais brasileiros | Não se candidata por você |
| Avalia se cada vaga combina com você | Não envia nada a empresa nenhuma |
| Escreve currículo e carta sob medida, sem inventar | Não inventa experiência nem competência |
| Prepara você para entrevistas | Não garante entrevista |
| Guarda tudo no seu computador | Não publica seus dados (se você usar um repositório privado) |

> **Privacidade:** o seu perfil fica em arquivos do projeto. Se você guardar o projeto no
> GitHub, use um repositório **privado** (o [SETUP.md](SETUP.md), seção 8, mostra como). O
> painel e o `/setup` avisam se o seu repositório for público.

---

## 2. Monte o seu perfil

O perfil é a base de tudo: a busca usa os cargos e níveis que você quer, a avaliação compara
as vagas com a sua experiência, e o currículo sai das suas informações reais. **Quanto melhor
o perfil, melhores os resultados.** Você faz isso uma vez e atualiza quando algo muda.

### Pelo painel

1. Abra o painel: dois cliques em `abrir-painel.bat` (Windows) ou `python3 tools/painel.py`.
   Ele abre no **Início**, que mostra o próximo passo. Na primeira vez, é montar o perfil:
   clique em **Ir para Meu perfil**.
2. **Seus documentos:** clique em **Enviar currículo (PDF)**. Se tiver, envie também o
   **LinkedIn (PDF)** (no LinkedIn: seu perfil > Mais > Salvar como PDF).
3. **O que o currículo não diz:** ao receber o PDF, o Claude já preenche o que der para tirar
   dele, com uma barra verde e a origem de cada campo. Confira, complete o resto e salve. Depois
   de conferir, o formulário da Ana ficou assim:

   ```
   Quem é você
     Cidade e UF ............ Recife - PE
     Escrever no ............ (•) feminino  ( ) masculino  ( ) neutro
     Idiomas ................ Português - nativo
                              Inglês - avançado
   O trabalho que você busca
     Cargos ................. Analista de Dados
                              Analista de BI
                              Data Analyst
     Níveis ................. [x] pleno  [x] sênior
     Competências ........... SQL, Power BI, Python
   Condições
     Modelo ................. [x] remoto
     Regimes ................ [x] CLT  [x] PJ
     Pretensão em CLT ....... R$ 9 a 11 mil
     Mínimo em PJ ........... R$ 13 mil
     Não aceita ............. vaga presencial; plantão de fim de semana
   ```

   Clique em **Salvar respostas**.
4. Clique em **Montar meu perfil com o Claude** e espere alguns minutos.
5. Role até **Mudanças propostas pelo Claude**, confira cada arquivo (verde entra, vermelho
   sai) e clique em **Aplicar ao meu perfil**. Antes disso, nada muda.

### Pela conversa

1. Copie o currículo para a pasta `documents/cv` (e o LinkedIn para `documents/linkedin`).
2. Escreva `/setup` para o Claude. Ele lê os documentos e pergunta o que falta, uma coisa de
   cada vez.

### Confira o resultado (os dois caminhos)

O Claude mostra o que propõe gravar (pelo painel, nada muda até você clicar em **Aplicar**; pela conversa, ele pergunta antes). **Leia com atenção estas três partes:**

- **Inferido:** o que ele deduziu dos documentos sem você ter dito (por exemplo, "prefere
  ambientes colaborativos"). Se não for verdade, corrija.
- **Lacunas:** o que ficou faltando. Quanto menos lacunas, melhores as avaliações.
- **Conflitos** (quando você atualiza um perfil existente): o que o currículo novo diz de
  diferente do que já estava gravado. O que estava gravado foi mantido; decida se quer trocar.

**Para corrigir,** escreva ao Claude, por exemplo: *"No meu perfil, tire 'prefere ambientes
colaborativos' e acrescente que liderei a migração do Excel para o Power BI em 2024."* Para
refazer só uma parte: `/setup --section search` (só as buscas), por exemplo.

> **Dica:** o perfil é a única fonte de verdade para o currículo. Uma conquista que não está
> no perfil não vai entrar em currículo nenhum, porque o Claude não inventa. Sempre que lembrar
> de um resultado com número ("reduzi o tempo do relatório de 2 dias para 2 horas"), peça para
> acrescentar ao perfil.

---

## 3. Encontre vagas

### Pelo painel

1. Aba **Vagas novas**, **Nova busca**. As prioridades 1 e 2 já vêm marcadas; escolha
   **Publicadas nos últimos 14 dias** e clique em **Buscar vagas**. Leva de 1 a 3 minutos, e a
   lista aparece logo abaixo.
2. Clique em **Classificar com o Claude**. Em alguns minutos, cada vaga ganha um encaixe (alto,
   médio ou baixo), uma nota e o motivo, e a lista passa a vir da melhor para a pior.
3. Use os filtros. A Ana escolheu **Encaixe alto ou médio**, **Remoto** e **Só sem avisos**.
4. Para cada vaga, olhe o cartão:

   ```
   ┌──────────────────────────────────────────────────────────┐
   │ [Encaixe alto · 84]                                      │
   │ Analista de Dados Pleno                                  │
   │ Acme Tecnologia                                          │
   │ SQL e Power BI no centro da vaga; pede dbt, que ela não  │
   │ usa no dia a dia                                         │
   │ [Brasil] [Remoto] [Pleno] [CLT] [Publicada em 20/10] [Gupy]│
   │ ⚠ texto diz "híbrido, 2x por semana em São Paulo"        │
   │ Ver vaga   [Me interessa]  [Descartar]                    │
   └──────────────────────────────────────────────────────────┘
   ```

   - **Me interessa** guarda a vaga para avaliar.
   - **Descartar** tira a vaga da lista e das próximas buscas.
   - Um **⚠ aviso** chama a atenção para algo que o rótulo do portal esconde. No exemplo, a
     vaga aparece como "remota", mas o texto diz híbrido: a Ana descartou.

### Pela conversa

Escreva `/scrape`. O Claude faz a mesma busca e já comenta o encaixe de cada vaga. Se vierem
muitas, `/rank` dá uma nota de triagem a todas e devolve a lista em ordem.

> **Dica:** não guarde tudo. Separe 3 a 5 vagas por semana que você realmente faria. Uma
> candidatura bem feita rende mais que dez genéricas.

---

## 4. Avalie uma vaga

### Pelo painel

Na aba **Me interessam**, clique em **Avaliar com o Claude** na vaga. Em 2 a 3 minutos, a
avaliação aparece no cartão.

### Pela conversa

Escreva `/apply` seguido do link da vaga, por exemplo
`/apply https://acme.gupy.io/jobs/1234567`. O Claude mostra a avaliação e pergunta se você
quer o currículo e a carta.

### Como ler a avaliação

| Parte | O que olhar |
|---|---|
| **Integridade da vaga** | `clean` é o normal. Um ⚠ quer dizer que o anúncio tem texto escondido ou suspeito: leia o que foi encontrado antes de seguir |
| **Origem** | Portal conhecido ou site oficial de recrutamento é bom sinal. "Host não verificado": confirme que a empresa existe antes de investir tempo |
| **Notas** | Competências, experiência, cultura e carreira, de 0 a 100. Local é aprovado ou reprovado |
| **Nota geral e veredito** | Strong Fit (75+), Good Fit (60-74), Moderate Fit (45-59), Weak Fit (30-44), Poor Fit (abaixo de 30) |
| **Regime e salário** | A referência salarial só aparece com a fonte consultada. Sem fonte: "não consultada" |
| **Lacunas** | O que a vaga pede e você não tem. É o que a carta vai precisar tratar com honestidade |

**A Ana recebeu:** nota geral 68, **Good Fit**. Pontos fortes: SQL, Power BI e 4 anos de
experiência. Lacuna: a vaga pede "experiência com dbt", que ela não tem. Recomendação:
candidatar, tratando a lacuna na carta.

**Quando pular:** Weak ou Poor Fit, um deal-breaker (presencial, quando você só aceita remoto),
ou um sinal de golpe (a vaga pede pagamento, Pix, dados bancários, ou só contato por WhatsApp).

---

## 5. Gere currículo e carta

### Pelo painel

No cartão da vaga, clique em **Fazer currículo e carta**. Pode levar até meia hora: você pode
fechar a aba e voltar depois, desde que a janela preta continue aberta.

### Pela conversa

Depois da avaliação do `/apply`, responda **sim** à pergunta "Quer que eu redija o currículo
e a carta?". Você acompanha cada etapa e pode pedir mudanças no meio.

### O que acontece por trás

1. O Claude escreve um currículo e uma carta para **esta** vaga, só com fatos do seu perfil.
2. Um segundo agente, que faz o papel de quem recruta, pesquisa a empresa e critica os
   rascunhos. O Claude revisa a partir da crítica.
3. Os PDFs são gerados e conferidos: currículo com **exatamente 2 páginas**, carta com **1**,
   nada cortado ou fora do lugar.
4. O currículo é lido como um sistema de recrutamento (ATS) o lê, para garantir que contatos,
   datas e palavras-chave chegam inteiros.
5. A candidatura entra na aba **Candidaturas** como **Rascunho**.

**Onde ficam os arquivos:** `cv/main_<empresa>_<cargo>.pdf` e
`cover_letters/cover_<empresa>_<cargo>.pdf`, na pasta do projeto.

> **Pelo painel, o Claude não pode perguntar nada.** Se a vaga tiver algo estranho (filtro de
> integridade com ⚠, origem não verificada), ele para e explica em vez de escrever. Nesse caso,
> leia o motivo e, se quiser seguir, faça pela conversa.

---

## 6. Revise antes de enviar

**Esta etapa é sua, e não dá para pular.** O Claude confere muita coisa, mas quem assina a
candidatura é você. Abra os dois PDFs e passe por esta lista:

**Currículo**
- [ ] Nome, telefone, e-mail e LinkedIn estão certos.
- [ ] Cargos, empresas e datas batem com a sua história.
- [ ] Nenhuma frase diz algo que você não fez, ou que não saberia explicar numa entrevista.
- [ ] Os números (percentuais, valores, prazos) são os seus.
- [ ] Tem 2 páginas e nada cortado.

**Carta**
- [ ] Está endereçada à empresa certa, com o nome certo da vaga.
- [ ] O que ela diz sobre a empresa é verdade (o Claude confere, mas confira também).
- [ ] As lacunas foram tratadas com honestidade, sem prometer o que você não tem.
- [ ] O tom soa como você.
- [ ] Cabe em 1 página.

**Para ajustar,** escreva ao Claude, por exemplo: *"No currículo da Acme, troque o segundo
tópico da experiência atual por algo sobre o painel de vendas que eu fiz"* ou *"Deixe a carta
mais direta no primeiro parágrafo."* Ele refaz e gera o PDF de novo.

> Se você corrigir um fato (uma data, uma conquista), peça também para atualizar o perfil.
> Senão, o próximo currículo repete o erro.

---

## 7. Envie a candidatura

1. Abra a vaga no site (o botão **Ver vaga** no painel).
2. Envie o **currículo em PDF**. A carta: se o site tem campo para anexo, anexe; se tem um
   campo de texto ("Por que você quer esta vaga?"), cole o conteúdo.
3. **Campos do formulário:** a Gupy e outros portais costumam pedir um resumo, perguntas de
   motivação e a **pretensão salarial**. Pela conversa, peça ao Claude: *"Escreva os campos de
   formulário da vaga da Acme"*. Ele respeita o limite de caracteres de cada campo e usa só
   fatos do seu perfil.
4. **Registre o envio:** escreva `/outcome Acme`. A candidatura passa de **Rascunho** para
   **Enviada**, e os documentos enviados ficam arquivados.

> **Dica sobre pretensão salarial:** quando a vaga não informa salário, use a faixa do seu
> perfil. Lembre que CLT e PJ não se comparam pelo número do anúncio: em PJ você paga
> impostos e não tem 13º, férias nem FGTS. A avaliação mostra a conta, e a aba **CLT × PJ**
> do painel faz a mesma conta com os números que você quiser.

---

## 8. Acompanhe depois do envio

| Situação | O que fazer |
|---|---|
| Passaram dias sem resposta | `/outcome followup` lista as candidaturas em silêncio há 10 dias ou mais e escreve um rascunho curto de mensagem de acompanhamento. Você revisa e envia; ele nunca envia nada |
| Chegou um e-mail da empresa | `/outcome Acme` e conte o que aconteceu (convite, teste, recusa). Ou use `/gmail-sync`, que lê o seu Gmail, sugere as mudanças e só grava depois da sua aprovação |
| Quer ver o funil inteiro | Aba **Candidaturas** do painel, ou `/html-report` para um relatório com gráficos |
| A candidatura acabou (sim ou não) | `/outcome Acme` com o resultado. Depois de algumas candidaturas resolvidas, o Claude sugere ajustar o método de avaliação com base no que de fato rendeu entrevistas |

**Situações na aba Candidaturas:** Rascunho → Enviada → Entrevista → Proposta → Contratação.
Ou, a qualquer momento, Não seguiu, Sem resposta, Desisti ou Proposta recusada.

---

## 9. Prepare-se para a entrevista

Quando marcar uma entrevista, registre (`/outcome Acme`, "entrevista com o RH na
quinta") e escreva **`/interview`**. O Claude monta um material para aquela etapa:
- o que a empresa leu de você (o currículo e a carta exatos que você enviou);
- a pesquisa da empresa e, quando há nome, de quem vai entrevistar;
- as perguntas prováveis, ligadas a exemplos seus no formato STAR (situação, tarefa, ação,
  resultado);
- respostas honestas para as lacunas (a Ana preparou como fala do dbt: "ainda não uso no dia a
  dia, mas modelo dados em SQL há 4 anos, que é a base dele");
- como responder sobre pretensão salarial e disponibilidade;
- perguntas para você fazer.

No fim, ele oferece uma **simulação**: faz as perguntas como quem entrevista e comenta as
suas respostas.

### Chegou uma proposta: CLT × PJ

A Ana chegou à última etapa e recebeu uma proposta PJ de R$ 14 mil por mês. Ela tinha pedido
R$ 10 mil em CLT, com VR de R$ 800 e plano de saúde de R$ 500. Na aba **CLT × PJ** do painel,
preencheu os dois lados e clicou em **Comparar**:

```
CLT  R$ 10.000 + benefícios ..... R$ 125.434 no ano (com FGTS e benefícios)
     PJ equivalente ............. R$ 12.902 por mês de nota
PJ   R$ 14.000 × 11 meses ....... R$ 136.417 no ano
     CLT equivalente ............ R$ 11.023 por mês de salário
Resultado: o PJ dá R$ 10.983 a mais por ano
```

A proposta passa da pretensão dela, mas com folga de uns 9%, não os 40% que o "R$ 14 mil
contra R$ 10 mil" sugere. Antes de responder, ela pediu ao contador para confirmar a alíquota
da atividade dela.

---

## 10. Sua rotina semanal

Uma rotina que cabe em uma ou duas horas por semana:

| Quando | O quê | Onde |
|---|---|---|
| Segunda | Buscar vagas dos últimos 7 dias, classificar e separar 3 a 5 | Painel: Vagas novas |
| Segunda | Avaliar as separadas | Painel: Me interessam |
| Terça a quinta | Gerar, **revisar** e enviar as que valem a pena; registrar com `/outcome` | Painel e conversa |
| Sexta | `/outcome followup` para as que estão em silêncio; `/gmail-sync`, se usar | Conversa |
| Quando marcar | `/interview` | Conversa |

---

## 11. Mantenha tudo atualizado

| Quando | O que fazer |
|---|---|
| Mudou de emprego, terminou um curso, conseguiu um resultado novo | Envie o currículo novo em **Meu perfil** e clique em **Atualizar meu perfil**, ou peça na conversa |
| Quer mudar o tipo de vaga que busca | `/setup --section search`, ou ajuste cargos e níveis no formulário e atualize o perfil |
| As avaliações mostram sempre a mesma lacuna | `/upskill` mostra as lacunas mais frequentes nas vagas que você acompanha e monta um plano de estudos |
| Tem GitHub, portfólio ou Lattes | `/expand` procura competências que o perfil ainda não tem nessas fontes |
| Saiu uma versão nova do projeto | Peça ao Claude: *"Atualize o projeto com a versão nova do repositório original"* (o [SETUP.md](SETUP.md), seção 8, tem os detalhes) |

---

## 12. Glossário

| Termo | O que é |
|---|---|
| **ATS** | Sistema de recrutamento (Gupy, Sólides, Workday) que lê o currículo antes de uma pessoa. Lê o texto do PDF, não o desenho |
| **CLT** | Emprego com carteira assinada: 13º, férias com 1/3, FGTS |
| **PJ** | Você presta serviço pela sua empresa e emite nota: sem 13º, férias pagas nem FGTS, e paga os impostos |
| **Deal-breaker** | Condição que elimina a vaga para você (presencial, por exemplo) |
| **Encaixe (fit)** | Quanto a vaga combina com você. Vai de Strong Fit a Poor Fit |
| **Filtro de integridade** | Verificação do texto da vaga atrás de conteúdo escondido ou suspeito |
| **Perfil** | Os arquivos com a sua história, competências e preferências. Fonte única para tudo o que o Claude escreve |
| **Repositório privado** | Uma cópia do projeto no GitHub que só você vê |
| **STAR** | Jeito de contar uma experiência: situação, tarefa, ação, resultado |
| **Tracker** | A planilha das candidaturas (`job_search_tracker.csv`), que a aba Candidaturas mostra |

---

## 13. Perguntas frequentes

**O Claude pode inventar coisas no meu currículo?**
Ele é instruído a usar só fatos do seu perfil e confere cada afirmação contra ele. Mesmo
assim, revise sempre (Etapa 6): você é quem responde pelo que enviou.

**Quanto isso custa?**
O projeto é gratuito. O Claude usa o seu plano, como numa conversa. A busca de vagas não usa
o Claude.

**Meus dados vão para algum lugar?**
Ficam no seu computador. O conteúdo das conversas passa pelo Claude, como em qualquer conversa
no claude.ai. Se você guardar o projeto no GitHub, use um repositório privado.

**Posso usar só o painel, sem conversar com o Claude?**
Sim, para o perfil, a busca, a avaliação e o currículo e a carta. Registrar o resultado
(`/outcome`), preparar entrevista (`/interview`) e os campos de formulário ainda são pela
conversa.

**Uma vaga veio com ⚠. Devo descartar?**
Não necessariamente. Leia o aviso: às vezes é só o modelo de trabalho divergente entre o portal
e o texto. Vale o texto da vaga.

**O painel não abre, ou um botão não funciona.**
Veja a tabela [Quando algo não funciona](PAINEL.md#quando-algo-não-funciona) do PAINEL.md.

**Quero recomeçar do zero.**
Escreva `/reset` para apagar o perfil e depois `/setup` de novo (o [README](README.md#recomeçar-do-zero)
explica o que é apagado).
