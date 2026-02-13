#!/bin/bash
# Renderizar español
quarto render

# Renderizar inglés
quarto render en/

# Copiar inglés a docs/en/
rm -rf docs/en/
cp -r en/_site/. docs/en/