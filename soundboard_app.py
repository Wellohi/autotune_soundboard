import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pygame
import keyboard
import os
import json
# Importação Avançada: Acesso direto ao wrapper de áudio SDL2 para listar dispositivos
# Isso não é documentado na página principal do Pygame, é um recurso de "power user".
from pygame import _sdl2 as sdl2_audio

CONFIG_FILE = "soundboard_config.json"

class SoundboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Soundboard - Roteamento Avançado")
        self.root.geometry("500x550") # Aumentei para caber o seletor

        # Inicializa o mixer padrão primeiro
        pygame.mixer.init()
        
        # Inicializa o módulo SDL2 para conseguirmos ler os nomes dos dispositivos
        sdl2_audio.get_audio_device_names(False) 

        self.sound_map = {}
        self.saved_data = {}
        
        # Variável para guardar o dispositivo de áudio escolhido
        self.current_device = tk.StringVar()

        self._setup_ui()
        self._setup_global_hotkeys()
        self.load_config()

    def _setup_ui(self):
        # --- ÁREA DE CONFIGURAÇÃO DE ÁUDIO ---
        # Cientistas de dados precisam garantir que o 'Sink' (Destino) dos dados está correto.
        audio_frame = tk.LabelFrame(self.root, text="Configuração de Saída de Áudio", padx=10, pady=10)
        audio_frame.pack(fill="x", padx=10, pady=5)
        
        lbl_device = tk.Label(audio_frame, text="Onde o som deve sair?\n(Selecione 'CABLE Input' para usar no mic)")
        lbl_device.pack(anchor="w")

        # Combobox para listar dispositivos
        self.device_combo = ttk.Combobox(audio_frame, textvariable=self.current_device, width=50)
        self.device_combo['values'] = self.get_output_devices()
        self.device_combo.pack(pady=5)
        
        # Botão para aplicar a mudança de dispositivo
        btn_apply = tk.Button(audio_frame, text="Mudar Dispositivo de Saída", command=self.change_audio_output, bg="#dddddd")
        btn_apply.pack(pady=5)

        # --- ÁREA DE ATALHOS (CÓDIGO ANTERIOR) ---
        control_frame = tk.Frame(self.root, pady=10)
        control_frame.pack(fill="x")

        tk.Label(control_frame, text="Atalho:").pack(side="left", padx=5)
        
        self.hotkey_entry = tk.Entry(control_frame, width=10, bg="#f0f0f0")
        self.hotkey_entry.pack(side="left", padx=5)
        self.hotkey_entry.bind("<Key>", self._on_key_press)

        btn_add = tk.Button(control_frame, text="Adicionar", command=self.add_sound_dialog, bg="#d9ffcc")
        btn_add.pack(side="left", padx=5)

        btn_remove = tk.Button(control_frame, text="Remover", command=self.remove_selected_sound, bg="#ffcccc")
        btn_remove.pack(side="left", padx=5)

        self.listbox = tk.Listbox(self.root, width=60, height=15)
        self.listbox.pack(pady=10, padx=10)

        info_text = (
            "1. Selecione 'CABLE Input' acima.\n"
            "2. No Windows, mantenha seu Fone como padrão.\n"
            "3. No Discord, use 'CABLE Output' como microfone."
        )
        lbl_info = tk.Label(self.root, text=info_text, fg="gray", justify="center")
        lbl_info.pack(side="bottom", pady=5)

    def get_output_devices(self):
        """Retorna uma lista de strings com os nomes das saídas de áudio."""
        try:
            # True = Capture (Microfones), False = Playback (Alto-falantes)
            return sdl2_audio.get_audio_device_names(False)
        except Exception as e:
            print(f"Erro ao listar dispositivos: {e}")
            return ["Padrão do Sistema"]

    def change_audio_output(self):
        """
        Reinicia o mixer do Pygame apontando para o dispositivo específico.
        Isso é um 'Hot Swap' (Troca a quente).
        """
        device_name = self.current_device.get()
        if not device_name:
            return

        print(f"Tentando mudar saída para: {device_name}")
        
        try:
            # Para mudar o dispositivo, precisamos fechar o mixer e reabrir
            pygame.mixer.quit()
            
            # Re-inicializa com o parâmetro 'devicename'
            # Isso força o Pygame a ignorar o padrão do Windows
            pygame.mixer.init(devicename=device_name)
            
            # ATENÇÃO: Ao fechar o mixer, todos os sons carregados na RAM são perdidos.
            # Precisamos recarregar tudo do disco.
            self.sound_map.clear() # Limpa referencias antigas
            self.load_config() # Recarrega do JSON
            
            messagebox.showinfo("Sucesso", f"Áudio roteado para:\n{device_name}\nSons recarregados!")
            
        except Exception as e:
            messagebox.showerror("Erro de Áudio", f"Falha ao mudar dispositivo: {e}\nVoltando ao padrão.")
            pygame.mixer.init()
            self.load_config()

    # --- (RESTO DO CÓDIGO PERMANECE IGUAL) ---
    def _setup_global_hotkeys(self):
        try:
            keyboard.add_hotkey('alt+p', self.stop_all_sounds)
        except Exception: pass

    def stop_all_sounds(self):
        pygame.mixer.stop()

    def load_config(self):
        self.listbox.delete(0, tk.END) # Limpa visual
        if not os.path.exists(CONFIG_FILE): return
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
            self.saved_data = data # Restaura o dicionário de paths
            for hotkey, file_path in data.items():
                if os.path.exists(file_path):
                    self.register_sound(hotkey, file_path, silent=True, save=False)
        except Exception as e:
            print(f"Erro load: {e}")

    def save_config(self):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.saved_data, f, indent=4)
        except Exception: pass

    def remove_selected_sound(self):
        selection = self.listbox.curselection()
        if not selection: return
        index = selection[0]
        hotkey = self.listbox.get(index).split(']')[0].replace('[', '')
        
        if hotkey in self.sound_map:
            try: keyboard.remove_hotkey(hotkey)
            except: pass
            del self.sound_map[hotkey]
        
        if hotkey in self.saved_data:
            del self.saved_data[hotkey]
            self.save_config()
            
        self.listbox.delete(index)

    def _on_key_press(self, event):
        modifiers = []
        if event.state & 4: modifiers.append("ctrl")
        if event.state & 1: modifiers.append("shift")
        if event.state & 131072 or event.state & 8: modifiers.append("alt")
        key = event.keysym.lower()
        mapping = {'return': 'enter', 'control_l': 'ctrl', 'control_r': 'ctrl', 'alt_l': 'alt', 'alt_r': 'alt', 'shift_l': 'shift', 'shift_r': 'shift'}
        key = mapping.get(key, key)
        if key in ['ctrl', 'alt', 'shift']: full_hotkey = "+".join(modifiers)
        else: full_hotkey = "+".join(modifiers) + "+" + key if modifiers and key not in modifiers else "+".join(modifiers) if not key else key
        self.hotkey_entry.delete(0, tk.END)
        self.hotkey_entry.insert(0, full_hotkey)
        return "break"

    def add_sound_dialog(self):
        hotkey = self.hotkey_entry.get().lower()
        if not hotkey: return
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
        if file_path: self.register_sound(hotkey, file_path, silent=False)

    def register_sound(self, hotkey, file_path, silent=False, save=True):
        if hotkey in self.sound_map:
            try: keyboard.remove_hotkey(hotkey)
            except: pass
        try:
            sound = pygame.mixer.Sound(file_path)
        except pygame.error as e:
            if not silent: messagebox.showerror("Erro", str(e))
            return
        
        self.sound_map[hotkey] = sound
        if save:
            self.saved_data[hotkey] = file_path
            self.save_config()
        
        filename = os.path.basename(file_path)
        self.listbox.insert(tk.END, f"[{hotkey}] -> {filename}")
        self.hotkey_entry.delete(0, tk.END)
        
        try: keyboard.add_hotkey(hotkey, lambda: self.play_sound(hotkey))
        except: pass

    def play_sound(self, hotkey):
        if hotkey in self.sound_map: self.sound_map[hotkey].play()

if __name__ == "__main__":
    try: import keyboard; import pygame; from pygame import _sdl2
    except ImportError: exit()
    root = tk.Tk()
    app = SoundboardApp(root)
    root.mainloop()