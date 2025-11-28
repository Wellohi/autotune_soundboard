import tkinter as tk
from tkinter import filedialog, messagebox
import pygame
import keyboard
import os

# A classe 'SoundboardApp' encapsula toda a lógica do nosso programa.

class SoundboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Soundboard")
        self.root.geometry("500x400")

        # 1. Inicializando o Mixer de Áudio
        # O mixer é o motor que combina e toca os sons.
        pygame.mixer.init()

        # Dicionário para guardar nossos sons carregados.
        # Estrutura: { "tecla_atalho": objeto_som_pygame }
        self.sound_map = {}
        
        # Lista visual para mostrar ao usuário o que está configurado
        self.hotkey_list = []

        self._setup_ui()

    def _setup_ui(self):
        """Configura os elementos visuais da janela."""
        
        # Frame de topo para adicionar novos sons
        control_frame = tk.Frame(self.root, pady=10)
        control_frame.pack(fill="x")

        tk.Label(control_frame, text="Tecla de Atalho (ex: q, ctrl+g):").pack(side="left", padx=5)
        
        # Entry: onde o usuário digita
        self.hotkey_entry = tk.Entry(control_frame, width=10)
        self.hotkey_entry.pack(side="left", padx=5)

        # Botão que chama a função de adicionar
        btn_add = tk.Button(control_frame, text="Selecionar MP3 & Adicionar", command=self.add_sound_dialog)
        btn_add.pack(side="left", padx=5)

        # Lista de sons configurados
        self.listbox = tk.Listbox(self.root, width=60, height=15)
        self.listbox.pack(pady=10, padx=10)

        # Instruções
        lbl_info = tk.Label(self.root, text="Dica: O app deve ficar aberto para os atalhos funcionarem.\nInstale 'VB-Cable' para usar como microfone.", fg="gray")
        lbl_info.pack(side="bottom", pady=5)

    def add_sound_dialog(self):
        """Lógica para selecionar arquivo e vincular ao atalho."""
        
        # 1. Obter o atalho digitado
        hotkey = self.hotkey_entry.get().lower()
        
        if not hotkey:
            messagebox.showwarning("Atenção", "Digite uma tecla de atalho primeiro! (ex: F1, a, ctrl+b)")
            return

        # 2. Abrir janela de seleção de arquivo
        # filedialog é nativo do OS, muito útil em scripts de automação.
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
        
        if file_path:
            try:
                self.register_sound(hotkey, file_path)
            except Exception as e:
                # Tratamento de erro é essencial. Se o arquivo estiver corrompido, o app não fecha.
                messagebox.showerror("Erro", f"Não foi possível carregar o áudio:\n{e}")

    def register_sound(self, hotkey, file_path):
        """
        A 'Mágica' acontece aqui.
        Carregamos o som na memória e criamos o 'gancho' (hook) no teclado.
        """
        
        # Carrega o som na memória do Pygame (Sound Object)
        # Diferença importante: 'Sound' carrega tudo na RAM (rápido, arquivos curtos).
        # 'music.load' faz streaming (lento, arquivos longos). Para soundboard, usamos Sound.
        sound_effect = pygame.mixer.Sound(file_path)
        
        # Guardamos no dicionário
        self.sound_map[hotkey] = sound_effect

        # Atualiza a interface visual
        filename = os.path.basename(file_path)
        display_text = f"[{hotkey}] -> {filename}"
        self.listbox.insert(tk.END, display_text)
        
        # --- O GLOBAL HOOK ---
        # Aqui usamos a biblioteca 'keyboard'.
        # add_hotkey roda em background. Quando a tecla é detectada, ela chama 'self.play_sound'.
        # O lambda é uma função anônima, necessária para passar argumentos para a função play_sound.
        try:
            keyboard.add_hotkey(hotkey, lambda: self.play_sound(hotkey))
            print(f"Atalho registrado: {hotkey}") # Log para debug no console
        except Exception as e:
            messagebox.showerror("Erro de Atalho", f"Tecla inválida: {e}")

    def play_sound(self, hotkey):
        """Função chamada quando o atalho é pressionado."""
        if hotkey in self.sound_map:
            print(f"Tocando som para: {hotkey}")
            # .play() é assíncrono (fire and forget).
            self.sound_map[hotkey].play()

# --- Bloco de Execução Principal ---
if __name__ == "__main__":
    # Verifica se as dependências estão instaladas
    try:
        import keyboard
        import pygame
    except ImportError:
        print("ERRO CRÍTICO: Você precisa instalar as bibliotecas.")
        print("Rode no terminal: pip install keyboard pygame")
        exit()

    root = tk.Tk()
    app = SoundboardApp(root)
    
    # Inicia o loop da interface gráfica. Nada abaixo disso roda até a janela fechar.
    root.mainloop()