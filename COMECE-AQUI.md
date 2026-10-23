# Comece aqui: instalação sem terminal

Este guia é para quem nunca usou terminal nem GitHub. Você instala dois programas com
cliques e, a partir daí, **pede em português** para o Claude fazer o resto. Leva uns 40
minutos, a maior parte esperando downloads.

Se você já usa terminal e git, o [SETUP.md](SETUP.md) é mais direto.

## O que você precisa

- Um computador com **Windows 10 ou 11** (no Mac os passos são parecidos; veja o fim).
- Uma **assinatura do Claude** (Pro ou Max) em [claude.ai](https://claude.ai). O plano gratuito
  não dá acesso ao Claude Code.
- Uns **3 GB livres** no disco.
- O seu **currículo em PDF**. Se ele estiver no Word, abra e use Arquivo → Salvar como → PDF.

## Passo 1: instale o VS Code

O VS Code é o programa onde você vai conversar com o Claude e ver os arquivos.

1. Baixe em [code.visualstudio.com](https://code.visualstudio.com) (botão azul "Download for Windows").
2. Abra o instalador e vá clicando em "Próximo". Pode aceitar tudo como vem.

## Passo 2: instale o Git

O Claude Code usa o Git no Windows. Você não vai precisar mexer nele.

1. Baixe em [git-scm.com/download/win](https://git-scm.com/download/win)
   ("Click here to download").
2. Abra o instalador e clique em "Next" até o fim, sem mudar nada.

> **O instalador parou e não acontece nada?** A janela que pede permissão de administrador
> às vezes fica escondida atrás das outras. Procure um ícone piscando na barra de tarefas e
> clique em "Sim".

## Passo 3: ligue o Claude no VS Code

1. Abra o VS Code.
2. Na barra da esquerda, clique no ícone de quatro quadradinhos (**Extensões**).
3. Procure **Claude Code**, confira se o autor é a **Anthropic** e clique em **Install**.
4. Clique no ícone do Claude que apareceu e entre com a sua conta do claude.ai.
5. Abra uma pasta para trabalhar: menu **File → Open Folder** (Arquivo → Abrir Pasta),
   escolha **Documentos** e confirme. Se o VS Code perguntar se você confia nos autores da
   pasta, responda que sim.

**Como funciona a conversa:** você escreve no painel do Claude como num chat. Antes de rodar
qualquer comando no seu computador, ele mostra o comando e **pede licença**. Leia e clique em
permitir. Se não entender um comando, pergunte "o que esse comando faz?" antes de permitir.

## Passo 4: peça ao Claude para instalar o resto

O projeto precisa de mais três programas: o **Python** (ferramentas de apoio), o **Bun**
(busca nos portais de vagas) e o **MiKTeX** (gera o PDF do currículo e da carta). Copie e
cole esta mensagem no painel do Claude:

```text
Instale o que o projeto job-pindorama precisa neste Windows, usando o winget:
Python 3.12, Bun e MiKTeX. Depois configure o MiKTeX para instalar pacotes sem
perguntar (initexmf --set-config-value=[MPM]AutoInstall=1). Me explique cada
comando em uma frase antes de rodar.
```

Quando ele terminar, **feche o VS Code e abra de novo**. Os programas novos só ficam visíveis
depois disso. Em seguida, cole:

```text
Confira se o Python, o Bun e o lualatex estão funcionando.
```

## Passo 5: baixe o projeto

Cole esta mensagem:

```text
Baixe o projeto com git clone https://github.com/rosanapegasgodoy/job-pindorama.git
dentro da minha pasta Documentos e, dentro dele, rode
python tools/install_portal_clis.py.
```

Depois abra a pasta do projeto: **File → Open Folder → Documentos → job-pindorama**. Daqui
em diante, sempre abra o VS Code nessa pasta.

## Passo 6: configure o seu perfil

1. Copie o seu currículo em PDF para a pasta `Documentos\job-pindorama\documents\cv`, pelo
   Explorador de Arquivos. Se tiver, ponha também o PDF do seu perfil do LinkedIn em
   `documents\linkedin`, diplomas em `documents\diplomas` e cartas de recomendação em
   `documents\references`. Antes, se quiser, tire do currículo CPF, RG e data de nascimento:
   a busca de vagas não precisa deles.
2. No painel do Claude, escreva **`/setup`** e envie.

O Claude lê os seus documentos e faz perguntas sobre o que faltar: os regimes que você aceita
(CLT, PJ, estágio), a pretensão salarial, o modelo de trabalho, a senioridade que faz sentido
buscar e o gênero gramatical para os textos. Responda com calma; dá para mudar tudo depois.

**Prefere botões?** O painel (veja [O painel](#o-painel-buscar-e-avaliar-vagas-com-botões)) tem a
aba **Meu perfil**, que faz o mesmo sem conversa:

1. **Seus documentos:** envie o currículo e, se tiver, o PDF do LinkedIn. Eles vão para as
   pastas `documents\cv` e `documents\linkedin`.
2. **O que o currículo não diz:** um formulário curto (cidade, gênero gramatical, idiomas,
   cargos, níveis, modelo de trabalho, regimes, pretensão). Clique em "Salvar respostas".
3. **Montar meu perfil com o Claude:** ele lê os documentos e as respostas e grava o perfil.
   Leva alguns minutos. No fim, aparece o que ele gravou, o que deduziu sozinho e o que
   ficou faltando.

Se você já tem perfil, o botão vira "Atualizar meu perfil": ele acrescenta o que é novo,
mantém o que já existe e lista as diferenças para você revisar. Confira sempre a lista
**"inferido"**: é o que o Claude deduziu, não o que você disse. Se o projeto estiver ligado a
um repositório público no GitHub, o painel avisa antes e pede a sua confirmação.

## Passo 7: use

| Escreva no Claude | O que acontece |
|---|---|
| `/scrape` | Busca vagas compatíveis com o seu perfil em vários portais brasileiros |
| `/rank` | Pontua e ordena muitas vagas de uma vez |
| `/apply` seguido do link da vaga | Avalia a vaga e, se você quiser, escreve currículo e carta sob medida |
| `/interview` | Prepara você para uma entrevista marcada |

O Claude sempre pergunta antes de seguir para a próxima etapa. **Nada é enviado a empresa
nenhuma:** quem se candidata é você, com os arquivos que ele preparou.

### O painel: buscar e avaliar vagas com botões

Para buscar e avaliar vagas com botões, sem escrever nada: abra a pasta do projeto no
Explorador de Arquivos e dê **dois cliques em `abrir-painel.bat`**. Abre uma janela preta (deixe
aberta, pode minimizar) e o navegador com o painel. Se o navegador não abrir sozinho, copie o
endereço que aparece na janela preta (`http://127.0.0.1:8765/`) e cole no navegador.

- **Meu perfil:** os seus documentos, o formulário e o botão que monta o perfil (veja o
  Passo 6). Enquanto o perfil não existe, o painel abre nesta aba.
- **Buscar:** escolha as prioridades e clique em "Buscar vagas" (leva de 1 a 3 minutos).
- **Vagas novas:** filtre por modelo de trabalho e portal, veja os avisos e abra cada vaga.
  "Me interessa" guarda a vaga; "Descartar" tira da lista. As duas somem das próximas buscas.
- **Me interessam:** as vagas guardadas, cada uma com três botões:
  - **Avaliar com o Claude:** a nota de encaixe, os pontos fortes e as lacunas aparecem ali
    mesmo, no cartão da vaga (leva alguns minutos).
  - **Fazer currículo e carta:** depois da avaliação, o Claude escreve, revisa e gera os PDFs,
    e a vaga entra em Candidaturas (pode levar meia hora). Os arquivos ficam nas pastas `cv` e
    `cover_letters`.
  - **Copiar pedido:** para fazer tudo isso conversando com o Claude no VS Code, acompanhando
    e corrigindo junto.
- **Candidaturas:** as candidaturas registradas pelo `/apply`.

O Claude trabalha numa vaga por vez e usa o seu plano, como numa conversa. Pelo painel ele não
pode perguntar nada: se a vaga tiver algo estranho, ele para e avisa, e você decide na conversa.
**Confira sempre o currículo e a carta antes de enviar.**

O [PAINEL.md](PAINEL.md) explica o fluxo inteiro aba por aba, o que cada aviso quer dizer e o
que fazer quando algo não funciona.

Para fechar o painel, feche a janela preta. O painel só funciona no seu computador. Além das
buscas nos portais, só o Claude sai para a internet, para ler a vaga e pesquisar a empresa.

## Seus dados

- O seu perfil, o seu currículo e as vagas ficam **só no seu computador**, na pasta do projeto.
- Não publique essa pasta no GitHub nem em outro lugar público. Se um dia quiser uma cópia de
  segurança na nuvem, peça ajuda ao Claude para criar um repositório **privado**.
- O conteúdo das conversas passa pelo Claude, como em qualquer conversa no claude.ai.

## Atualizar o projeto

De tempos em tempos, o job-pindorama ganha portais e correções. Para receber, cole:

```text
Traga as atualizações do job-pindorama com git pull, mantendo as minhas
personalizações. Se houver conflito, me explique antes de resolver.
```

## Problemas comuns

- **"python" abre a Microsoft Store:** feche e abra o VS Code. Se continuar, vá em
  Configurações do Windows → Aplicativos → Aliases de execução de aplicativo e desligue
  "python.exe" e "python3.exe".
- **"bun não é reconhecido" ou "lualatex não é reconhecido":** o VS Code foi aberto antes
  da instalação. Feche e abra de novo.
- **Um instalador parece travado:** procure a janela de permissão escondida na barra de
  tarefas (veja o passo 2).
- **Qualquer outra coisa:** descreva o problema para o Claude com as suas palavras e cole a
  mensagem de erro. Ele também conhece o [SETUP.md](SETUP.md), que tem a seção
  "Solução de problemas".

## No Mac

Os passos são os mesmos, com três diferenças:

- No passo 2, não precisa baixar o Git: se ele faltar, o próprio Mac oferece instalar na
  primeira vez que for usado.
- No passo 4, peça: "Instale o que o projeto job-pindorama precisa neste Mac: Python, Bun e
  uma distribuição LaTeX, seguindo o SETUP.md. Me explique cada comando antes de rodar."
- Os caminhos usam `/` em vez de `\`.
