# pokus o jednoduchou vizualizci kliků.

import tkinter as tk
from pynput import mouse, keyboard
import pygame
import queue
import time
import os
from PIL import Image, ImageDraw, ImageFont, ImageTk, ImageColor

# --- KONFIGURACE ---
CLICK_SOUND_FILE = "click.wav"
SCROLL_SOUND_FILE = "scroll.wav"
KEY_SOUND_FILE = "presskey.wav"

# Barvy pro různé typy událostí
LEFT_CLICK_COLOR = "#FF5733"   # Červená pro levé tlačítko
RIGHT_CLICK_COLOR = "#3498DB"  # Modrá pro pravé tlačítko
SCROLL_COLOR = "#2ECC71"       # Zelená pro kolečko

TEXT_COLOR = "#FFFFFF"
DISPLAY_MS = 400  # Jak dlouho bublina zůstane (ms)
MAX_TYPED_CHARS = 15
OVERLAY_IDLE_SECONDS = 5.0
OVERLAY_BG_COLOR = "#FFD400"
OVERLAY_TEXT_COLOR = "black"
FONTSIZE = 64
FONTSIZE_CLICK = 16
FONTNAME = "Monaco"  # Modern monospace font
FONT_STYLE = "bold"

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

    # Vytvořit frame pro bubliny klávesy
    frame = tk.Frame(top, bg=OVERLAY_BG_COLOR)
    frame.pack(fill="both", expand=True)
    
    # Uložit frame do overlay_window pro pozdější přístup k UI prvkům
    top.bubble_frame = frame
    top.current_bubbles = []

    overlay_window = top


def show_overlay_text(text):
    if overlay_window is None:
        return
    
    # Vyčistit staré bubliny
    for widget in overlay_window.current_bubbles:
        widget.destroy()
    overlay_window.current_bubbles.clear()
    
    if not text:
        overlay_window.withdraw()
        return
    
    # Vytvořit bubliny pro každý řádek/obsah
    # Rozdělíme text na jednotlivé znaky/kombinace pro hezčí zobrazení
    pil_img = create_rounded_bubble_image(text, OVERLAY_BG_COLOR, OVERLAY_TEXT_COLOR, FONTSIZE, FONTNAME)
    photo = ImageTk.PhotoImage(pil_img)
    
    lbl = tk.Label(
        overlay_window.bubble_frame,
        image=photo,
        bg=OVERLAY_BG_COLOR,
        bd=0,
        highlightthickness=0
    )
    lbl.image = photo  # Udržet referenci
    lbl.pack(side="left", padx=14, pady=14)
    
    overlay_window.current_bubbles.append(lbl)
    overlay_window.deiconify()


def hide_overlay():
    global last_key_event_at
    if overlay_window is None:
        return
    
    # Vyčistit bubliny
    for widget in overlay_window.current_bubbles:
        widget.destroy()
    overlay_window.current_bubbles.clear()
    
    overlay_window.withdraw()
    # Reset historie znaků, aby se po skryti zobrazy jen nove znaky.
    typed_chars.clear()
    last_key_event_at = 0.0

def play_sound(sound_file):
    try:
        pygame.mixer.Sound(sound_file).play()
    except:
        pass # Ignorovat, pokud soubor chybí

def create_rounded_bubble_image(text, bg_color, fg_color, fontsize, fontname):
    """Vytvoří zakulacenou bublinu jako PIL Image."""
    # Konverze barev z hex/jmen na RGB
    try:
        bg_rgb = ImageColor.getrgb(bg_color)
    except:
        bg_rgb = (255, 212, 0)  # Fallback na žlutou
    
    try:
        fg_rgb = ImageColor.getrgb(fg_color)
    except:
        fg_rgb = (255, 255, 255)  # Fallback na bílou
    
    # Vytvořit dočasný obrázek pro měření textu
    temp_img = Image.new('RGBA', (1, 1))
    temp_draw = ImageDraw.Draw(temp_img)
    
    try:
        font = ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", fontsize)
    except:
        try:
            font = ImageFont.truetype(f"/System/Library/Fonts/Monaco.dfont", fontsize)
        except:
            font = ImageFont.load_default()
    
    # Měření textu - dostaneme přesný bounding box včetně ascendersů a descenderů
    bbox = temp_draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    bbox_top_offset = bbox[1]  # Offset horního okraje (může být negativní pro ascendery)
    
    # Rozměry bubliny s padding
    padding_x = 12
    padding_y = 10
    radius = 8
    
    bubble_width = text_width + padding_x * 2
    bubble_height = text_height + padding_y * 2
    
    # Vytvořit finální obrázek s průhledností
    img = Image.new('RGBA', (bubble_width, bubble_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Nakreslit zakulacenou bublinu - obdélník s zakulacenými rohy
    draw.rounded_rectangle(
        [(0, 0), (bubble_width - 1, bubble_height - 1)],
        radius=radius,
        fill=bg_rgb,
        outline=None
    )
    
    # Nakreslit text - vycentrovat vertikálně s ohledem na ascendery/descendery
    # bbox_top_offset korriguje odsazení tak, aby text fit správně do bubliny
    text_x = padding_x - bbox[0]
    text_y = padding_y - bbox_top_offset
    draw.text((text_x, text_y), text, font=font, fill=fg_rgb)
    
    return img

def create_bubble(x, y, text, color):
    """Vytvoří bublinu se zakulacenými rohy, která se sama zničí."""
    top = tk.Toplevel()
    top.overrideredirect(True)      # Bez okrajů
    top.attributes("-topmost", True) # Vždy navrchu
    
    # Vytvořit PIL obrázek se zakulacenými rohy
    pil_img = create_rounded_bubble_image(text, color, TEXT_COLOR, FONTSIZE_CLICK, FONTNAME)
    
    # Převést PIL Image na PhotoImage pro Tkinter
    photo = ImageTk.PhotoImage(pil_img)
    
    # Vytvořit label s obrázkem
    lbl = tk.Label(top, image=photo, bd=0, highlightthickness=0)
    lbl.image = photo  # Udržet referenci!
    lbl.pack()
    
    # Pozice (mírně posunutá od kurzoru, aby nepřekážela kliknutí)
    top.geometry(f"+{int(x+10)}+{int(y+10)}")
    
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