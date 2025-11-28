# Arquitetura do Soundboard Python


### 1. O Padrão de Projeto: Event-Driven Programming (Programação Orientada a Eventos)

Diferente de scripts de análise de dados que rodam do topo para baixo (top-down) e terminam, uma interface gráfica (GUI) precisa ficar "viva" esperando o usuário fazer algo.

O Loop Principal (root.mainloop): O tkinter cria um loop infinito que desenha a janela 60 vezes por segundo (aproximadamente) e verifica se houve cliques.

O Listener de Teclado: A biblioteca keyboard cria uma thread (linha de execução) separada que fica "escutando" o sistema operacional. Quando você aperta a tecla, ela injeta um comando para o nosso código tocar o som.

### 2. Por que Pygame para o Áudio?

Poderíamos usar bibliotecas nativas como playsound, mas elas bloqueiam o código.

Bloqueante vs. Não-Bloqueante: Se usássemos uma lib simples, ao tocar um áudio de 5 segundos, a interface travaria por 5 segundos. O pygame.mixer toca o som em um canal separado, permitindo que o código continue rodando (assíncrono). Isso é vital para um Soundboard, pois você pode querer tocar dois sons ao mesmo tempo ou parar um som no meio.

### 3. Estrutura de Dados

Para gerenciar os sons, utilizaremos um Dicionário Python (dict).
Esta é a estrutura de dados mais importante para um Cientista de Dados.

Chave: O atalho (ex: "alt+g").

Valor: O caminho do arquivo (ex: "C:/sons/risada.mp3").

Isso permite busca rápida O(1) quando uma tecla é pressionada.

### 4. O Fluxo do "Microfone" (Virtual Audio Cable)

O código Python enviará o áudio para o dispositivo de saída padrão do Windows.
Para que isso saia no seu microfone em jogos/calls:

Instale um driver de cabo virtual (ex: VB-Cable).

No Windows, defina a "Saída de Áudio" para o cabo virtual.

No app de destino (Discord, etc), defina a "Entrada" (Microfone) para o cabo virtual.



### RODAR APP:

```
python soundboard_app.py
```



## TO-DO

*Fazer com que o app receba o audio do microfone para poder ser usado (como do discord) enquanto pode aplicar os audios salvos*
