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

# --- CONSTANTES DE ÁUDIO (PRO CONFIG) ---
# Definimos padrões de estúdio para garantir compatibilidade com VoiceMeeter/Discord
AUDIO_FREQ = 48000      # 48kHz (Padrão DVD/Discord). Evita distorção de resampling.
AUDIO_SIZE = -16        # 16-bit signed (Padrão CD).
AUDIO_CHANNELS = 2      # Stereo.
AUDIO_BUFFER = 2048     # Tamanho do Buffer. Aumente se ouvir "estalos" ou "picotes".

class SoundboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Soundboard - High Fidelity")
        self.root.geometry("500x550") 

        # --- INICIALIZAÇÃO DE ÁUDIO CORRIGIDA ---
        # Antes de iniciar, configuramos a "pré-inicialização" com os parâmetros de qualidade.
        # Isso força o Pygame a não usar os padrões antigos de baixa qualidade.
        try:
            pygame.mixer.pre_init(frequency=AUDIO_FREQ, size=AUDIO_SIZE, channels=AUDIO_CHANNELS, buffer=AUDIO_BUFFER)
            pygame.mixer.init()
            # Inicializa o módulo SDL2 para conseguirmos ler os nomes dos dispositivos
            sdl2_audio.get_audio_device_names(False) 
        except Exception as e:
            messagebox.showerror("Erro de Audio Driver", f"Não foi possível iniciar o driver de som:\n{e}")

        self.sound_map = {}
        self.saved_data = {}
        
        # Variável de Estado: Volume Mestre (Padrão 1.0 = 100%)
        # Guardamos isso para aplicar em novos sons que forem carregados futuramente.
        self.master_volume = 1.0
        
        # Variável para guardar o dispositivo de áudio escolhido
        self.current_device = tk.StringVar()

        self._setup_ui()
        self._setup_global_hotkeys()
        self.load_config()

    def _setup_ui(self):
        # --- ÁREA DE CONFIGURAÇÃO DE ÁUDIO ---
        # Cientistas de dados precisam garantir que o 'Sink' (Destino) dos dados está correto.
        audio_frame = tk.LabelFrame(self.root, text="Configuração de Áudio (Saída & Volume)", padx=10, pady=10)
        audio_frame.pack(fill="x", padx=10, pady=5)
        
        lbl_device = tk.Label(audio_frame, text="Dispositivo de Saída:")
        lbl_device.pack(anchor="w")

        # Combobox para listar dispositivos
        self.device_combo = ttk.Combobox(audio_frame, textvariable=self.current_device, width=50)
        self.device_combo['values'] = self.get_output_devices()
        self.device_combo.pack(pady=5)
        
        # Controle de Volume (Slider)
        # from_=0, to=100: Escala Humana
        # command=self.update_volume: Função chamada a cada movimento do mouse
        tk.Label(audio_frame, text="Volume Geral:").pack(anchor="w")
        self.vol_slider = tk.Scale(audio_frame, from_=0, to=100, orient="horizontal", command=self.update_volume)
        self.vol_slider.set(100) # Define valor inicial visual
        self.vol_slider.pack(fill="x")

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
            "Dica: Se o som estiver picotando, feche outros programas pesados.\n"
            "Configuração atual: 48kHz, 16bit, Stereo."
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

    def update_volume(self, val):
        """
        Função chamada automaticamente pelo Slider (tk.Scale).
        O Tkinter envia o valor atual como string (ex: "55").
        """
        # 1. Normalização de Dados (0-100 -> 0.0-1.0)
        # Transformamos a escala humana em escala de máquina.
        volume_float = int(val) / 100
        
        # 2. Atualiza o Estado Global
        self.master_volume = volume_float
        
        # 3. Atualiza todos os sons já carregados na memória
        # Iteramos sobre o dicionário de sons e aplicamos o novo volume imediatamente.
        for sound in self.sound_map.values():
            sound.set_volume(self.master_volume)

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
            
            # Re-inicializa com o parâmetro 'devicename' E OS PARÂMETROS DE QUALIDADE
            # Se não passarmos freq/size/buffer aqui de novo, ele pode resetar para qualidade baixa.
            pygame.mixer.init(
                frequency=AUDIO_FREQ,
                size=AUDIO_SIZE,
                channels=AUDIO_CHANNELS,
                buffer=AUDIO_BUFFER,
                devicename=device_name
            )
            
            # ATENÇÃO: Ao fechar o mixer, todos os sons carregados na RAM são perdidos.
            # Precisamos recarregar tudo do disco.
            self.sound_map.clear() # Limpa referencias antigas
            self.load_config() # Recarrega do JSON
            
            messagebox.showinfo("Sucesso", f"Áudio roteado para:\n{device_name}\nSons recarregados em Alta Fidelidade (48kHz)!")
            
        except Exception as e:
            messagebox.showerror("Erro de Áudio", f"Falha ao mudar dispositivo: {e}\nVoltando ao padrão.")
            # Tenta recuperar com as configs padrão
            pygame.mixer.init(frequency=AUDIO_FREQ, size=AUDIO_SIZE, buffer=AUDIO_BUFFER)
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
            
            # --- APLICAÇÃO DO VOLUME ---
            # Assim que o som nasce (é carregado), ele já recebe o volume configurado.
            sound.set_volume(self.master_volume)
            
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