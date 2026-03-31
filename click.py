import tkinter as tk
from pynput import mouse
import pygame
import threading
import queue

# --- KONFIGURACE ---
CLICK_SOUND_FILE = "click.wav"
SCROLL_SOUND_FILE = "scroll.wav"

# Barvy pro různé typy událostí
LEFT_CLICK_COLOR = "#FF5733"   # Červená pro levé tlačítko
RIGHT_CLICK_COLOR = "#3498DB"  # Modrá pro pravé tlačítko
SCROLL_COLOR = "#2ECC71"       # Zelená pro kolečko

TEXT_COLOR = "white"
DISPLAY_MS = 400  # Jak dlouho bublina zůstane (ms)

# Inicializace fronty a zvuku
msg_queue = queue.Queue()
pygame.mixer.init()

def play_sound(sound_file):
    try:
        pygame.mixer.Sound(sound_file).play()
    except:
        pass # Ignorovat, pokud soubor chybí

def create_bubble(x, y, text, color):
    """Vytvoří bublinu, která se sama zničí."""
    top = tk.Toplevel()
    top.overrideredirect(True)      # Bez okrajů
    top.attributes("-topmost", True) # Vždy navrchu
    # Na macOS může být potřeba: top.attributes("-alpha", 0.8)
    
    # Pozice (mírně posunutá od kurzoru, aby nepřekážela kliknutí)
    top.geometry(f"+{int(x+10)}+{int(y+10)}")
    
    lbl = tk.Label(top, text=text, bg=color, fg=TEXT_COLOR, 
                   font=("Arial", 10, "bold"), padx=6, pady=3)
    lbl.pack()
    
    # Klíč k úspěchu: Okno se samo zničí po uplynutí času
    top.after(DISPLAY_MS, top.destroy)

def check_queue(root):
    """Pravidelně kontroluje frontu, jestli někdo nekliknul."""
    try:
        while True:
            event_data = msg_queue.get_nowait()
            event_type = event_data['type']
            x = event_data['x']
            y = event_data['y']
            
            if event_type == 'left':
                create_bubble(x, y, "Click Left", LEFT_CLICK_COLOR)
                play_sound(CLICK_SOUND_FILE)
            elif event_type == 'right':
                create_bubble(x, y, "Click Right", RIGHT_CLICK_COLOR)
                play_sound(CLICK_SOUND_FILE)
            elif event_type == 'scroll':
                direction = event_data['direction']
                text = "↑ Scroll Up" if direction > 0 else "↓ Scroll Down"
                create_bubble(x, y, text, SCROLL_COLOR)
                play_sound(SCROLL_SOUND_FILE)
    except queue.Empty:
        pass
    # Zkontroluj znovu za 10ms
    root.after(10, lambda: check_queue(root))

def on_click(x, y, button, pressed):
    if pressed:
        # Rozlišení levého a pravého tlačítka
        if button == mouse.Button.left:
            msg_queue.put({'type': 'left', 'x': x, 'y': y})
        elif button == mouse.Button.right:
            msg_queue.put({'type': 'right', 'x': x, 'y': y})

def on_scroll(x, y, dx, dy):
    # dy > 0 znamená scroll nahoru, dy < 0 znamená scroll dolů
    msg_queue.put({'type': 'scroll', 'x': x, 'y': y, 'direction': dy})

# --- HLAVNÍ ČÁST PROGRAMU ---
root = tk.Tk()
root.withdraw() # Skryje hlavní okno, chceme jen bubliny

# Spuštění sledování myši v pozadí (Daemon=True zajistí vypnutí s programem)
listener = mouse.Listener(on_click=on_click, on_scroll=on_scroll)
listener.daemon = True
listener.start()

print("Sleduju myš... Pro ukončení zavři terminál nebo stiskni Ctrl+C.")
print("  - Levé tlačítko: červená bublina")
print("  - Pravé tlačítko: modrá bublina")
print("  - Kolečko myši: zelená bublina")

# Spuštění kontrolní smyčky pro frontu
check_queue(root)

# Spuštění hlavní grafické smyčky (teď vše poběží hladce)
try:
    root.mainloop()
except KeyboardInterrupt:
    print("\nUkončování...")