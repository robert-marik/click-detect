# Click Detect 🖱️

Jednoduchá Python aplikace pro vizuální a zvukovou indikaci událostí myši a klávesnice. Při událostech myši se zobrazí animovaná bublina s popisem akce a přehraje se zvukový efekt, stisky kláves se zobrazují v levém horním rohu.

## 🎯 Funkce

- **Rozlišení tlačítek**: Zobrazí červenou bublinu „Click Left" pro levé a modrou bublinu „Click Right" pro pravé tlačítko
- **Detekce scrollování**: Zobrazí zelenou bublinu „↑ Scroll Up" nebo „↓ Scroll Down" při otáčení kolečkem myši
- **Klávesové zobrazení v jednom okně**: V levém horním rohu se ve stejném panelu zobrazuje buď kombinace (`Ctrl+C`, `Ctrl+V`), nebo běžně psané znaky
- **Psaný text**: Při stisku kláves bez modifikátorů (včetně `Shift` pro `A`, `:`, `?` atd.) zobrazuje posledních 15 znaků
- **Automatické skrytí**: Pokud 5 sekund není stisk klávesy, panel se úplně skryje (nezůstane ani prázdné okno)
- **Zvukové efekty**: Přehraje `click.wav` při kliknutí nebo stisku klávesy a `scroll.wav` při scrollování (pokud jsou soubory dostupné)
- **Neblokující**: Bubliny se automaticky zavírají a nepřekáží v práci
- **Konfigurovatelné**: Barvy, čas zobrazení a zvukové soubory lze snadno upravit

## 📋 Požadavky

- Python 3.6 nebo novější
- Operační systém: Windows, macOS, Linux

## 🚀 Instalace

1. Naklonujte repozitář:
```bash
git clone https://github.com/robert-marik/click-detect.git
cd click-detect
```

2. Nainstalujte závislosti:
```bash
pip install -r requirements.txt
```

## 💻 Použití

Spusťte program příkazem:

```bash
python click.py
```

Program běží na pozadí a sleduje kliknutí myši i stisky kláves. Pro ukončení stiskněte `Ctrl+C` v terminálu.

## ⚙️ Konfigurace

V souboru `click.py` můžete upravit následující konstanty:

```python
CLICK_SOUND_FILE = "click.wav"    # Zvuk při kliknutí myší
SCROLL_SOUND_FILE = "scroll.wav"  # Zvuk při scrollování
KEY_SOUND_FILE = "click.wav"      # Krátké tuknutí při stisku klávesy

LEFT_CLICK_COLOR = "#FF5733"   # Barva bubliny pro levé tlačítko (červená)
RIGHT_CLICK_COLOR = "#3498DB"  # Barva bubliny pro pravé tlačítko (modrá)
SCROLL_COLOR = "#2ECC71"       # Barva bubliny pro scroll (zelená)

TEXT_COLOR = "white"           # Barva textu v bublinách
DISPLAY_MS = 400               # Jak dlouho bublina zůstane viditelná (ms)
MAX_TYPED_CHARS = 15           # Počet zobrazených znaků bez modifikátorů
```

## 🎨 Vlastní zvukové efekty

Aplikace očekává soubory `click.wav` a `scroll.wav` ve stejné složce jako `click.py`. Můžete použít jakékoliv WAV soubory nebo funkci zvuku úplně vypnout odstraněním příslušných souborů.

## 🛠️ Technické detaily

Aplikace využívá:
- **tkinter**: Pro vytváření grafických bublin
- **pynput**: Pro sledování událostí myši i klávesnice na úrovni systému
- **pygame**: Pro přehrávání zvukových efektů
- **threading & queue**: Pro bezpečnou komunikaci mezi vlákny

## 🐛 Řešení problémů

### Program nereaguje na kliknutí
- Zkontrolujte, zda máte nainstalované všechny závislosti
- Na některých systémech může být potřeba spustit s administrátorskými právy

### Zvuk se nepřehrává
- Ověřte, že soubory `click.wav` a `scroll.wav` existují ve stejné složce jako skript
- Zkontrolujte, že váš systém podporuje přehrávání WAV souborů

### Bubliny se nezobrazují správně na macOS
- Zkuste odkomentovat řádek s `top.attributes("-alpha", 0.8)` v kódu

## 📄 Licence

Tento projekt je licencován pod MIT licencí - viz soubor [LICENSE](LICENSE) pro detaily.

## 👤 Autor

Robert Mařík ([@robert-marik](https://github.com/robert-marik))

## 🤝 Přispívání

Příspěvky jsou vítány! Neváhejte otevřít issue nebo pull request.
