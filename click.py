# pokus o jednoduchou vizualizci kliků.

import tkinter as tk
from pynput import mouse, keyboard
import pygame
import queue
import time
import os

# --- KONFIGURACE ---
CLICK_SOUND_FILE = "click.wav"
SCROLL_SOUND_FILE = "scroll.wav"
KEY_SOUND_FILE = "presskey.wav"

# Barvy pro různé typy událostí
LEFT_CLICK_COLOR = "#FF5733"   # Červená pro levé tlačítko
RIGHT_CLICK_COLOR = "#3498DB"  # Modrá pro pravé tlačítko
SCROLL_COLOR = "#2ECC71"       # Zelená pro kolečko

TEXT_COLOR = "white"
DISPLAY_MS = 400  # Jak dlouho bublina zůstane (ms)
MAX_TYPED_CHARS = 15
OVERLAY_IDLE_SECONDS = 5.0
OVERLAY_BG_COLOR = "#FFD400"
OVERLAY_TEXT_COLOR = "black"
FONTSIZE=20

# Inicializace fronty a zvuku ěšě+š3213
msg_queue = queue.Queue()
pygame.mixer.init()

pressed_modifiers = set()
pressed_modifier_keys = {}  # Trackuje konkreetni klice (shift_l, shift_r, ctrl_l, ctrl_r, ...)

typed_chars = []
overlay_window = None
overlay_text_var = None
last_key_event_at = 0.0


def is_modifier_key(key):
    return key in {
        keyboard.Key.ctrl,
        keyboard.Key.ctrl_l,
        keyboard.Key.ctrl_r,
        keyboard.Key.alt,
        keyboard.Key.alt_l,
        keyboard.Key.alt_r,
        keyboard.Key.shift,
        keyboard.Key.shift_l,
        keyboard.Key.shift_r,
        keyboard.Key.cmd,
        keyboard.Key.cmd_l,
        keyboard.Key.cmd_r,
    }


def modifier_name(key):
    if key in {keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r}:
        return "Ctrl"
    if key in {keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r}:
        return "Alt"
    if key in {keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r}:
        return "Shift"
    if key in {keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r}:
        return "Cmd"
    return None


def get_active_modifiers():
    """Vraci sadu aktivnich modifikatoru ve spravnem poradi."""
    modifiers = set()
    if any(pressed_modifier_keys.get(k) for k in [keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r]):
        modifiers.add("Ctrl")
    if any(pressed_modifier_keys.get(k) for k in [keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r]):
        modifiers.add("Alt")
    if any(pressed_modifier_keys.get(k) for k in [keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r]):
        modifiers.add("Shift")
    if any(pressed_modifier_keys.get(k) for k in [keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r]):
        modifiers.add("Cmd")
    return modifiers


def normalized_modifier_order(modifiers):
    order = ["Ctrl", "Alt", "Shift", "Cmd"]
    return [name for name in order if name in modifiers]


def plain_key_text(key):
    """Ziska tisknutelny znak z klavesu."""
    if isinstance(key, keyboard.KeyCode) and key.char is not None:
        return key.char if key.char.isprintable() else None
    
    special = {
        keyboard.Key.space: " ",
        keyboard.Key.enter: "[Enter]",
        keyboard.Key.tab: "[Tab]",
        keyboard.Key.esc: "[Esc]",
    }
    return special.get(key)


def combo_key_text(key):
    """Ziska jmeno klavesu pro kombinace (Ctrl+C, Alt+F4, atd.)."""
    if isinstance(key, keyboard.KeyCode) and key.char is not None:
        ch = key.char
        # Ctrl+<pismeno> vraci ridici kod (1-26), prevedeme na pismeno
        if len(ch) == 1 and 1 <= ord(ch) <= 26:
            ch = chr(ord('a') + ord(ch) - 1)
        # Zobrazime velke pismeno pro kombinace
        return ch.upper() if ch.isalpha() else ch if ch.isprintable() else None
    
    special = {
        keyboard.Key.space: "Space",
        keyboard.Key.enter: "Enter",
        keyboard.Key.tab: "Tab",
        keyboard.Key.delete: "Delete",
        keyboard.Key.up: "Up",
        keyboard.Key.down: "Down",
        keyboard.Key.left: "Left",
        keyboard.Key.right: "Right",
        keyboard.Key.esc: "Esc",
    }
    return special.get(key)


def create_overlay(root):
    global overlay_window, overlay_text_var

    top = tk.Toplevel(root)
    top.overrideredirect(True)
    top.attributes("-topmost", True)
    top.geometry("+10+10")
    top.configure(bg=OVERLAY_BG_COLOR)
    top.withdraw()

    overlay_text_var = tk.StringVar(value="")

    text_label = tk.Label(
        top,
        textvariable=overlay_text_var,
        bg=OVERLAY_BG_COLOR,
        fg=OVERLAY_TEXT_COLOR,
        font=("Arial", FONTSIZE, "bold"),
        anchor="w",
        justify="left",
        padx=8,
        pady=6,
    )
    text_label.pack(fill="x")

    overlay_window = top


def show_overlay_text(text):
    if overlay_window is None or overlay_text_var is None:
        return
    overlay_text_var.set(text)
    overlay_window.deiconify()


def hide_overlay():
    global last_key_event_at
    if overlay_window is None:
        return
    overlay_window.withdraw()
    # Reset historie znaků, aby se po skryti zobrazy jen nove znaky.
    typed_chars.clear()
    last_key_event_at = 0.0

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
                   font=("Arial", FONTSIZE, "bold"), padx=6, pady=3)
    lbl.pack()
    
    # Klíč k úspěchu: Okno se samo zničí po uplynutí času
    top.after(DISPLAY_MS, top.destroy)

def check_queue(root):
    """Pravidelně kontroluje frontu, jestli někdo nekliknul."""
    global last_key_event_at, typed_chars

    now = time.time()
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
            elif event_type == 'key_backspace':
                if typed_chars:
                    typed_chars.pop()
                show_overlay_text("".join(typed_chars))
                last_key_event_at = now
                play_sound(KEY_SOUND_FILE)
            elif event_type == 'key_combo':
                typed_chars.clear()
                show_overlay_text(event_data['text'])
                last_key_event_at = now
                play_sound(KEY_SOUND_FILE)
            elif event_type == 'key_plain':
                typed_chars.append(event_data['text'])
                del typed_chars[:-MAX_TYPED_CHARS]
                show_overlay_text("".join(typed_chars))
                last_key_event_at = now
                play_sound(KEY_SOUND_FILE)
    except queue.Empty:
        pass

    if last_key_event_at and (now - last_key_event_at) > OVERLAY_IDLE_SECONDS:
        hide_overlay()
        last_key_event_at = 0.0

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


def on_key_press(key):
    global typed_chars, last_key_event_at
    
    if is_modifier_key(key):
        pressed_modifier_keys[key] = True
        return

    # Backspace: vždy smazat poslední znak, bez ohledu na aktivní modifikátory.
    # (AltGr na CZ klávesnici se sleduje jako "Alt" a bez tohoto pravidla
    #  by uvíznutý AltGr zablokoval mazání.)
    if key == keyboard.Key.backspace:
        msg_queue.put({'type': 'key_backspace', 'x': 0, 'y': 0})
        for k in pressed_modifier_keys:
            pressed_modifier_keys[k] = False
        return

    key_text_for_combo = combo_key_text(key)
    if not key_text_for_combo:
        return

    modifiers = get_active_modifiers()
    shift_only = modifiers and all(mod == "Shift" for mod in modifiers)

    # Shift + znak je psani (napr. A, :, ?), ne klavesova zkratka.
    if modifiers and not shift_only:
        combo = "+".join(normalized_modifier_order(modifiers) + [key_text_for_combo])
        msg_queue.put({'type': 'key_combo', 'text': combo, 'x': 0, 'y': 0})
        for k in pressed_modifier_keys:
            pressed_modifier_keys[k] = False
        return

    plain_text = plain_key_text(key)
    if plain_text:
        msg_queue.put({'type': 'key_plain', 'text': plain_text, 'x': 0, 'y': 0})
    
    # Reset modifikatoru po zpracovani klavesy
    for k in pressed_modifier_keys:
        pressed_modifier_keys[k] = False


def on_key_release(key):
    if is_modifier_key(key):
        pressed_modifier_keys[key] = False

# --- HLAVNÍ ČÁST PROGRAMU ---
root = tk.Tk()
root.withdraw()

# Inicializuj pressed_modifier_keys pro vsechny varianty
for key_variant in [keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r,
                    keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r,
                    keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r,
                    keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r]:
    pressed_modifier_keys[key_variant] = False

create_overlay(root)

# Spuštění sledování myši v pozadí (Daemon=True zajistí vypnutí s programem)
listener = mouse.Listener(on_click=on_click, on_scroll=on_scroll)
listener.daemon = True
listener.start()

keyboard_listener = keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
keyboard_listener.daemon = True
keyboard_listener.start()

print("Sleduju myš a klávesy. Pro ukončení stiskni Ctrl+C v terminálu.")
if os.environ.get("WAYLAND_DISPLAY"):
    print("Pozn.: Ve Waylandu je globální odchyt kláves omezen compositor-em.")

# Spuštění kontrolní smyčky pro frontu
check_queue(root)

# Spuštění hlavní grafické smyčky (teď vše poběží hladce)
try:
    root.mainloop()
except KeyboardInterrupt:
    print("\nUkončování...")