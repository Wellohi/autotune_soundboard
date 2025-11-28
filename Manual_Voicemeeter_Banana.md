# Manual de Arquitetura de Áudio: Voicemeeter Banana

*O objetivo desta configuração é o Isolamento de Canais.*
### Queremos que:

*Jogos/Windows: Saiam no seu fone (Você ouve) -> NÃO vai para o Discord.*

*Sua Voz: Vai para o Discord + Opcionalmente para seu fone (Retorno).*

*Python Soundboard: Vai para o Discord (Amigos ouvem) + Vai para seu fone (Você ouve).*

## 1. Conceitos Fundamentais do Voicemeeter

*Olhando para a interface do Voicemeeter Banana, você verá várias colunas (Strips). Entenda a lógica de roteamento:*

*HARDWARE OUT (Canto Superior Direito): São suas saídas FÍSICAS.*

*A1: Seu Fone de Ouvido Principal.*

*Botões de Roteamento (A1, A2, B1, B2): Existem em cada coluna de entrada.*

*A1: Manda o som dessa coluna para o seu Fone (Monitoramento).*

*B1: Manda o som dessa coluna para a Saída Virtual (O que o Discord escuta).*

## 2. Passo a Passo da Configuração

*A. Configurando as Saídas (Sinks)*

*No Voicemeeter, clique em Hardware Out A1 (Canto superior direito).*

*Selecione seu Fone de Ouvido / Headset (Dê preferência para "WDM" ou "KS", pois têm menos latência que "MME").*

*B. Configurando as Entradas (Sources)*

*Coluna 1: Seu Microfone Físico*

*Clique no nome "Hardware Input 1".*

*Selecione seu Microfone real.*

*Roteamento (Atenção aqui!):*

*Desmarque A1 (Senão você ouvirá sua própria voz com eco).*

*Marque B1 (Para sua voz ir para o Discord).*

*Coluna Virtual: O Som do Windows (Jogos/Spotify)*

*O Voicemeeter instala um dispositivo chamado "Voicemeeter Input (VAIO)".*

*Vá nas configurações de som do Windows.*

*Mude a Saída Padrão para Voicemeeter Input (VB-Audio Voicemeeter VAIO).*

*Agora, todo som do PC entra na coluna "Voicemeeter VAIO" do programa.*

*No programa Voicemeeter, na coluna Voicemeeter VAIO:*

*Marque A1 (Para você ouvir o jogo no fone).*

*DESMARQUE B1 (CRUCIAL: Isso impede que o jogo vá para o Discord).*

*Coluna Virtual Auxiliar: O Python Soundboard*

*O Voicemeeter tem uma segunda entrada virtual chamada "Voicemeeter AUX". Vamos usar essa via exclusiva para o seu app.*

*Abra seu App Python (soundboard_app.py).*

*No seletor que criamos, escolha: Voicemeeter Aux Input (VB-Audio Voicemeeter AUX VAIO).*

*No programa Voicemeeter, na coluna Voicemeeter AUX:*

*Marque A1 (Para você ouvir o meme/áudio).*

*Marque B1 (Para seus amigos ouvirem o meme/áudio).*

## 3. O Destino Final (Discord/Teams)

*Agora precisamos dizer ao Discord para pegar tudo o que foi jogado no canal B1.*

*Abra o Discord -> Configurações -> Voz e Vídeo.*

*Dispositivo de Entrada (Input): Selecione Voicemeeter Output (VB-Audio Voicemeeter VAIO).*

*Nota técnica: O canal B1 corresponde ao "Voicemeeter Output". (O canal B2 corresponderia ao "Voicemeeter Aux Output", mas não estamos usando o B2 hoje).*

*Dispositivo de Saída (Output): Selecione Voicemeeter Input ou seu Fone direto.*

### Resumo da Matriz de Roteamento*

*Fonte (Source) - Vai para A1 (Seu Ouvido) - Vai para B1 (Discord)*

*Microfone       -         ❌ (Não)         -        ✅ (Sim)*

*Windows (Jogo)  -         ✅ (Sim)        -         ❌ (Não)*

*Python App      -         ✅ (Sim)        -         ✅ (Sim)*


*Isso resolve o problema de "Vazamento" de áudio perfeitamente!*