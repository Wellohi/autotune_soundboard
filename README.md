# 🎛️ Soundboard Pro Python - Manual de Engenharia e Operação

Este projeto é uma aplicação desktop de Soundboard desenvolvida em Python, projetada para roteamento de áudio avançado (VoIP, Discord, Games). Ele utiliza pygame para manipulação de áudio de baixa latência e keyboard para ganchos globais de teclado.

## 🏗️ FASE 1: Build & Deploy (Do Código ao Executável)

O primeiro passo é transformar seu script Python (.py) em um executável (.exe) portátil, para que ele rode fora do ambiente de desenvolvimento.

### 1. Preparação do Ambiente

Certifique-se de estar na pasta do projeto via terminal (CMD/PowerShell) e que as dependências estejam instaladas.

```
pip install pyinstaller keyboard pygame
```

### 2. O Processo de "Freeze" (Compilação)

Utilizaremos o PyInstaller. Precisamos usar flags específicas para garantir que o módulo de áudio avançado (pygame._sdl2), que normalmente fica oculto, seja incluído no pacote.

Execute o comando abaixo (em uma única linha):

```
pyinstaller --noconsole --onefile --name="SoundboardPro" --hidden-import="pygame._sdl2" soundboard_app.py
```


**--noconsole: Executa como aplicação GUI (sem janela preta de terminal).**

**--onefile: Empacota DLLs e Python em um único arquivo .exe.**

**--hidden-import="pygame._sdl2": Crítico. Força a inclusão do driver de seleção de dispositivos de áudio.**


### 3. Localização do Artefato

Após a compilação, o executável estará na pasta:
./dist/SoundboardPro.exe

**Nota: Ao mover o .exe para outra pasta, lembre-se que o arquivo de configuração soundboard_config.json será criado automaticamente no mesmo diretório onde o .exe estiver.**

## 🎚️ FASE 2: Engenharia de Áudio (Infraestrutura)

Para que o som saia no seu microfone sem eco e com alta qualidade, precisamos preparar os "cabos virtuais".

### 1. Instalação de Drivers

Baixe e instale os seguintes softwares (Requer Reinicialização):

VB-Audio Cable (O cabo simples).

Voicemeeter Banana (A mesa de som virtual).

### 2. Sincronização de Frequência (Sample Rate) - Crucial para Qualidade

O Python foi configurado para 48.000Hz (48kHz). Se o Windows estiver em 44.1kHz, o som ficará estourado ou com velocidade errada (pitch shift).

Abra o Painel de Som do Windows (Win+R -> mmsys.cpl).

Vá na aba Reprodução:

Voicemeeter Input (VAIO): Propriedades -> Avançado -> 24 bit, 48000 Hz.

Voicemeeter Aux Input: Propriedades -> Avançado -> 24 bit, 48000 Hz.

Vá na aba Gravação:

Voicemeeter Output: Propriedades -> Avançado -> 24 bit, 48000 Hz.

Voicemeeter Aux Output: Propriedades -> Avançado -> 24 bit, 48000 Hz.

## 🔀 FASE 3: Matriz de Roteamento (Voicemeeter Banana)

O objetivo aqui é separar o som do seu Jogo (que só você ouve) do som do Soundboard (que seus amigos ouvem).

Abra o Voicemeeter Banana e configure as colunas:

1. Saída Física (Monitoramento)

No canto superior direito (A1), selecione seu Fone de Ouvido Real (preferência por drivers WDM ou KS).

2. Colunas de Entrada (Inputs)

**Coluna ---------- O que é? ---------- Configuração de Botões ---------- Explicação Técnica**

**Hardware Input 1 ---------- Selecione seu Microfone Físico ---------- Desmarque A1 e Marque B1 ---------- B1 envia sua voz para o Discord. A1 desligado evita que você ouça sua própria voz (retorno).**

**Voicemeeter VAIO ---------- Som do Windows/Jogos ---------- Marque A1 e Desmarque B1 ---------- A1 envia o jogo para seu fone. B1 desligado impede que o jogo vaze no microfone.**

**Voicemeeter AUX ----------  Som do Python App ---------- Marque A1 e Marque B1 ---------- Envia o meme para seu fone (A1) E para o Discord (B1) ao mesmo tempo.**

## 🚀 FASE 4: Execução e Configuração Final

### 1. Configurando o Windows

Defina a Saída Padrão do Windows para: Voicemeeter Input (VB-Audio Voicemeeter VAIO).

Isso joga todo o som do PC na coluna do meio do Voicemeeter.

### 2. Configurando o App (SoundboardPro.exe)

Abra o App (como Administrador se os atalhos falharem).

Na lista de dispositivos, selecione: Voicemeeter Aux Input (VB-Audio Voicemeeter AUX VAIO).

Clique em "Mudar Dispositivo de Saída".

Ajuste o volume se necessário.

### 3. Configurando o Discord/Teams

Dispositivo de Entrada (Microfone): Selecione Voicemeeter Output (VB-Audio Voicemeeter VAIO).

Nota: O canal B1 do Voicemeeter corresponde a essa saída.

## 🆘 Troubleshooting (Solução de Problemas)

Som "Picotando" ou "Robótico":

Geralmente é conflito de Sample Rate. Verifique a FASE 2.

Se persistir, aumente o AUDIO_BUFFER no código Python para 4096 e recompile.

Erro ao abrir o .exe:

Verifique se usou a flag --hidden-import="pygame._sdl2" no build.

Atalhos não funcionam em jogos (Tela Cheia):

Execute o SoundboardPro.exe como Administrador. Alguns jogos bloqueiam a leitura de teclado de apps comuns.