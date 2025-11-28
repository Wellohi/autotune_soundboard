import tkinter as tk
from tkinter import filedialog, messagebox
import pygame
import keyboard
import os
import json  # BIBLIOTECA NOVA: Para ler e escrever arquivos de configuração

# --- NOTA DO PROFESSOR ---
# Persistência de Dados (Data Persistence):
# O computador tem Memória Volátil (RAM) e Não-Volátil (Disco).
# Até agora, usávamos só RAM. Agora usaremos JSON para salvar no Disco.

CONFIG_FILE = "soundboard_config.json"

class SoundboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Soundboard - Com Persistência")
        self.root.geometry("500x480")

        pygame.mixer.init()

        # Dicionário 1: Mapeia Atalho -> Objeto de Som (Usado para TOCAR - RAM)
        self.sound_map = {}
        
        # Dicionário 2: Mapeia Atalho -> Caminho do Arquivo (Usado para SALVAR - Disco)
        self.saved_data = {}

        self._setup_ui()
        self._setup_global_hotkeys()
        
        # Carrega os dados salvos assim que o app abre
        self.load_config()

    def _setup_ui(self):
        """Configura os elementos visuais da janela."""
        control_frame = tk.Frame(self.root, pady=10)
        control_frame.pack(fill="x")

        tk.Label(control_frame, text="Clique e pressione o atalho:").pack(side="left", padx=5)
        
        self.hotkey_entry = tk.Entry(control_frame, width=15, bg="#f0f0f0")
        self.hotkey_entry.pack(side="left", padx=5)
        self.hotkey_entry.bind("<Key>", self._on_key_press)

        btn_add = tk.Button(control_frame, text="Adicionar MP3", command=self.add_sound_dialog, bg="#d9ffcc")
        btn_add.pack(side="left", padx=5)

        btn_remove = tk.Button(control_frame, text="Remover Selecionado", command=self.remove_selected_sound, bg="#ffcccc")
        btn_remove.pack(side="left", padx=5)

        self.listbox = tk.Listbox(self.root, width=60, height=15)
        self.listbox.pack(pady=10, padx=10)

        info_text = (
            "Dica: O app salva suas configurações automaticamente.\n"
            "Instale 'VB-Cable' para usar como microfone.\n"
            "🛑 ATALHO DE EMERGÊNCIA: 'Alt+P' para parar todos os sons."
        )
        lbl_info = tk.Label(self.root, text=info_text, fg="gray", justify="center")
        lbl_info.pack(side="bottom", pady=5)

    def _setup_global_hotkeys(self):
        try:
            keyboard.add_hotkey('alt+p', self.stop_all_sounds)
        except Exception as e:
            print(f"Erro global hotkey: {e}")

    def stop_all_sounds(self):
        pygame.mixer.stop()
        print("🛑 STOP: Todos os sons foram interrompidos.")

    # --- NOVO BLOCO: PERSISTÊNCIA DE DADOS ---

    def load_config(self):
        """Lê o arquivo JSON e restaura os atalhos."""
        if not os.path.exists(CONFIG_FILE):
            return  # Se o arquivo não existe (primeira vez usando), não faz nada.

        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                
            print(f"Carregando configuração: {data}")
            
            # Itera sobre os dados salvos e registra um por um
            for hotkey, file_path in data.items():
                # Verificação de segurança: O arquivo mp3 ainda existe no computador?
                if os.path.exists(file_path):
                    # silent=True evita pipocar 10 janelas de "Sucesso" ao abrir o app
                    self.register_sound(hotkey, file_path, silent=True)
                else:
                    print(f"Aviso: Arquivo {file_path} não encontrado. Ignorando.")
                    
        except Exception as e:
            messagebox.showerror("Erro de Configuração", f"Falha ao carregar save:\n{e}")

    def save_config(self):
        """Escreve o dicionário de caminhos no arquivo JSON."""
        try:
            with open(CONFIG_FILE, 'w') as f:
                # indent=4 deixa o arquivo bonitinho para humanos lerem
                json.dump(self.saved_data, f, indent=4)
            print("Configuração salva com sucesso.")
        except Exception as e:
            print(f"Erro ao salvar configuração: {e}")

    # ------------------------------------------

    def remove_selected_sound(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um item para remover.")
            return
        
        index = selection[0]
        item_text = self.listbox.get(index)
        hotkey_to_remove = item_text.split(']')[0].replace('[', '')
        
        # 1. Remove do Sistema (Keyboard) e Memória RAM (Mixer)
        if hotkey_to_remove in self.sound_map:
            try:
                keyboard.remove_hotkey(hotkey_to_remove)
            except KeyError:
                pass
            del self.sound_map[hotkey_to_remove]

        # 2. Remove dos Dados de Salvamento (JSON)
        if hotkey_to_remove in self.saved_data:
            del self.saved_data[hotkey_to_remove]
            # Salva a alteração no disco imediatamente
            self.save_config()

        self.listbox.delete(index)

    def _on_key_press(self, event):
        modifiers = []
        if event.state & 4: modifiers.append("ctrl")
        if event.state & 1: modifiers.append("shift")
        if event.state & 131072 or event.state & 8: modifiers.append("alt")
        
        key = event.keysym.lower()
        mapping = {
            'return': 'enter', 'control_l': 'ctrl', 'control_r': 'ctrl',
            'alt_l': 'alt', 'alt_r': 'alt', 'shift_l': 'shift', 'shift_r': 'shift',
            'prior': 'page up', 'next': 'page down'
        }
        key = mapping.get(key, key)

        if key in ['ctrl', 'alt', 'shift']:
            full_hotkey = "+".join(modifiers)
        else:
            if modifiers:
                if key not in modifiers:
                    full_hotkey = "+".join(modifiers) + "+" + key
                else:
                    full_hotkey = "+".join(modifiers)
            else:
                full_hotkey = key

        self.hotkey_entry.delete(0, tk.END)
        self.hotkey_entry.insert(0, full_hotkey)
        return "break"

    def add_sound_dialog(self):
        hotkey = self.hotkey_entry.get().lower()
        if not hotkey:
            messagebox.showwarning("Atenção", "Defina um atalho primeiro!")
            return

        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
        if file_path:
            # Aqui chamamos o register com silent=False, pois o usuário acabou de adicionar manualmente
            self.register_sound(hotkey, file_path, silent=False)

    def register_sound(self, hotkey, file_path, silent=False):
        """
        Registra o som.
        Parametro 'silent': Se True, não mostra popups (usado ao carregar o app).
        """
        # Limpa registro anterior se houver (Overwrite)
        if hotkey in self.sound_map:
            try:
                keyboard.remove_hotkey(hotkey)
            except: pass

        try:
            sound_effect = pygame.mixer.Sound(file_path)
        except pygame.error as e:
            if not silent:
                messagebox.showerror("Erro", f"Falha no arquivo: {e}")
            return
        
        # Atualiza dicionários
        self.sound_map[hotkey] = sound_effect
        self.saved_data[hotkey] = file_path # Guarda o caminho string para o JSON
        
        # Atualiza UI
        filename = os.path.basename(file_path)
        display_text = f"[{hotkey}] -> {filename}"
        self.listbox.insert(tk.END, display_text)
        self.hotkey_entry.delete(0, tk.END)
        
        try:
            keyboard.add_hotkey(hotkey, lambda: self.play_sound(hotkey))
            
            # Salva no disco toda vez que um som novo é registrado com sucesso
            self.save_config()
            
            if not silent:
                messagebox.showinfo("Sucesso", f"Atalho '{hotkey}' salvo!")
                
        except Exception as e:
            if not silent:
                messagebox.showerror("Erro", f"Tecla inválida: {e}")

    def play_sound(self, hotkey):
        if hotkey in self.sound_map:
            print(f"Tocando: {hotkey}")
            self.sound_map[hotkey].play()

if __name__ == "__main__":
    try:
        import keyboard
        import pygame
    except ImportError:
        print("Instale: pip install keyboard pygame")
        exit()

    root = tk.Tk()
    app = SoundboardApp(root)
    root.mainloop()