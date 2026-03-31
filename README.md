# Click Detect 🖱️

Jednoduchá Python aplikace pro vizuální a zvukovou indikaci kliknutí myši. Při každém kliknutí se zobrazí animovaná bublina s textem "Click!" a přehraje se zvukový efekt.

## 🎯 Funkce

- **Vizuální feedback**: Zobrazí barevnou bublinu při každém kliknutí myši
- **Zvukový efekt**: Přehraje zvuk při každém kliknutí (pokud je dostupný soubor `click.wav`)
- **Neblokující**: Bubliny se automaticky zavírají a nepřekáží v práci
- **Konfigurovatelné**: Barvy, čas zobrazení a zvukový soubor lze snadno upravit

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

Program běží na pozadí a sleduje všechna kliknutí myši. Pro ukončení stiskněte `Ctrl+C` v terminálu.

## ⚙️ Konfigurace

V souboru `click.py` můžete upravit následující konstanty:

```python
SOUND_FILE = "click.wav"      # Cesta ke zvukovému souboru
BUBBLE_COLOR = "#FF5733"       # Barva bubliny (hex kód)
TEXT_COLOR = "white"           # Barva textu
DISPLAY_MS = 400               # Jak dlouho bublina zůstane viditelná (ms)
```

## 🎨 Vlastní zvukový efekt

Aplikace očekává soubor `click.wav` ve stejné složce jako `click.py`. Můžete použít jakýkoliv WAV soubor nebo funkci zvuku úplně vypnout odstraněním souboru.

## 🛠️ Technické detaily

Aplikace využívá:
- **tkinter**: Pro vytváření grafických bublin
- **pynput**: Pro sledování událostí myši na úrovni systému
- **pygame**: Pro přehrávání zvukových efektů
- **threading & queue**: Pro bezpečnou komunikaci mezi vlákny

## 🐛 Řešení problémů

### Program nereaguje na kliknutí
- Zkontrolujte, zda máte nainstalované všechny závislosti
- Na některých systémech může být potřeba spustit s administrátorskými právy

### Zvuk se nepřehrává
- Ověřte, že soubor `click.wav` existuje ve stejné složce jako skript
- Zkontrolujte, že váš systém podporuje přehrávání WAV souborů

### Bubliny se nezobrazují správně na macOS
- Zkuste odkomentovat řádek s `top.attributes("-alpha", 0.8)` v kódu

## 📄 Licence

Tento projekt je licencován pod MIT licencí - viz soubor [LICENSE](LICENSE) pro detaily.

## 👤 Autor

Robert Mařík ([@robert-marik](https://github.com/robert-marik))

## 🤝 Přispívání

Příspěvky jsou vítány! Neváhejte otevřít issue nebo pull request.
