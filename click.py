import tkinter as tk
from pynput import mouse
import pygame
import threading
import queue

# --- KONFIGURACE ---
SOUND_FILE = "click.wav"
BUBBLE_COLOR = "#FF5733"
TEXT_COLOR = "white"
DISPLAY_MS = 400  # Jak dlouho bublina zůstane (ms)

# Inicializace fronty a zvuku
msg_queue = queue.Queue()
pygame.mixer.init()

def play_sound():
    try:
        pygame.mixer.Sound(SOUND_FILE).play()
    except:
        pass # Ignorovat, pokud soubor chybí

def create_bubble(x, y):
    """Vytvoří bublinu, která se sama zničí."""
    top = tk.Toplevel()
    top.overrideredirect(True)      # Bez okrajů
    top.attributes("-topmost", True) # Vždy navrchu
    # Na macOS může být potřeba: top.attributes("-alpha", 0.8)
    
    # Pozice (mírně posunutá od kurzoru, aby nepřekážela kliknutí)
    top.geometry(f"+{int(x+10)}+{int(y+10)}")
    
    lbl = tk.Label(top, text="Click!", bg=BUBBLE_COLOR, fg=TEXT_COLOR, 
                   font=("Arial", 10, "bold"), padx=6, pady=3)
    lbl.pack()
    
    # Klíč k úspěchu: Okno se samo zničí po uplynutí času
    top.after(DISPLAY_MS, top.destroy)

def check_queue(root):
    """Pravidelně kontroluje frontu, jestli někdo nekliknul."""
    try:
        while True:
            x, y = msg_queue.get_nowait()
            create_bubble(x, y)
            play_sound()
    except queue.Empty:
        pass
    # Zkontroluj znovu za 10ms
    root.after(10, lambda: check_queue(root))

def on_click(x, y, button, pressed):
    if pressed:
        # Pošleme souřadnice do fronty pro hlavní vlákno
        msg_queue.put((x, y))

# --- HLAVNÍ ČÁST PROGRAMU ---
root = tk.Tk()
root.withdraw() # Skryje hlavní okno, chceme jen bubliny

# Spuštění sledování myši v pozadí (Daemon=True zajistí vypnutí s programem)
listener = mouse.Listener(on_click=on_click)
listener.daemon = True
listener.start()

print("Sleduju myš... Pro ukončení zavři terminál nebo stiskni Ctrl+C.")

# Spuštění kontrolní smyčky pro frontu
check_queue(root)

# Spuštění hlavní grafické smyčky (teď vše poběží hladce)
try:
    root.mainloop()
except KeyboardInterrupt:
    print("\nUkončování...")