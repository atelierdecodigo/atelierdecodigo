"""
traducir_posts_simple.py
-------------------------
Traduce posts .qmd de español a inglés usando la API REST de Google Gemini.
Versión simplificada que solo requiere 'requests' (sin grpcio ni dependencias pesadas).

Uso:
    pip install requests  # probablemente ya lo tengas
    export GEMINI_API_KEY="AIza..."
    python traducir_posts_simple.py

Clave gratuita en: https://aistudio.google.com → "Get API key"
"""

import os
import time
import json
from pathlib import Path
import requests

# ── Configuración ──────────────────────────────────────────────────────────────
INPUT_DIR  = Path("posts")       # carpeta con los .qmd en español
OUTPUT_DIR = Path("en/posts")    # carpeta destino en inglés
DELAY_ENTRE_ARCHIVOS = 5         # segundos entre llamadas (plan gratuito: 15 rpm)
# ───────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a professional translator specializing in technical and data science content.
You will receive Quarto Markdown (.qmd) files written in Spanish.

Your task is to translate them to English following these strict rules:

1. YAML FRONT MATTER: Translate the VALUES but never the KEYS.
   - Translate: title, description, subtitle, any text values
   - Do NOT translate: categories names that are proper nouns or code terms (R, Python, ggplot2, etc.)
   - Keep the structure identical

2. CODE BLOCKS: Never translate anything inside ``` blocks or inline `code`.

3. MARKDOWN: Preserve all formatting — headers (#), bold (**), italics (*), links, images.
   - Translate link text but keep the URLs unchanged
   - Translate image alt text but keep the file paths unchanged

4. TECHNICAL TERMS: Keep R/Python package names, function names, and proper nouns in their original form.

5. OUTPUT: Return ONLY the translated file content, with no explanations or extra text."""


def traducir_archivo(api_key: str, contenido: str, nombre: str) -> str:
    """Envía el contenido a Gemini via API REST y devuelve la traducción."""
    print(f"  Traduciendo {nombre}...")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    prompt = f"{SYSTEM_PROMPT}\n\nTranslate this Quarto file from Spanish to English:\n\n{contenido}"
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, json=payload, headers=headers, timeout=60)
    response.raise_for_status()
    
    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def main():
    # Verificar API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: no encontré la variable GEMINI_API_KEY.")
        print("   Obtené tu key gratis en https://aistudio.google.com")
        print("   Luego exportala con: export GEMINI_API_KEY='AIza...'")
        return

    # Crear carpeta destino si no existe
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Obtener lista de archivos .qmd
    archivos = sorted(INPUT_DIR.glob("*.qmd"))
    if not archivos:
        print(f"❌ No encontré archivos .qmd en '{INPUT_DIR}/'")
        return

    print(f"📂 Encontré {len(archivos)} archivos en '{INPUT_DIR}/'")
    print(f"📁 Guardando traducciones en '{OUTPUT_DIR}/'\n")

    exitosos = []
    fallidos  = []

    for i, archivo in enumerate(archivos, 1):
        destino = OUTPUT_DIR / archivo.name

        # Saltar si ya existe
        if destino.exists():
            print(f"[{i}/{len(archivos)}] ⏭️  {archivo.name} ya existe, saltando.")
            continue

        print(f"[{i}/{len(archivos)}] 🔄 {archivo.name}")

        try:
            contenido = archivo.read_text(encoding="utf-8")
            traduccion = traducir_archivo(api_key, contenido, archivo.name)
            destino.write_text(traduccion, encoding="utf-8")
            print(f"  ✅ Guardado en {destino}")
            exitosos.append(archivo.name)

        except Exception as e:
            print(f"  ❌ Error: {e}")
            fallidos.append(archivo.name)

        # Pausa entre archivos
        if i < len(archivos):
            time.sleep(DELAY_ENTRE_ARCHIVOS)

    # Resumen final
    print(f"\n{'─'*50}")
    print(f"✅ Traducidos exitosamente: {len(exitosos)}")
    if fallidos:
        print(f"❌ Con errores: {len(fallidos)}")
        for f in fallidos:
            print(f"   - {f}")
    print("─"*50)
    print("Listo. Revisá los archivos antes de publicar.")


if __name__ == "__main__":
    main()
